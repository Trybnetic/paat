import os

import tensorflow as tf
from tensorflow.keras.models import load_model

model_file = "TIB_model"

for m in os.listdir("./"):
    if m.endswith(".h5"):
        model_file = m.split(".")[0]
    else:
        continue

    model= load_model(f'{model_file}.h5')
    def freeze_graph(graph,session,output_node_names,save_pb_dir='.',save_pb_name=f'{model_file}.pb',save_pb_as_text=False):
        with graph.as_default():
            output_graph_def= tf.graph.util.convert_variables_to_constants(session,grapg.as_graph_def(),output_node_names)
            tf.graph.io_write_graph(output_graph_def,save_pb_dir, save_pb_name, as_text=save_pb_as_text)

    model.export(f'{model_file}.pb')

    print(f'Model {model_file} converted into PB successfully')
