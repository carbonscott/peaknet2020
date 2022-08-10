#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import logging

logger = logging.getLogger(__name__)

class ConfigParam:

    def __init__(self, name_cls = '', **kwargs):
        self.name_cls = name_cls

        self.kwargs = kwargs
        for k, v in kwargs.items(): setattr(self, k, v)


    def report(self):
        logger.info(f"___/ Configure '{self.name_cls}' \___")
        for k, v in self.__dict__.items():
            if k == 'kwargs': continue
            logger.info(f"KV - {k:16s} : {v}")




class ExtractPeak:
    '''
    Extract successfully indexed peaks previously found by psocake peak finder.
    '''

    def __init__(self, config):
        self.path_stream = getattr(config, 'path_stream', None)

        self.marker_dict = {
            "CHUNK_START"      : "----- Begin chunk -----",
            "CHUNK_END"        : "----- End chunk -----",
            "PEAK_LIST_START"  : "Peaks from peak search",
            "PEAK_LIST_END"    : "End of peak list",
            "CRYSTAL_START"    : "--- Begin crystal",
            "CRYSTAL_END"      : "--- End crystal",
            "REFLECTION_START" : "Reflections measured after indexing",
            "REFLECTION_END"   : "End of reflections",
        }

        self.peak_dict = {}


    def setup_re(self):
        '''
        Set up extended regex for parsing a stream file.
        '''
        # Define the regex that matches a line with peak found...
        re_match_found_peak = re.compile(
            r"""(?xm)
                    ^                                      # Match the beginning
                    (?:
                        (?: [-+]?(?:\d+(?:\.\d*)?|\.\d+) ) # Match a floating number
                        \s+?                               # Match whitespace at least once
                    ){4}                                   # Match the whole construct 4 times

                    (?: [0-9A-Za-z]+ )                     # Match a detector panel
                    $                                      # Match the end
             """)

        # Define the regex that matches a line with peak indexed...
        re_match_indexed_peak = re.compile(
            r'''(?xm)
                    ^                                      # Match the beginning
                    (?:
                        (?: [-+]?(?:\d+(?:\.\d*)?|\.\d+) ) # Match a floating number
                        \s+?                               # Match whitespace at least once
                    ){9}                                   # Match the whole construct 9 times

                    (?:[0-9A-Za-z]+)                       # Match a detector panel
                    $                                      # Match the end
             ''')

        return re_match_found_peak, re_match_indexed_peak


    def parse(self):
        '''
        Return a dictionary of events that contain successfully indexed peaks
        found by psocake peak finder.
        '''
        # Setup regex for matching purposes...
        re_match_found_peak, re_match_indexed_peak = self.setup_re()

        # Define state variable...
        record_ok = False

        # Import marker...
        marker_dict = self.marker_dict

        # Start parsing a stream file by chunks...
        path_stream = self.path_stream
        with open(path_stream,'r') as fh:
            for line in fh.readlines():
                line = line.strip()

                # Turn off recording by default for a new chunk...
                if line == marker_dict["CHUNK_START"]: record_ok = False

                # Look up filename...
                if line.startswith("Image filename: "):
                    filename = line[line.rfind(':') + 1:] # e.g. 'Image filename: /xxx/cxig3514_0041.cxi'
                    filename = filename.strip()

                # Look up event number...
                if line.startswith("Event: "):
                    event_num = line[line.rfind('/') + 1:] # e.g. 'Event: //17'
                    event_num = int(event_num)

                # Look up indexing status...
                if line.startswith("indexed_by"):
                    status_indexing = line[line.rfind('=') + 1:].strip() # e.g. 'indexed_by = none'

                    # Turn on recording when indexing is successful...
                    if status_indexing != 'none': record_ok = True

                # Don't record anything???
                if not record_ok: continue

                # Get ready to save results from events in each file...
                # Accumulate by filename
                if not filename in self.peak_dict: self.peak_dict[filename] = {}

                # Accumulate by event number
                if not event_num in self.peak_dict[filename]:
                    self.peak_dict[filename][event_num] = {
                        "found"   : {},
                        "indexed" : {},
                    }

                # Is it a found peak???
                match_result = re_match_found_peak.match(line)
                if match_result is not None:
                    data = match_result.group(0)
                    dim1, dim2, _, _, panel = data.split()

                    if not panel in self.peak_dict[filename][event_num]["found"]: 
                        self.peak_dict[filename ] \
                                      [event_num] \
                                      ["found"  ] \
                                      [panel    ] = []

                    self.peak_dict[filename ] \
                                  [event_num] \
                                  ["found"  ] \
                                  [panel    ].append([float(dim1), 
                                                      float(dim2),])

                # Is it a indexed peak???
                match_result = re_match_indexed_peak.match(line)
                if match_result is not None:
                    data = match_result.group(0)
                    _, _, _, _, _, _, _, dim1, dim2, panel = data.split()

                    if not panel in self.peak_dict[filename ] \
                                                  [event_num] \
                                                  ["indexed"]:
                        self.peak_dict[filename ] \
                                      [event_num] \
                                      ["indexed"] \
                                      [panel    ] = []

                    self.peak_dict[filename ] \
                                  [event_num] \
                                  ["indexed"] \
                                  [panel    ].append([float(dim1), 
                                                      float(dim2),])


# [[[ EXAMPLE ]]]

## path_stream = '/reg/data/ana15/cxi/cxig3514/scratch/cwang31/psocake/r0041/cxig3514_0041.stream'
path_stream = '/reg/data/ana15/cxi/cxig3514/scratch/cwang31/psocake/r0041/cxig3514_0041_d100.stream'
## path_stream = '/reg/data/ana15/cxi/cxig3514/scratch/cwang31/psocake/r0041/test.stream'
config_extract_peak = ConfigParam( path_stream = path_stream )
extract_peak = ExtractPeak(config_extract_peak)
extract_peak.parse()
