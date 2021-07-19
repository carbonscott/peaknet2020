import os
import pandas as pd
import shutil
import argparse
import numpy as np
from streamManager import iStream
import psana

def get_new_seen(extract):
    seen = []
    for idx in range(len(extract.label.index)):
        event_idx = get_event_number(extract, idx)
        seen.append(event_idx)
    seen = list(set(seen))
    return seen

def get_event_number(extract, idx_stream):
    event_number_pos = extract.label.index[idx_stream][2]
    line = extract.content[event_number_pos]
    id = int(line.split()[1].split('/')[2])
    return id

class Experiment:
    def __init__(self, experimentName, runNumber, detInfo='cspad'):
        self.experimentName = experimentName
        self.runNumber = runNumber
        self.detInfo = detInfo

    def setup(self):
        access = 'exp=' + str(self.experimentName) + ':run=' + str(self.runNumber) + ':idx'
        self.ds = psana.DataSource(access)
        self.run = next(self.ds.runs())
        self.times = self.run.times()
        self.eventTotal = len(self.times)

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
            results[exp][run] = {"n_indexed": np.zeros((n_son_mins, n_amax_thrs), dtype=float), "seen_events": []}
    results["son_mins"] = son_mins
    results["amax_thrs"] = amax_thrs

    for i in range(len(df)):

        print('')
        print(str(i + 1) + '/' + str(len(df)))

        filename = df.iloc[i]["filename"]
        exp = df.iloc[i]["experiment"]
        run = df.iloc[i]["run"]
        son_min = df.iloc[i]["son_min"]
        amax_thr = df.iloc[i]["amax_thr"]
        son_min_idx = np.argwhere(son_mins == son_min)
        amax_thr_idx = np.argwhere(amax_thrs == amax_thr)

        print('Experiment: ' + str(exp))
        print('Run: ' + str(run))
        print('son_min: ' + str(son_min))
        print('amax_thr: ' + str(amax_thr))

        print("Reading stream file...")
        extract = iStream()
        extract.initial(fstream=filename)
        extract.get_label()
        extract.get_info()

        indexed = len(extract.label.index)
        print("Number of reflection lists in stream: " + str(indexed))

        # my_exp = Experiment(exp, run, None)
        # my_exp.setup()
        # total = my_exp.eventTotal
        # print("Number of events: " + str(total))
        # ratio = float(indexed) / float(total)
        # print("Indexing Rate: " + str(ratio))
        # print("Indexing Failure Rate: " + str(1 - ratio))

        results[exp][run]["n_indexed"][son_min_idx, amax_thr_idx] = indexed

        seen = get_new_seen(extract)
        results[exp][run]["seen_events"] = list(set(results[exp][run]["seen_events"] + seen))

        print("Seen events: " + str(len(results[exp][run]["seen_events"])))

    for exp in experiments:
        for run in results[exp].keys():
            results[exp][run]["seen_events"] = len(results[exp][run]["seen_events"])

    save_name = save_dir + '/results.npy'
    print("Saving at " + save_name)
    np.save(save_name, results)
    print("Saved!")

if __name__ == "__main__":
    main()