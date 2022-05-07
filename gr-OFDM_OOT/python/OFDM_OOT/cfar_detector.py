#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import pmt

class cfar_detector(gr.basic_block):
    """
    docstring for block cfar_detector
    """
    def __init__(self, train_regions = [-100, -10], p_false_alarm=1e-4, n_search_forward=0, n_skip_after_detect=0):
        gr.basic_block.__init__(self,
            name="cfar_detector",
            in_sig=[np.complex64, np.complex64 ],
            out_sig=[np.complex64, np.complex64 ])
        
        self.train_regions = np.array(train_regions)
        self.p_false_alarm = p_false_alarm
        self.n_search_forward = n_search_forward
        self.n_skip_after_detect = n_skip_after_detect

        self.noise_power_est = 0
        
        assert self.train_regions.size > 0 and self.train_regions.size%2 == 0, 'bad train_regions sequence'
        for i in range(0, self.train_regions.size, 2):
            assert self.train_regions[i+1] > self.train_regions[i], 'bad train regions sequence'
        

        # precalculate number of train cell for later averaging
        self.train_sz = 0
        for i in range(0, self.train_regions.size, 2):
            self.train_sz += self.train_regions[i+1] - self.train_regions[i]

        # calculate needed history
        assert n_search_forward >= 0, 'negative n_search_forward'
        max_idx_needed = np.max([n_search_forward, self.train_regions[1::2].max()-1]) # -1 cause intervals
        min_idx_needed = np.min([0, self.train_regions[0::2].min()])
        self.set_history(max_idx_needed - min_idx_needed + 1)
        # skip data cause first taps are zero which can lead to false alarm
        self.skip_left = self.history()

        # positions of regions and cut in relation to first sample
        self.cut_rel_pos = -min_idx_needed
        self.train_regions_rel_pos = self.train_regions - min_idx_needed

        # treshold factor
        N = np.sum(self.train_regions[1::2] - self.train_regions[0::2])
        self.treshold_factor = N * (self.p_false_alarm**(-1. / N) - 1)


    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [self.history() + noutput_items - 1] * ninputs
        return ninput_items_required


    def process_next(self, in_corr, tg_idx):
        # add new taps
        self.noise_power_est += np.sum(np.abs(
            in_corr[self.train_regions_rel_pos[1::2]-1]
        ))/self.train_sz

        current_noise_power_est = self.noise_power_est

        # substract taps that shouldn't be summed for the next step
        self.noise_power_est -= np.sum(np.abs(
            in_corr[self.train_regions_rel_pos[0::2]]
        ))/self.train_sz

        # tag streams
        if self.skip_left == 0:
            treshold = self.treshold_factor * current_noise_power_est
            cut = in_corr[self.cut_rel_pos]

            if np.abs(cut) > treshold:
                max_idx = np.argmax(np.abs(
                    in_corr[self.cut_rel_pos:self.cut_rel_pos + self.n_search_forward]
                ))

                self.skip_left = max_idx + self.n_skip_after_detect

                corr_arg = np.angle(in_corr[self.cut_rel_pos + max_idx])
                self.add_item_tag(0,
                                self.nitems_written(0) + tg_idx + max_idx,
                                pmt.intern("cfar"),
                                pmt.from_float(corr_arg))

                self.add_item_tag(1,
                                self.nitems_written(1) + tg_idx + max_idx,
                                pmt.intern("cfar"),
                                pmt.from_float(corr_arg))
        
        self.skip_left = np.max([0, self.skip_left - 1])


    def general_work(self, input_items, output_items):
        in_signal = input_items[0]
        in_corr = input_items[1]
        out_signal = output_items[0]
        out_corr = output_items[1]

        in_available = np.min([len(in_signal), len(in_corr)]) - (self.history() - 1)
        items_processed = np.min([len(out_signal), len(out_corr), in_available])

        out_signal[:items_processed] = in_signal[self.cut_rel_pos: self.cut_rel_pos + items_processed]
        out_corr[:items_processed] = in_corr[self.cut_rel_pos: self.cut_rel_pos + items_processed]

        for i in range(items_processed):
            self.process_next(in_corr[i:i+self.history()], i)

        self.consume_each(items_processed)
        return items_processed

