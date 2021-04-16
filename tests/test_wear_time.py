import os

from paat import io, wear_time


TEST_ROOT = os.path.join(os.path.pardir, os.path.dirname(__file__))
FILE_PATH_SIMPLE = os.path.join(TEST_ROOT, 'resources/test_file.gt3x')


# standard deviation threshold in g
std_threshold = 0.004
# merge distance to group two nearby candidate nonwear episodes
distance_in_min = 5
# define window length to create input features for the CNN model
episode_window_sec = 7
# default classification when an episode does not have a starting or stop feature window (happens at t=0 or at the end of the data)
edge_true_or_false = True
# logical operator to see if both sides need to be classified as non-wear time (AND) or just a single side (OR)
start_stop_label_decision = 'and'

# load cnn model
cnn_model_file = os.path.join('/home/msw/Documents/paat/paat/models/', f'cnn_v2_{str(episode_window_sec)}.h5')


def test_non_wear_time_algorithm():
    actigraph_acc, actigraph_time, meta_data = io.read_gt3x(FILE_PATH_SIMPLE)

    nw_vector, nw_data = wear_time.cnn_nw_algorithm(raw_acc = actigraph_acc,
                									hz = int(meta_data['Sample_Rate']),
                									cnn_model_file = cnn_model_file,
                									std_threshold = std_threshold,
                									distance_in_min = distance_in_min,
                									episode_window_sec = episode_window_sec,
                									edge_true_or_false = edge_true_or_false,
                									start_stop_label_decision = start_stop_label_decision)
