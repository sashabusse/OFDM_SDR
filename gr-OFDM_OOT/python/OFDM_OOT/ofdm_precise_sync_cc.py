#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class ofdm_precise_sync_cc(gr.basic_block):
    """
    @brief implements precise syncronization with use of pilots

    @param nfft
    @param piot_carrier
    """
    def __init__(self, nfft=1024, pilot_carriers_idx=[], pilot_carriers_vals=[]):
        gr.basic_block.__init__(self,
            name="ofdm_precise_sync_cc",
            in_sig=[(np.complex64, nfft), ],
            out_sig=[(np.complex64, nfft), ])
        
        self.nfft = nfft
        self.pilot_carriers_idx = pilot_carriers_idx
        self.pilot_carriers_vals = pilot_carriers_vals

    def forecast(self, noutput_items, ninputs):
        # ninputs is the number of input connections
        # setup size of input_items[i] for work call
        # the required number of input items is returned
        #   in a list where each element represents the
        #   number of required items for each input
        ninput_items_required = [noutput_items] * ninputs
        return ninput_items_required

    def process_next(self,in_iq):
        # precise time syncronization
        # calclulate average phase increase per sample
        pilot_diffs_est = np.angle(in_iq[self.pilot_carriers_idx[1:]]) - np.angle(in_iq[self.pilot_carriers_idx[:-1]])
        pilot_diffs_est[pilot_diffs_est < 0] += 2*np.pi
        pilot_diffs_val = np.angle(self.pilot_carriers_vals[1:]) - np.angle(self.pilot_carriers_vals[:-1])
        pilot_diffs_val[pilot_diffs_val < 0] += 2*np.pi

        pilot_idx_diff = np.array(self.pilot_carriers_idx[1:]) - np.array(self.pilot_carriers_idx[:-1])

        phase_per_sample_avg = np.mean((pilot_diffs_est - pilot_diffs_val)/pilot_idx_diff)
        
        # eliminate phase increase
        in_iq = in_iq * np.exp(-1j*phase_per_sample_avg*np.arange(self.nfft))

        # remoove first pilot phase diff
        phase_diff = np.angle(in_iq[self.pilot_carriers_idx[0]]) - np.angle(self.pilot_carriers_vals[0])
        in_iq *= np.exp(-1j*phase_diff)

        # remove average pilot phase diff
        phase_diff = np.angle(in_iq[self.pilot_carriers_idx]) - np.angle(self.pilot_carriers_vals)
        phase_diff[phase_diff <= np.pi] += 2*np.pi
        phase_diff[phase_diff > np.pi] -= 2*np.pi
        in_iq *= np.exp(-1j*np.mean(phase_diff))

        # scale average pilot amplitude
        mul = np.mean(np.abs(self.pilot_carriers_vals) / np.abs(in_iq[self.pilot_carriers_idx]))
        in_iq *= mul

        return in_iq

    def general_work(self, input_items, output_items):
        ninput_items = len(input_items[0])
        noutput_items = len(output_items[0])

        items_processed = min(ninput_items, noutput_items)
        for i in range(items_processed):
            output_items[0][i] = self.process_next(input_items[0][i])

        # debug purposes
        #print("precise_sync.general_work(ninput_items={}, n_output_items={})->items_processed={}".format(
        #    ninput_items, noutput_items, items_processed), flush=True)

        self.consume_each(items_processed)
        return items_processed



