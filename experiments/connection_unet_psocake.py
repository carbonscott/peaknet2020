import numpy as np
import os

os.chdir("/cds/home/a/axlevy/peaknet2020/peaknet")

experiment_name = "my_model"
model_path = "debug/" + experiment_name + "/model.pt"
os.system('python peaknet_for_psocake.py --model_path ' + model_path)