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
    son_mins = np.sort(list(set(df["son_min"])))
    amax_thrs = np.sort(list(set(df["amax_thr"])))
    n_son_mins = len(son_mins)
    n_amax_thrs = len(amax_thrs)

    results = {}
    for exp in experiments:
        results[exp] = {}
        runs = list(set(df.query("experiment == '{}'".format(exp))["run"]))
        for run in runs:
            results[exp][run] = np.zeros((n_son_mins, n_amax_thrs), dtype=float)
    results["son_mins"] = son_mins
    results["amax_thrs"] = amax_thrs

    for i in range(len(df)):
        filename = df.iloc[i]["filename"]
        exp = df.iloc[i]["experiment"]
        run = df.iloc[i]["run"]
        son_min = df.iloc[i]["son_min"]
        amax_thr = df.iloc[i]["amax_thr"]
        son_min_idx = np.argwhere(son_mins == son_min)
        amax_thr_idx = np.argwhere(amax_thrs == amax_thr)
        results[exp][run][son_min_idx, amax_thr_idx] = son_min + amax_thr

    print(results)

if __name__ == "__main__":
    main()