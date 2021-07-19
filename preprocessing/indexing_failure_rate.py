import numpy as np
import h5py
from streamManager import iStream
import argparse
import psana
import os
import shutil


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
    p.add_argument("--filename", "-f", type=str, required=True, help="Path to .stream file")
    p.add_argument("--experiment", "-e", type=str, required=True, help="Name of experiment")
    p.add_argument("--run", "-r", type=int, required=True, help="Run index")
    return p.parse_args()

def main():
    args = parse_args()

    print(args.filename)

    extract = iStream()
    extract.initial(fstream=args.filename)
    extract.get_label()
    extract.get_info()

    indexed = len(extract.label.index)
    print("Number of reflection lists in stream: " + str(indexed))

    my_exp = Experiment(args.experiement, args.run, None)
    my_exp.setup()

    total = my_exp.eventTotal
    print("Number of events: " + str(total))

    print("Indexing Rate: " + str(indexed / total))
    print("Indexing Failure Rate: " + str(1 - indexed / total))

if __name__ == "__main__":
    main()