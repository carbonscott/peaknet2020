import os
from glob import glob
import json
import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from data import PSANAImageNoLabel, PSANADatasetNoLabel
from unet import UNet
from saver import Saver
import shutil
import argparse
import h5py

def evaluation_metrics(scores, y, cutoff=0.5):
    scores_c = scores[:, 0, :, :].reshape(-1)
    targets_c = y[:, 0, :, :].reshape(-1)
    gt_mask = targets_c > 0

    n_gt = targets_c.sum()
    positives = (nn.Sigmoid()(scores_c) > cutoff)
    n_p = positives.sum()
    n_tp = (positives[gt_mask]).sum()
    if n_p == 0:
        n_p = n_tp
    recall = float(n_tp) / max(1, int(n_gt))
    precision = float(n_tp) / max(1, int(n_p))

    metrics = {"recall": recall, "precision": precision}
    return metrics

def check_existence(exp, run):
    files = glob("/reg/d/psdm/cxi/{}/xtc/*{}*.xtc".format(exp, run))
    return len(files) > 0

def peak_find(model, device, params):
    model.eval()

    eval_dataset = PSANADatasetNoLabel(params["run_dataset_path"], shuffle=True, n=params["n_experiments"])
    seen = 0

    print('')
    print('---')
    print("Writing cxi file...")
    print("Name: " + params["save_name"])
    save_dir = "saved_outputs/psocake_cxi/"
    cxi_file = h5py.File(save_dir + params["save_name"] + '.cxi', 'w')

    # Groups in cxi file
    LCLS = cxi_file.create_group('LCLS')
    result_1 = cxi_file.create_group('entry_1/result_1')
    detector_1 = cxi_file.create_group('entry_1/instrument_1/detector_1')

    event_numbers = []

    total_steps = 0
    with torch.no_grad():
        for i, (exp, run) in enumerate(eval_dataset):
            if check_existence(exp, run):
                pass
            else:
                print("[{:}] exp: {}  run: {}  PRECHECK FAILED".format(i, exp, run))
                continue
            print("*********************************************************************")
            print("[{:}] exp: {}  run: {}".format(i, exp, run))
            print("*********************************************************************")
            psana_images = PSANAImageNoLabel(exp, run)
            data_loader = DataLoader(psana_images, batch_size=params["batch_size"], shuffle=True, drop_last=True,
                                     num_workers=params["num_workers"])
            for j, x in enumerate(data_loader):
                n = x.size(0)
                x = x.to(device)
                scores = model(x)

                total_steps += 1
                seen += n

                ### Do smtg w/ scores here
                event_numbers.append(j)
            psana_images.close()

    # Save cxi file
    print('')
    print("Saving cxi file...")
    LCLS.create_dataset('eventNumber', data=event_numbers)
    result_1.create_dataset('nPeaks', data=nPeaks_array)
    result_1.create_dataset('peak2', data=peak2)
    result_1.create_dataset('peak1', data=peak1)
    detector_1.create_dataset('description', data=default_detector)
    result_1.create_dataset('peakXPosRaw', data=peakXPosRaw)
    result_1.create_dataset('peakYPosRaw', data=peakYPosRaw)
    cxi_file.close()
    print("Saved!")

def parse_args():
    p = argparse.ArgumentParser(description=__doc__)

    # Existing model
    p.add_argument("--model_path", "-m", required=True, type=str, default=None, help="A path to .PT file")

    # System parameters
    p.add_argument("--gpu", "-g", type=int, default=0, help="Use GPU x")

    # Parameters that can be modified when calling evaluate.py
    p.add_argument("--run_dataset_path", type=str, default="/cds/home/a/axlevy/peaknet2020/data/cxic0415_psocake2.csv")
    p.add_argument("--cutoff_eval", type=float, default=0.5)
    p.add_argument("--print_every", type=int, default=10)
    p.add_argument("--upload_every", type=int, default=1)
    p.add_argument("--save_name", type=str, default=None)
    p.add_argument("--n_experiments", type=int, default=-1)
    p.add_argument("--n_per_run", type=int, default=-1)
    p.add_argument("--batch_size", type=int, default=5)
    p.add_argument("--num_workers", type=int, default=0)
    p.add_argument("--verbose", type=str, default="True")
    ### Downsample is 1 for now

    return p.parse_args()


def main():
    args = parse_args()

    # Existing model
    model = torch.load(args.model_path)

    # System parameters
    if args.gpu is not None and torch.cuda.is_available():
        device = torch.device("cuda:{}".format(args.gpu))
    else:
        device = torch.device("cpu")

    model = model.to(device)

    params = {}
    params["run_dataset_path"] = args.run_dataset_path
    params["cutoff_eval"] = args.cutoff_eval
    params["print_every"] = args.print_every
    params["upload_every"] = args.upload_every
    params["save_name"] = args.save_name
    params["n_experiments"] = args.n_experiments
    params["n_per_run"] = args.n_per_run
    params["batch_size"] = args.batch_size
    params["num_workers"] = args.num_workers
    if args.verbose == "True":
        params["verbose"] = True
    else:
        params["verbose"] = False

    if params["save_name"] is None:
        params["save_name"] = params["run_dataset_path"].split('.')[0].split('/')[-1]

    peak_find(model, device, params)


if __name__ == "__main__":
    main()