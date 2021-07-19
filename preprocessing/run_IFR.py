import os
import pandas as pd
import shutil
import argparse
import numpy as np

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--csv_path", type=str, required=True, help="Path to .csv file")
    return p.parse_args()

def main():
    args = parse_args()

    df = pd.read_csv(args.csv_path)

    print('')
    save_dir = 'IFR_psocake'
    print("Saving directory: " + save_dir)

    if os.path.exists(save_dir):
        y = 'y'
        print('')
        val = input("The saving directory exists. Overwrite? (y/n)")
        if val == 'y':
            shutil.rmtree(save_dir)
            print("Directory removed.")
        else:
            return

    os.makedirs(save_dir)

    experiments = list(set(df["experiment"]))
    n_son_mins = len(list(set(df["son_min"])))
    n_amax_thr = len(list(set(df["amax_thr"])))

    results = {}
    for exp in experiments:
        results[exp] = {}
        runs = list(set(df.query("experiment == '{}'".format(exp))["run"]))
        for run in runs:
            results[exp][run] = np.zeros((n_son_mins, n_amax_thr), dtype=float)

    

if __name__ == "__main__":
    main()