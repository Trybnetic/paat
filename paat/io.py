"""
Input & Output Module
---------------------

*paat.io* provides loading and saving functions to process the raw
acceleration signals.

"""

import os
import logging
import zipfile
from struct import unpack
import tempfile
import sys

import numpy as np
import pandas as pd
from bitstring import Bits

from . import preprocessing


def _unzip_gt3x_file(file, save_location=None, delete_source_file=False, metadata_only=False):
    """
    Unzip the .gt3x file

    Parameters
    ---------
    file : string
        file location of the .gt3x file
    save_location : string (optional)
        location where the unzipped files should be saved, if not given, files are saved within the same folder as f
    delete_source_file : Boolean (Optional)
        if True, then the original .gt3x file will be deleted after it is unzipped
    metadata_only : Boolean (optional)
        if True, only the metadata info.txt file is unzipped. This saves a lot of time if only the metadata should loaded

    Returns
    -------
    log_bin : string
        location where the log.bin file is stored
    info_txt : string
        location where the info.txt file is stored
    """

    # if save location is not given, then save in the same folder
    # as where the file resides with the folder name equal the name of the file
    if save_location is None:
        save_location = os.path.splitext(file)[0]

    # if folder does not exist, create it
    if not os.path.exists(save_location):
        os.makedirs(save_location)

    # create the path locations where the log.bin and info.txt files are stored
    log_bin = os.path.join(save_location, 'log.bin')
    info_txt = os.path.join(save_location, 'info.txt')

    if metadata_only:
        with zipfile.ZipFile(file, 'r') as myzip:
            myzip.extract("info.txt", path=save_location)

        return info_txt

    # check if file already exists
    if not os.path.exists(log_bin) and not os.path.exists(info_txt):

        try:
            # unzip the file
            with zipfile.ZipFile(file, 'r') as myzip:

                myzip.extractall(save_location)

        except Exception as msg:
            logging.error('Error unpacked file: %s', msg)
            return None, None

        finally:
            # delete source file if delete_source_file parameter is set to True
            if delete_source_file:
                os.remove(file)
    else:
        logging.debug('file already unpacked: %s', file)

    # return location of the files
    return log_bin, info_txt


def _extract_info(info_txt):

    """
    Extract the content from the info.txt file that was unzipped from the raw .gt3x file
    Example:
    {'Battery_Voltage': '3,83', 'Acceleration_Scale': '256.0', 'Download_Date': '635672143370000000', 'Unexpected_Resets': '0', 'Stop_Date': '635664672000000000',
    'Firmware': '1.3.0', 'Acceleration_Min': '-8.0', 'Subject_Name': '90046928', 'Last_Sample_Time': '635664672000000000', 'Sample_Rate': '100',
    'Device_Type': 'wGT3XBT', 'TimeZone': '02:00:00', 'Acceleration_Max': '8.0', 'Serial_Number': 'MOS2C02150348', 'Start_Date': '635658624000000000',
    'Board_Revision': '3'}

    Parameters
    ----------
    info_txt : string
        location of the info.txt file on disk

    Returns
    -------
    info_data : dictionary
        dictionary of key, value pairs as extracted from the info file
    """

    # create empty dictionary
    info_data = {}

    try:
        # open the file
        with open(info_txt, 'r') as file:
            # loop trough each of the lines
            for line in file.readlines():
                # strip away the new lines
                line = line.strip('\r\n')
                # split on semicolon + space (the timezone value has semicolons in it and not using the space would cause issues splitting it)
                key, value = line.split(': ')
                # add to dictionary and replace key values with space in key with underscore
                info_data[key.replace(' ', '_')] = value
    except Exception as msg:
        logging.error('Error extracting data from info.txt file: %s', msg)

    # return dictionary
    return info_data


def _extract_log(log_bin, acceleration_scale, sample_rate, use_scaling=False):
    """
    Extract acceleration data from log.bin file that was unzipped from the raw .gt3x file
    One second of raw activity samples packed into 12-bit values in YXZ order.

    Parameters
    ----------
    log_bin : string
        location of the log.bin file on disk
    acceleration_scale : float
        Scale the resultant by the scale factor (this gives us an acceleration value in g's).
        Device serial numbers starting with NEO and CLE use a scale factor of 341 LSB/g (±6g).
        MOS devices use a 256 LSB/g scale factor (±8g). If a LOG_PARAMETER record is preset,
        then the ACCEL_SCALE value should be used.
    sample_rate : int
        sample rate, i.e. the number of Hz (how many values we obtain per second)
        This value can also be inferred from the payload size when you know how many axis data you have.
        So payload size of 450 bytes = 300 (12 bit sized ints). And when we have 3 axis, we have 300/3 = 100 values per 3-axis per second
    use_scaling: Boolean (optional)
        acceleration data is originally stored as a signed integer. To obtain the acceleration value we need to scale it with the acceleration_scale
        this will give us the decimal numbers. However, this would also increase memory size of the array in which we store the values. We might not want to
        scale if we only want to store the data in a smaller memory size format. Scaling can then be done at a later stage, for instance, when we want to pre-process the data

    Returns
    -------
    log_data : numpy array (time steps * sample_rate, num axes)
        log data contains the raw acceleration values in YXZ order
    log_time : numpy array (time steps, 1)
        log time contains the timestamps of measurements
    """

    # define the size of the payload. This is necessary because we need to define the size of the numpy array before we populate it.
    SIZE = _count_payload_size(log_bin)
    # raw data values are stored in ints, to obtain values in G, we need to scale them by a factor found in the acceleration_scale parameter within the info.txt file. For example, 256.0
    SCALING = 1. / acceleration_scale
    # counter so we can keep track of how many acceleration values we have processed
    COUNTER = 0
    # number of axes, the GTX3 is tri-axial, so we hard code it here.
    NUM_AXES = 3

    # empty dictionary where we can store the 12bit to signed integer values; this saves calculating them all the time
    bit12_to_int = {}

    """
        create empty numpy array where we can store the acceleration data to: dimensions (sample_rate x SIZE,number of axis)
        if we want to scale the values to floats, we need a bigger datatype, it would take more memory. If no scaling is necessary, because we can scale later during preprocessing or so, we can
        proceed with just an int8 datatype array.
        For example, without scaling, 7 days of data equals around 180MB, with scaling the numpy array equals around 1.5GB
    """

    # use int16 as datatype to store the signed integer values, this saves memory when saving the array
    acc_data_type = np.int16
    if use_scaling:
        # use float when we want to store the acceleration data in G, meaning that we the scaling factor to recalculate the signed int into decimal values
        acc_data_type = float
    # create empty array for the acceleration data
    log_data = np.empty((sample_rate * SIZE, NUM_AXES), dtype=acc_data_type)
    # empty numpy array to store the timestamps
    time_data = np.empty((SIZE, 1), dtype=np.uint32)

    # open the log.bin file in binary mode
    with open(log_bin, mode='rb') as file:

        try:

            # keep reading byte by byte
            while True:

                """
                Log Record Format
                Offset (bytes)    Size (bytes)    Name    Description    Part of Record
                0    1    Seperator    An ASCII record separator byte (1Eh) marks the beginning of each log record.    Header
                1    1    Type    A type identifier is used to interpret the payload of the record.    Header
                2    4    Timestamp    The date and time of the data contained in the record are marked to the nearest second in Unix time format.    Header
                6    2    Size    The size of the payload is given in bytes as an little-endian unsigned integer.    Header
                """
                _, payload_type, timestamp, size = unpack("<cbLH", file.read(8))

                # acceleration type 0 is the activity data, we skip all other data but can easily be read with an if statement
                if payload_type == 0:

                    """
                        This is the actual data that varies based on the record *Type* field. It's size is provided in the *Size* field. Please refer to the appropriate section for the record type for the indiviual payload formats.

                        read the payload in bits (the reason we are converting the bytes to bits is that 1 acceleration value is encoded in 12bit, so we can cut out 12 bits at a time from the full payload represented as individual bits)
                        basically the YXZ (3 axis) is 12 bit + 12 bit + 12 bit = 36 bits. When we have 100hz, we have a total of 36 * 100 = 3600 bits. When you look at the size of the payload in bytes, that is for instance 450 bytes, you can
                        see that this is also 450 * 8 = 3600 bits
                    """

                    # read the bytes as bits as a large string
                    payload_bits = Bits(bytes=file.read(size)).bin

                    # extract 12 bits as 1 acceleration value and add them to a list
                    bits_list = []
                    for ii in range(0, len(payload_bits), 12):

                        # extract the 12 bit as a string
                        bitstring = payload_bits[ii:ii + 12]

                        # convert to 12bit two's complement to signed integer value: also store values in dictionary for faster reading if not already present (the Bits function is not as fast as reading it from a dictionary)
                        if bitstring not in bit12_to_int:
                            # convert 12bit to signed integer
                            acc_value = Bits(bin=bitstring).int
                            # add to dictionary so we can read it faster next time we have the same value
                            bit12_to_int[bitstring] = acc_value
                        else:
                            # bitstring previously already converted to signed int, so we can obtain it from the dictionary
                            acc_value = bit12_to_int[bitstring]

                        # add to list
                        bits_list.append(acc_value)

                    # convert list to numpy array and perform scaling if it was set to True: no scaling allows for a smaller numpy array because we can use int8 and not need the float
                    if use_scaling:
                        payload_bits_array = np.array(bits_list).reshape(sample_rate, NUM_AXES) * SCALING
                    else:
                        payload_bits_array = np.array(bits_list).reshape(sample_rate, NUM_AXES)

                    # add payload bits array to overall numpy array
                    np_start = COUNTER * sample_rate
                    np_end = np_start + sample_rate
                    log_data[np_start:np_end] = payload_bits_array

                    # add the time component
                    time_data[COUNTER] = timestamp

                    # increase the counter
                    COUNTER += 1

                else:
                    # skip whatever is not acceleration data
                    # there are different payload types and can easily be read by adding a different payload_type in this section
                    file.seek(size, 1)

                """
                A 1-byte checksum immediately follows the record payload. It is a 1's complement, exclusive-or (XOR) of the log header and payload with an initial value of zero.
                TODO: calculate checksum from payload and header and see if it matches the checksum that we read from the last byte
                """
                _ = unpack("B", file.read(1))

                # stop when all records have been read
                if COUNTER == SIZE:

                    logging.info('Finished processing activity data')
                    break

        except Exception as msg:
            logging.error('Unpacking GTX3 exception: %s', msg)
            return None, None

        # return acceleration data + time data
        return log_data, time_data


def _count_payload_size(log_bin, count_payload=0):
    """
    Count the payload size of the log.bin file. The size of the payload is necessary to know how large
    the numpy array needs to be that will be populated while reading the log.bin file byte by byte. The reasons why
    is that populating an array is much faster than appending new array values to it

    Parameters
    ----------
    log_bin : string
        location of the log.bin file on disk
    count_payload : int (optional)
        the payload type that we want to count. default is 0, which is the acceleration data.

    Returns
    -------
    SIZE : int
        the size (as in count) of the payload
    """

    # define size variable
    SIZE = 0

    # open the log.bin file in binary mode
    with open(log_bin, mode='rb') as file:

        try:
            # keep reading byte by byte
            while True:

                # extract header information
                _, payload_type, _, size = unpack("<cbLH", file.read(8))

                # count payload
                if payload_type == count_payload:

                    # skip the byte content, we don't need to process it here
                    file.seek(size, 1)
                    # increment counter
                    SIZE += 1
                else:
                    # skip other payload types, we don't need to read it here
                    file.seek(size, 1)

                # skip the 1-byte checksum value
                file.seek(1, 1)

        except Exception:
            logging.info('Counted payload size: %s', SIZE)

            # return the value
            return SIZE


def _create_time_array(time_data, hz=100):
    """
    Create a time array by adding the miliseconds range of the sampling frequency
    the standard time array only accounts for full seconds. However, when the sampling
    frequency is 100 hertz for instance, we need to add 100 microseconds to the data

    Parameters
    ----------
    time_data : np.array
        numpy array containing unix timestamps (obtained by reading the raw .gt3x data)
    hz : int (optional)
        sampling frequency of the acceleration data (this is to know how many miliseconds we need to add to the time series)

    Returns
    -------
    time_data : np.array
        numpy array with correct number of time series (so now the sampling frequency is added within the original data which only contained seconds and not miliseconds)

    Raises
    ------
    NotImplementedError
        If the sampling frequency does not fit on milisecond precision
    """

    # check if the sampling frequenzy can fit into equal parts within a 1000ms window
    if 1000 % hz != 0:
        raise NotImplementedError("Creating time array does not support sampling frequencies other than 100hz yet. See https://github.com/Trybnetic/paat/issues/10")

    # calculate the step size of hz in 1s (so 100hz means 100 measurements in 1sec, so if we need to fill 1000ms then we need use a step size of 10)
    step_size = 1000 / hz
    # convert time_data of unix timestamps to numpy array of 64 bit seconds
    time_data = np.asarray(time_data, dtype='datetime64[s]')
    # convert the array to 64 bit milliseconds and add a time delta of a range of ms within a 1000ms window
    time_data = np.asarray(time_data, dtype='datetime64[ms]') + np.asarray(np.arange(0, 1000, step_size), dtype='timedelta64[ms]')
    # flatten the array
    time_data = time_data.flatten()

    return time_data


def _format_time(tstamp):
    tstamp = int(tstamp) // 10000000 + np.datetime64('0001-01-01T00:00:00').astype(int)
    return int(tstamp) * 1000


def _format_meta_data(meta):
    """
    Formats the meta data dict that is extracted from the gt3x file

    Parameters
    ----------
    meta : dict
        the meta data dict from the gt3x file

    Returns
    -------
    new_meta : dict
        an updated meta data dict having the fields of meta in the correct format
    """
    new_meta = {}

    # standard meta data fields of ActiGraph and their conversion functions
    fields_and_formats = {'Serial_Number': str,
                          'Device_Type': str,
                          'Firmware': str,
                          'Battery_Voltage': str,
                          'Sample_Rate': int,
                          'Start_Date': _format_time,
                          'Stop_Date': _format_time,
                          'Last_Sample_Time': _format_time,
                          'TimeZone': str,
                          'Download_Date': _format_time,
                          'Board_Revision': int,
                          'Unexpected_Resets': int,
                          'Acceleration_Scale': float,
                          'Acceleration_Min': float,
                          'Acceleration_Max': float,
                          'Subject_Name': str}

    for field, dtype in fields_and_formats.items():
        try:
            new_meta[field] = dtype(meta[field])
        except KeyError as msg:
            logging.info(msg)

    return new_meta


def _create_time_vector(start, n_samples, hz):
    """
    Creates a time vector starting at point start until start + n_samples/hz
    with a sampling frequency of hz

    Parameters
    ----------
    start : int or np.datetime64
        start point of the time vector at second precision level.
    n_samples : int
        number of samples
    hz : int
        sampling frequency

    Returns
    -------
    time_data : np.array
        a numpy array of np.datetime64 at nanosecond precision

    Raises
    ------
    NotImplementedError
        If the sampling frequency does not fit on milisecond precision
    """

    n_sec = n_samples / hz

    if not n_sec.is_integer():
        logging.error('Actiwave time in seconds not a whole number: %s', n_sec)
        sys.exit()

    # declare how many nanoseconds in one second
    ms_in_sec = 1e3

    # check if the sampling frequenzy can fit into equal parts within a nanosecond window
    if ms_in_sec % hz != 0:
        raise NotImplementedError("Creating time vector does not support sampling frequencies other than 100hz yet. See https://github.com/Trybnetic/paat/issues/10")

    step_size = ms_in_sec / hz

    # convert the array to 64 bit nanoseconds (necessary to fit 128hz for instance) and add a time delta of a range nanoseconds in seconds * lenght_sec, with corresponding stepsize
    time_data = np.asarray(start, dtype='datetime64[ms]') + np.asarray(np.arange(0, ms_in_sec * n_sec, step_size), dtype='timedelta64[ms]')

    return time_data.flatten()


def read_gt3x(file, rescale=True, pandas=True, metadata=False):
    """
    Reads a .gt3x file and returns the tri-axial acceleration values together
    with the corresponding time stamps and all meta data.

    Parameters
    ----------
    file : string
        file location of the .gt3x file
    rescale : boolean (optional)
        boolean indicating whether raw acceleration data should be rescaled to g values
    pandas : boolean (optional)
        boolean indicating whether the data should be returned as a pandas DataFrame
    metadata : boolean (optional)
        boolean indicating whether the full metadata should be returned

    Returns
    -------
    data : DataFrame
        a DataFrame containg the raw acceleration data
    sample_freq : int
        the sampling frequency in which the data was recorded
    time : np.array (n_samples x 1)
        a numpy array with time stamps for the observations in values
    values : np.array (n_samples x 3)
        a numpy array with the tri-axial acceleration values. If rescale is true, data
        is rescaled to units of g. Note, that this function returns the values in
        the default order of ActiGraph which is ['Y','X','Z']. Depending on further
        use, you might want to adjust that order.
    meta : dict
        a dict containing all meta data produced by ActiGraph

    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # unzip .gt3x file and get the file location of the binary log.bin (which contains the raw data) and the info.txt which contains the meta-data
        log_bin, info_txt = _unzip_gt3x_file(file=file, save_location=tmpdirname)

        # get meta data from info.txt file
        meta = _extract_info(info_txt)

        meta = _format_meta_data(meta)

        # extract acceleration data from the log file
        values, time_data = _extract_log(log_bin, meta['Acceleration_Scale'], meta['Sample_Rate'], use_scaling=rescale)

        # create time array
        time = _create_time_array(time_data, hz=meta['Sample_Rate'])

        # Add additional keys to meta (Note: they are important to later reconstruct the time vector)
        meta["Number_Of_Samples"] = values.shape[0]
        meta["Start_Time"] = time[0].astype(int)

    if pandas:
        data = pd.DataFrame(values, columns=["Y", "X", "Z"], index=time)
        data = data[["X", "Y", "Z"]]
        if metadata:
            return data, meta['Sample_Rate'], meta
        else:
            return data, meta['Sample_Rate']
    else:
        return time, values, meta


def read_metadata(file):
    """
    Reads the metadata from a .gt3x file.

    Parameters
    ----------
    file : string
        file location of the .gt3x file
    
    Returns
    -------
    meta : dict
        a dict containing all meta data produced by ActiGraph

    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # unzip .gt3x file and get the file location of the binary log.bin (which contains the raw data) and the info.txt which contains the meta-data
        info_txt = _unzip_gt3x_file(file=file, save_location=tmpdirname, metadata_only=True)

        # get meta data from info.txt file
        meta = _extract_info(info_txt)

    meta = _format_meta_data(meta)

    return meta