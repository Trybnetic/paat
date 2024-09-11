"""
Wear Time Module
----------------

*paat.wear_time* provides functions to infer wear and non wear times from
raw acceleration signals.

"""
import logging
import os
import sys

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pandas as pd
from tensorflow.keras import models

from . import preprocessing, features


def _find_candidate_non_wear_segments_from_raw(acc_data, std_threshold, hz, min_segment_length=1, sliding_window=1, use_vmu=False):
    """
    Find segements within the raw acceleration data that can potentially be non-wear time (finding the candidates)

    Parameters
    ----------
    acc_data : np.array(samples, axes)
        numpy array with acceleration data (typically YXZ)
    std_threshold : int or float
        the standard deviation threshold in g
    hz : int
        sample frequency of the acceleration data (could be 32hz or 100hz for example)
    min_segment_length : int (optional)
        minimum length of the segment to be candidate for non-wear time (default 1 minutes, so any shorter segments will not be considered non-wear time)
    sliding_window : int (optional)
        sliding window in minutes that will go over the acceleration data to find candidate non-wear segments
    use_vmu : bool
        indicates whether the algorithm should runon vector magnitude data

    Returns
    -------
    nw_vector_final: array_like
        a numpy array with candidate non-wear time periods
    """

    # adjust the sliding window to match the samples per second (this is encoded in the samplign frequency)
    sliding_window *= hz * 60
    # adjust the minimum segment lenght to reflect minutes
    min_segment_length *= hz * 60

    # define new non wear time vector that we initiale to all 1s, so we only have the change when we have non wear time as it is encoded as 0
    nw_vector = np.ones((len(acc_data), 1), dtype=np.uint8)
    nw_vector_final = np.ones((len(acc_data), 1), dtype=np.uint8)

    # loop over slices of the data
    for ii in range(0, len(acc_data), sliding_window):

        # slice the data
        data = acc_data[ii:ii + sliding_window]

        # calculate VMU if set to true
        if use_vmu:
            # calculate the VMU of XYZ
            data = features.calculate_vector_magnitude(data)

        # calculate the standard deviation of each column (YXZ)
        std = np.std(data, axis=0)

        # check if all of the standard deviations are below the standard deviation threshold
        if np.all(std <= std_threshold):

            # add the non-wear time encoding to the non-wear-vector for the correct time slices
            nw_vector[ii:ii + sliding_window] = 0

    # find all indexes of the numpy array that have been labeled non-wear time
    non_wear_indexes = np.where(nw_vector == 0)[0]

    # find the min and max of those ranges, and increase incrementally to find the edges of the non-wear time
    for row in _find_consecutive_index_ranges(non_wear_indexes):

        # check if not empty
        if row.size != 0:

            # define the start and end of the index range
            start_slice, end_slice = np.min(row), np.max(row)

            # backwards search to find the edge of non-wear time vector
            start_slice = _backward_search_non_wear_time(data=acc_data, start_slice=start_slice, end_slice=end_slice, std_max=std_threshold, hz=hz)
            # forward search to find the edge of non-wear time vector
            end_slice = _forward_search_non_wear_time(data=acc_data, start_slice=start_slice, end_slice=end_slice, std_max=std_threshold, hz=hz)

            # calculate the length of the slice (or segment)
            length_slice = end_slice - start_slice

            # minimum length of the non-wear time
            if length_slice >= min_segment_length:

                # update numpy array by setting the start and end of the slice to zero (this is a non-wear candidate)
                nw_vector_final[start_slice:end_slice] = 0

    # return non wear vector with 0= non-wear and 1 = wear
    return nw_vector_final


def _find_consecutive_index_ranges(vector, increment=1):
    """
    Find ranges of consequetive indexes in numpy array

    Parameters
    ----------
    vector: numpy vector
        numpy vector of integer values
    increment: int (optional)
        difference between two values (typically 1)

    Returns
    -------
    indexes: list
        list of ranges, for instance [1,2,3,4],[8,9,10], [44]
    """

    return np.split(vector, np.where(np.diff(vector) != increment)[0] + 1)


def _forward_search_non_wear_time(data, start_slice, end_slice, std_max, hz, time_step=60):
    """
    Increase the end_slice to obtain more non_wear_time (used when non-wear range has been found but due to window size, the actual non-wear time can be slightly larger)

    Parameters
    ----------
    data: numpy array of time x 3 axis
        raw log data
    start_slice: int
        start of known non-wear time range
    end_slice: int
        end of known non-wear time range
    std_max: int or float
        the standard deviation threshold in g
    hz : int
        sample frequency of the data (necessary when working with indexes)
    time_step: int (optional)
        value to add (or subtract in the backwards search) to find more non-wear time

    Returns
    -------
    end_slice: int
        index of the end of the non-wear time period
    """

    # adjust time step on number of samples per time step window
    time_step *= hz

    # define the end of the range
    end_of_data = len(data)

    # Do-while loop
    while True:

        # define temporary end_slice variable with increase by step
        temp_end_slice = end_slice + time_step

        # check condition range still contains non-wear time
        if temp_end_slice <= end_of_data and np.all(np.std(data[start_slice:temp_end_slice], axis=0) <= std_max):

            # update the end_slice with the temp end slice value
            end_slice = temp_end_slice

        else:
            # here we have found that the additional time we added is not non-wear time anymore, stop and break from the loop by returning the updated slice
            return end_slice


def _backward_search_non_wear_time(data, start_slice, end_slice, std_max, hz, time_step=60):
    """
    Decrease the start_slice to obtain more non_wear_time (used when non-wear range has been found but the actual non-wear time can be slightly larger, so here we try to find the boundaries)

    Parameters
    ----------
    data: numpy array of time x 3 axis
        raw log data
    start_slice: int
        start of known non-wear time range
    end_slice: int
        end of known non-wear time range
    std_max: int or float
        the standard deviation threshold in g
    hz : int
        sample frequency of the data (necessary when working with indexes)
    time_step: int (optional)
        value to add (or subtract in the backwards search) to find more non-wear time

    Returns
    -------
    start_slice: int
        index of the start of the non-wear time period
    """

    # adjust time step on number of samples per time step window
    time_step *= hz

    # Do-while loop
    while True:

        # define temporary end_slice variable with increase by step
        temp_start_slice = start_slice - time_step

        # logging.debug('Decreasing temp_start_slice to: {}'.format(temp_start_slice))

        # check condition range still contains non-wear time
        if temp_start_slice >= 0 and np.all(np.std(data[temp_start_slice:end_slice], axis=0) <= std_max):

            # update the start slice with the new temp value
            start_slice = temp_start_slice

        else:
            # here we have found that the additional time we added is not non-wear time anymore, stop and break from the loop by returning the updated slice
            return start_slice


def _group_episodes(episodes, distance_in_min=3, correction=3, hz=100, training=False):
    """
    Group episodes that are very close together

    Parameters
    -----------
    episodes : pd.DataFrame()
        dataframe with episodes that need to be grouped
    distance_in_min : int
        maximum distance two episodes can be apart and need to be grouped together
    correction : int
        due to changing from 100hz to 32hz we need to allow for a small correction to capture full minutes
    hz : int
        sample frequency of the data (necessary when working with indexes)

    Returns
    -------
    grouped_episodes: pd.DataFrame()
        dataframe with grouped episodes
    """

    # check if there is only 1 episode in the episodes dataframe, if so, we need not to do anything since we cannot merge episodes if we only have 1
    if episodes.empty or len(episodes) == 1:
        # transpose back and return
        return episodes.T

    # create a new dataframe that will contain the grouped rows
    grouped_episodes = pd.DataFrame()

    # get all current values from the first row
    current_start = episodes.iloc[0]['start']
    current_start_index = episodes.iloc[0]['start_index']
    current_stop = episodes.iloc[0]['stop']
    current_stop_index = episodes.iloc[0]['stop_index']
    current_label = None if not training else episodes.iloc[0]['label']
    current_counter = episodes.iloc[0]['counter']

    # loop over each next row (note that we skip the first row)
    for _, row in episodes.iloc[1:].iterrows():

        # define all next values
        next_start = row.loc['start']
        next_start_index = row.loc['start_index']
        next_stop = row.loc['stop']
        next_stop_index = row.loc['stop_index']
        next_label = None if not training else row.loc['label']
        next_counter = row.loc['counter']

        # check if there are 'distance_in_min' minutes apart from current and next ( + correction for some adjustment)
        if next_start_index - current_stop_index <= hz * 60 * distance_in_min + correction:

            # here the two episodes are close to eachother, we update the values and continue the next row to see if we can group more. If it's the last row, we need to add it to the dataframe
            current_stop_index = next_stop_index
            current_stop = next_stop

            # check if row is the last row
            if next_counter == episodes.iloc[-1]['counter']:

                # create the counter label
                counter_label = f'{current_counter}-{next_counter}'

                # save to new dataframe
                grouped_episodes[counter_label] = pd.Series({'counter': counter_label,
                                                             'start_index': current_start_index,
                                                             'start': current_start,
                                                             'stop_index': current_stop_index,
                                                             'stop': current_stop,
                                                             'label': None if not training else current_label})
        else:

            # create the counter label
            counter_label = current_counter if (next_counter - current_counter == 1) else f'{current_counter}-{next_counter - 1}'

            # save to new dataframe
            grouped_episodes[counter_label] = pd.Series({'counter': counter_label,
                                                         'start_index': current_start_index,
                                                         'start': current_start,
                                                         'stop_index': current_stop_index,
                                                         'stop': current_stop,
                                                         'label': None if not training else current_label})

            # update tracker variables
            current_start = next_start
            current_start_index = next_start_index
            current_stop = next_stop
            current_stop_index = next_stop_index
            current_label = next_label
            current_counter = next_counter

            # check if last row then also include by itself
            if next_counter == episodes.iloc[-1]['counter']:

                # save to new dataframe
                grouped_episodes[next_counter] = pd.Series({'counter': next_counter,
                                                            'start_index': current_start_index,
                                                            'start': current_start,
                                                            'stop_index': current_stop_index,
                                                            'stop': current_stop,
                                                            'label': None if not training else current_label})

    return grouped_episodes


def detect_non_wear_time_syed2021(data, sample_freq, cnn_model_file=None, std_threshold=0.004, distance_in_min=5, episode_window_sec=7, edge_true_or_false=True,
                                  start_stop_label_decision='and', min_segment_length=1, sliding_window=1, verbose=False):
    """
    Infer non-wear time from raw 100Hz triaxial data based on the method proposed by Syed et al. (2021). 
    Data at different sample frequencies will be resampled to 100hz.

    The steps are described in the paper but are summarized here too:

    Detect candidate non-wear episodes:
        Perform a forward pass through the raw acceleration signal and calculate the SD for each 1-minute interval and for each individual axis.
        If the standard deviation is <= 0.004 g for all axes, record this 1-minute interval as a candidate non-wear interval. After all 1-minute
        intervals have been processed, merge consecutive 1-minute intervals into candidate non-wear episodes and record their start and stop timestamps.

    Merge bordering candidate non-wear episodes:
        Merge candidate non-wear episodes that are no more than 5 minutes apart and record their new start and stop timestamps. This step is required
        to capture artificial movement that would typically break up two or more candidate non-wear episodes in close proximity.

    Detect the edges of candidate non-wear episodes:
        Perform a backward pass with a 1-second step size through the acceleration data from the start timestamp of a candidate non-wear episode and
        calculate the SD for each individual axis. The same is applied for the stop timestamps with a forward pass and a step size of 1 second.
        If the standard deviation of all axes is  <= 0.004 g, include the 1-second interval into the candidate non-wear episode and record the new
        start or stop timestamp. Repeat until the standard deviation of the 1-second interval does not satisfy <= 0.004 g. As a result, the resolution
        of the edges is now recorded on a 1-second resolution.

    Classifying the start and stop windows:
        For each candidate non-wear episode, extract the start and stop segment with a window length of 3 seconds to create input features
        for the CNN classification model. For example, if a candidate non-wear episode has a start timestamp of tstart a feature matrix is
        created as (tstart – w  , tstart) x 3 axes with w = 3 seconds, resulting in an input feature with dimensions (300 x 3) for 100Hz data.
        If both (i.e., logical ‘AND’) start and stop features are classified (through the CNN model) as non-wear time, the candidate non-wear
        episode can be considered true non-wear time. If tstart is at t = 0, or tend is at the end of the acceleration data—meaning that
        those candidate non-wear episodes do not have a preceding or following window to extract features from—classify the start or stop
        as non-wear time by default.

    References
    ----------

    Syed, S., Morseth, B., Hopstock, L. A., & Horsch, A. (2021). A novel algorithm to detect non-wear time from raw 
    accelerometer data using deep convolutional neural networks. *Scientific Reports*, 11(1), 8832. https://doi.org/10.1038/s41598-021-87757-z

    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    sample_freq : int
        sample frequency of the data. The CNN model was trained for 100Hz of data. If the data is at a different sampling frequency it will be resampled to 100Hz
    cnn_model_file: os.path (optional)
        file location of the trained CNN model. On default, the corresponding pretrained model is used.
    std_threshold: float (optional)
        standard deviation threshold to find candidate non-wear episodes. Default 0.004 g
    distance_in_min: int (optional)
        causes two nearby candidate non-wear episodes not more than 'distance_in_min' apart to be grouped/merged together. This results in capturing artificial movement
        that would otherwise break up a longer candidate non-wear time. Defaults to 5 minutes.
    episode_window_sec: int (optional)
        length of the window to extract features from the start or the end of a candidate non-wear episode. If a non-wear episodes starts at time t, then a feature
        will be extracted from the raw data t-'episode_window_sec' to t. The same happens at the end of a candidate non-wear episode. So t-end untill t-end + 'episode_window_sec'
        Default to 7 seconds. Also note that a different value will need a different trained CNN model.
    edge_true_or_false: Bool (optional)
        default classification if a candidate non-wear episode starts at the start of the acceleration data, so at t=0, or ends at the end of the acceleration data.
        In such cases, we can't obtain the feature at t-'episode_window_sec' since there is no data before t=0. In these cases, the start or stop of the candidate non-wear
        episode will be defaulted to True (non-wear time) or False (wear-time). Default value is True
    start_stop_label_decision: string ('or','and') (optional)
        Logical operator OR or AND to determine if a candidate non-wear episode should be considered non-wear time if only one side, either the start or the stop parts, is
        inferred as non-wear time, or if both sides need to be inferred as non-wear time for the candidate non-wear time to be considered true non-wear time. Default to AND, meaning
        that both the start and the stop parts of the candidate non-wear time need to be inferred as non-wear time to allow the candidate non-wear time to be true non-wear time.
        In all other cases, the candidate non-wear time is then wear-time.
    min_segment_length: int (optional)
        minimum length of the segment to be candidate for non-wear time
    sliding_window: int (optional)
        sliding window in minutes that will go over the acceleration data to find candidate non-wear segments
    verbose: Bool (optional)
        set to True if debug messages should be printed to the console and log file. Default False.

    Returns
    -------
    nw_vector: np.array(n_samples,)
        a numpy array indicating whether the values of the acceleration data are non-wear time

    Notes
    -----
    -    If the data is not 100hz, then it will be resampled to 100hz. However, how the inference of non-wear time is affected by this has not been investigated.
    -    CNN models were trained with a hip worn accelerometer.
    """

    raw_acc = data[["X", "Y", "Z"]].values

    # use one of the default models if no model file is given
    if cnn_model_file is None:
        cnn_model_file = os.path.join(os.path.pardir, os.path.dirname(__file__), 'models', f'cnn_v2_{str(episode_window_sec)}.h5')

    # check if data is triaxial
    if raw_acc.shape[1] != 3:
        logging.error('Acceleration data should be triaxial/3 axes. Number of axes found is %s', raw_acc.shape[1])
        sys.exit()

    # check if data needs to be resampled to 100hz
    if sample_freq != 100:
        logging.info('Sampling frequency of the data is %s Hz, should be 100Hz, starting resampling....', sample_freq)
        # call resampling function
        raw_acc = preprocessing.resample_acceleration(data=raw_acc, from_hz=sample_freq, to_hz=100, verbose=verbose)
        logging.info('Data resampled to 100hz')
        # set sampling frequency to 100hz
        sample_freq = 100

    # create new non-wear vector that is prepopulated with wear-time encoding. This way we only have to record the non-wear time
    nw_vector = np.zeros(raw_acc.shape[0], dtype=bool)

    # get candidate non-wear episodes (note that these are on a minute resolution). Also note that it returns wear time as 1 and non-wear time as 0
    nw_episodes = _find_candidate_non_wear_segments_from_raw(acc_data=raw_acc, std_threshold=std_threshold,
                                                             min_segment_length=min_segment_length,
                                                             sliding_window=sliding_window, hz=sample_freq)

    # find all indexes of the numpy array that have been labeled non-wear time
    nw_indexes = np.where(nw_episodes == 0)[0]
    # find consecutive ranges
    non_wear_segments = _find_consecutive_index_ranges(nw_indexes)
    # empty dictionary where we can store the start and stop times
    dic_segments = {}

    # check if segments are found
    if len(non_wear_segments[0]) > 0:

        # find start and stop times (the indexes of the edges and find corresponding time)
        for ii, row in enumerate(non_wear_segments):

            # find start and stop
            start, stop = np.min(row), np.max(row)

            # add the start and stop times to the dictionary
            # note that start and stop timestamps are not given.
            dic_segments[ii] = {'counter': ii, 'start': start, 'start_index': start, 'stop': stop, 'stop_index': stop}

    # create dataframe from segments
    episodes = pd.DataFrame.from_dict(dic_segments)

    # Merge episodes that are close to each other
    grouped_episodes = _group_episodes(episodes=episodes.T, distance_in_min=distance_in_min, correction=3, hz=sample_freq, training=False).T

    # load CNN model
    cnn_model = models.load_model(cnn_model_file)

    # For each episode, extend the edges, create features and infer label
    for _, row in grouped_episodes.iterrows():

        start_index = int(row.loc['start_index'])
        stop_index = int(row.loc['stop_index'])

        if verbose:
            logging.debug('Processing episode start_index: %s, stop_index: %s', start_index, stop_index)

        # forward search to extend stop index
        stop_index = _forward_search_episode(raw_acc, stop_index, hz=sample_freq, max_search_min=5, std_threshold=std_threshold, verbose=verbose)
        # backwar search to extend start index
        start_index = _backward_search_episode(raw_acc, start_index, hz=sample_freq, max_search_min=5, std_threshold=std_threshold, verbose=verbose)

        # get start episode
        start_episode = raw_acc[start_index - (episode_window_sec * sample_freq): start_index]
        # get stop episode
        stop_episode = raw_acc[stop_index: stop_index + (episode_window_sec * sample_freq)]

        # default label for start and stop combined. The first False will turn into True if the start of the episode is inferred as non-wear time. The same happens to the
        # second False when the end is inferred as non-weaer time
        start_stop_label = [False, False]

        # Start episode
        if start_episode.shape[0] == episode_window_sec * sample_freq:

            # reshape into num feature x time x axes
            start_episode = start_episode.reshape(1, start_episode.shape[0], start_episode.shape[1])

            # get binary class from model
            start_label = (cnn_model.predict(start_episode, verbose=verbose) > 0.5).astype("int32")

            # if the start label is 1, this means that it is wear time, and we set the first start_stop_label to 1
            if start_label == 1:
                start_stop_label[0] = True

        else:
            # there is an episode right at the start of the data, since we cannot obtain a full epsisode_window_sec array
            # here we say that True for nw-time and False for wear time
            start_stop_label[0] = edge_true_or_false

        # Stop episode
        if stop_episode.shape[0] == episode_window_sec * sample_freq:

            # reshape into num feature x time x axes
            stop_episode = stop_episode.reshape(1, stop_episode.shape[0], stop_episode.shape[1])

            # get binary class from model
            stop_label = (cnn_model.predict(stop_episode, verbose=verbose) > 0.5).astype("int32")

            # if the start label is 1, this means that it is wear time, and we set the first start_stop_label to 1
            if stop_label == 1:
                start_stop_label[1] = True
        else:
            # there is an episode right at the END of the data, since we cannot obtain a full epsisode_window_sec array
            # here we say that True for nw-time and False for wear time
            start_stop_label[1] = edge_true_or_false

        # check the start_stop_label.
        if start_stop_label_decision == 'or':
            # use logical OR to determine if episode is true non-wear time
            if any(start_stop_label):
                # true non-wear time, record start and stop in nw-vector
                nw_vector[start_index:stop_index] = True
                # verbose
                if verbose:
                    logging.info('Found non-wear time: start_index: %s, Stop_index: %s', start_index, stop_index)

        elif start_stop_label_decision == 'and':

            # use logical and to determine if episode is true non-wear time
            if all(start_stop_label):
                # true non-wear time, record start and stop in nw-vector
                nw_vector[start_index:stop_index] = True
                # verbose
                if verbose:
                    logging.info('Found non-wear time: start_index: %s, Stop_index: %s', start_index, stop_index)

        else:
            logging.error('Start/Stop decision unknown, can only use or/and, given: %s', start_stop_label_decision)
            sys.exit()

    return nw_vector


def detect_non_wear_time_hees2011(data, sample_freq, min_non_wear_time_window=60, window_overlap=15, std_mg_threshold=3.0, std_min_num_axes=2,
                                  value_range_mg_threshold=50.0, value_range_min_num_axes=2):
    """
    Estimation of non-wear time periods based on Van Hees et al. (2011, 2013)

    Accelerometer non-wear time was estimated on the basis of the standard deviation and the value range of each accelerometer axis, calculated for consecutive blocks of 30 minutes.
    A block was classified as non-wear time if the standard deviation was less than 3.0 mg (1 mg = 0.00981 m·s−2) for at least two out of the three axes or if the value range, for
    at least two out of three axes, was less than 50 mg.

    Important to note that the default encoding for this function of non-wear time = 0, and that of wear time is 1.


    References
    ----------

    Van Hees, V. T., Renström, F., Wright, A., Gradmark, A., Catt, M., Chen, K. Y., 
    Löf, M., Bluck, L., Pomeroy, J., Wareham, N. J., Ekelund, U., Brage, S., & Franks, 
    P. W. (2011). Estimation of Daily Energy Expenditure in Pregnant and Non-Pregnant 
    Women Using a Wrist-Worn Tri-Axial Accelerometer. *PLOS ONE*, 6(7), 7. 
    https://doi.org/10.1371/journal.pone.0022922

    Hees, V. T. van, Gorzelniak, L., León, E. C. D., Eder, M., Pias, M., Taherian, S., 
    Ekelund, U., Renström, F., Franks, P. W., Horsch, A., & Brage, S. (2013). 
    Separating Movement and Gravity Components in an Acceleration Signal and 
    Implications for the Assessment of Human Daily Physical Activity. *PLOS ONE*, 
    8(4), e61691. https://doi.org/10.1371/journal.pone.0061691

    Parameters
    ----------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    sample_freq : int
        sample frequency in hertz. Indicates the number of samples per 1 second. Default to 100 for 100hz. The sample frequency is necessary to
        know how many samples there are in a specific window. So let's say we have a window of 15 minutes, then there are hz * 60 * 15 samples
    min_non_wear_time_window: int (optional)
        minimum window length in minutes to be classified as non-wear time
    window_overlap: int (optional)
        basically the sliding window that progresses over the acceleration data. Defaults to 15 minutes.
    std_mg_threshold: float (optional)
        standard deviation threshold in mg. Acceleration axes values below or equal this threshold can be considered non-wear time. Defaults to 3.0g.
        Note that within the code we convert mg to g.
    std_min_num_axes: int (optional)
        minimum numer of axes used to check if acceleration values are below the std_mg_threshold value. Defaults to 2 axes; meaning that at least 2
        axes need to have values below a threshold value to be considered non wear time
    value_range_mg_threshold: float (optional)
        value range threshold value in mg. If the range of values within a window is below this threshold (meaning that there is very little change
        in acceleration over time) then this can be considered non wear time. Default to 50 mg. Note that within the code we convert mg to g
    value_range_min_num_axes: int (optional)
        minimum numer of axes used to check if acceleration values range are below the value_range_mg_threshold value. Defaults to 2 axes; meaning that at least 2 axes need to have a value range below a threshold value to be considered non wear time

    Returns
    -------
    nw_vector: np.array(n_samples,)
        a numpy array indicating whether the values of the acceleration data are non-wear time
    """

    raw_acc = data[["X", "Y", "Z"]].values

    # number of data samples in 1 minute
    num_samples_per_min = sample_freq * 60

    # define the correct number of samples for the window and window overlap
    min_non_wear_time_window *= num_samples_per_min
    window_overlap *= num_samples_per_min

    # convert the standard deviation threshold from mg to g
    std_mg_threshold /= 1000
    # convert the value range threshold from mg to g
    value_range_mg_threshold /= 1000

    # new array to record non-wear time. The default behavior is 0 = non-wear time, and 1 = wear time. Since we create a new array filled with wear time encoding, we only have to
    # deal with non-wear time, since everything else is already set as wear-time.
    nw_vector = np.zeros(raw_acc.shape[0], dtype=bool)

    # loop over the data, start from the beginning with a step size of window overlap
    for ii in range(0, len(raw_acc), window_overlap):

        # define the start of the sequence
        start = ii
        # define the end of the sequence
        end = ii + min_non_wear_time_window

        # slice the data from start to end
        subset_data = raw_acc[start:end]

        # check if the data sequence has been exhausted, meaning that there are no full windows left in the data sequence (this happens at the end of the sequence)
        # comment out if you want to use all the data
        if len(subset_data) < min_non_wear_time_window:
            break

        # calculate the standard deviation of each column (YXZ)
        std = np.std(subset_data, axis=0)

        # check if the standard deviation is below the threshold, and if the number of axes the standard deviation is below equals the std_min_num_axes threshold
        if (std < std_mg_threshold).sum() >= std_min_num_axes:

            # at least 'std_min_num_axes' are below the standard deviation threshold of 'std_min_num_axes', now set this subset of the data to the non-wear time encoding.
            # Note that the full 'new_wear_vector' is pre-populated with the wear time encoding, so we only have to set the non-wear time.
            nw_vector[start:end] = True

        # calculate the value range (difference between the min and max) (here the point-to-point numpy method is used) for each column
        value_range = np.ptp(subset_data, axis=0)

        # check if the value range, for at least 'value_range_min_num_axes' (e.g. 2) out of three axes, was less than 'value_range_mg_threshold' (e.g. 50) mg
        if (value_range < value_range_mg_threshold).sum() >= value_range_min_num_axes:

            # set the non wear vector to non-wear time for the start to end slice of the data
            nw_vector[start:end] = True

    return nw_vector


def detect_non_wear_time_naive(data, sample_freq, std_threshold, min_interval, use_vmu=False, min_segment_length=1, sliding_window=1):
    """
        Calculate non-wear time from raw acceleration data by finding intervals in which
        the acceleration standard deviation is below a std_threshold value

        Parameters
        ----------
        data : DataFrame
            a DataFrame containg the raw acceleration data
        sample_freq : int
            sample frequency of the data
        std_threshold: int or float
            the standard deviation threshold in g
        min_interval: int or float
            minimal interval to consider period as non-wear time
        use_vmu: bool
            indicates whether the algorithm should runon vector magnitude data
        min_segment_length: int (optional)
            minimum length of the segment to be candidate for non-wear time (default 1 minutes, so any shorter segments will not be considered non-wear time)
        sliding_window: int (optional)
            sliding window in minutes that will go over the acceleration data to find candidate non-wear segments

        Returns
        -------
        nw_vector: np.array(n_samples,)
            a numpy array indicating whether the values of the acceleration data are non-wear time
    """

    raw_acc = data[["X", "Y", "Z"]].values

    # make sure hz is int
    sample_freq = int(sample_freq)

    # create an new non-wear vector that we propoulate with wear-time encoding. This way we only have to update the vector with non-wear time
    nw_vector = np.zeros(raw_acc.shape[0], dtype=bool)

    """
        FIND CANDIDATE NON-WEAR SEGMENTS ACTIGRAPH ACCELERATION DATA
    """

    # get candidate non-wear episodes (note that these are on a minute resolution)
    nw_episodes = _find_candidate_non_wear_segments_from_raw(acc_data=raw_acc, std_threshold=std_threshold, min_segment_length=min_segment_length, sliding_window=sliding_window, hz=sample_freq, use_vmu=use_vmu)

    """
        GET START AND END TIME OF NON WEAR SEGMENTS
    """

    # find all indexes of the numpy array that have been labeled non-wear time. Note that the function _find_candidate_non_wear_segments_from_raw returns
    # non-wear episodes as 1, and wear time as 1
    nw_indexes = np.where(nw_episodes == 0)[0]
    # find consecutive ranges
    non_wear_segments = _find_consecutive_index_ranges(nw_indexes)

    # check if segments are found
    if len(non_wear_segments[0]) > 0:

        # find start and stop times (the indexes of the edges and find corresponding time)
        for _, row in enumerate(non_wear_segments):

            # find start and stop
            start, stop = np.min(row), np.max(row)

            # calculate lenght of episode in minutes
            length = int((stop - start) / sample_freq / 60)

            # check if length exceeds threshold, if so, then this is non-wear time
            if length >= min_interval:
                # now update nw vector
                nw_vector[start:stop] = True

    # return values
    return nw_vector


def _forward_search_episode(acc_data, index, hz, max_search_min, std_threshold, verbose=False):
    """
    When we have an episode, this was created on a minute resolution, here we do a forward search to find the edges of the episode with a second resolution
    """

    # calculate max slice index
    max_slice_index = acc_data.shape[0]

    for ii in range(hz * 60 * max_search_min):

        # create new slices
        new_start_slice = index
        new_stop_slice = index + hz

        if verbose:
            logging.info('i: %s, new_start_slice: %s, new_stop_slice: %s', ii, new_start_slice, new_stop_slice)

        # check if the new stop slice exceeds the max_slice_index
        if new_stop_slice > max_slice_index:
            if verbose:
                logging.info('Max slice index reached: %s', max_slice_index)
            break

        # slice out new activity data
        slice_data = acc_data[new_start_slice:new_stop_slice]

        # calculate the standard deviation of each column (YXZ)
        std = np.std(slice_data, axis=0)

        # check if all of the standard deviations are below the standard deviation threshold
        if np.all(std <= std_threshold):

            # update index
            index = new_stop_slice
        else:
            break

    if verbose:
        logging.info('New index: %s, number of loops: %s', index, ii)

    return index


def _backward_search_episode(acc_data, index, hz, max_search_min, std_threshold, verbose=False):
    """
    When we have an episode, this was created on a minute resolution, here we do a backward search to find the edges of the episode with a second resolution
    """

    # calculate min slice index
    min_slice_index = 0

    for ii in range(hz * 60 * max_search_min):

        # create new slices
        new_start_slice = index - hz
        new_stop_slice = index

        if verbose:
            logging.info('i: %s, new_start_slice: %s, new_stop_slice: %s', ii, new_start_slice, new_stop_slice)

        # check if the new start slice exceeds the max_slice_index
        if new_start_slice < min_slice_index:
            if verbose:
                logging.debug('Minimum slice index reached: %s', min_slice_index)
            break

        # slice out new activity data
        slice_data = acc_data[new_start_slice:new_stop_slice]

        # calculate the standard deviation of each column (YXZ)
        std = np.std(slice_data, axis=0)

        # check if all of the standard deviations are belowii the standard deviation threshold
        if np.all(std <= std_threshold):

            # update index
            index = new_start_slice
        else:
            break

    if verbose:
        logging.info('New index: %s, number of loops: %s', index, ii)
    return index
