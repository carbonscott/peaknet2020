import numpy as np
import os

os.chdir("/cds/home/a/axlevy/peaknet2020/peaknet")

os.system('python train.py params.json -g 0 --pos_weight 1e-4'
          ' --run_dataset_path /cds/home/a/axlevy/peaknet2020/data/official_training_set.csv'
          ' --experiment_name official_unet_1 --n_epochs 1 --n_per_run 1000')