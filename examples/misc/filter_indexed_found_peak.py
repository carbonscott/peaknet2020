#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import os
from scipy.spatial import cKDTree

fl_peak_dict = 'peak_dict.pickle'
with open(fl_peak_dict, 'rb') as fh:
    peak_dict = pickle.load(fh)


##########################################
# Okay, let's find 'good' peaks on a panel
##########################################
## cKDTree()

peak_in_cxi_dict   = peak_dict['/reg/d/psdm/cxi/cxig3514/scratch/cwang31/psocake/r0041/cxig3514_0041.cxi']
peak_in_event_dict = peak_in_cxi_dict[5]
peak_in_panel_dict = peak_in_event_dict['q2a2']
peak_list_found_in_panel = peak_in_panel_dict['found']
peak_list_indexed_in_panel = peak_in_panel_dict['indexed']

peak_tree_found = cKDTree(peak_list_found_in_panel)
peak_tree_indexed = cKDTree(peak_list_indexed_in_panel)

idx = peak_tree_found.query_ball_tree(peak_tree_indexed, r = 20)

idx_good = [ i for i,v in enumerate(idx) if len(v) > 0.0 ]
