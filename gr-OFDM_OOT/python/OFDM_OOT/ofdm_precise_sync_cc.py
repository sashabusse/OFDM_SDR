#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import time

class ofdm_precise_sync_cc(gr.basic_block):
    """
    @brief implements precise syncronization with use of pilots

    @param nfft
    @param piot_carrier
    """
    def __init__(self, nfft=64, pilot_groups_idx=[[]], pilot_groups_vals=[[]], report_freq_off=False):
        gr.basic_block.__init__(self,
            name="ofdm_precise_sync_cc",
            in_sig=[(np.complex64, nfft), ],
            out_sig=[(np.complex64, nfft), ])
        
        assert len(pilot_groups_idx) == len(pilot_groups_vals), 'different sizes of idx and vals'

        self.nfft = nfft
        self.pilot_groups_idx = pilot_groups_idx
        self.pilot_groups_vals = pilot_groups_vals

        self.report_freq_off = report_freq_off
        self.last_report_time = time.time()

    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [noutput_items] * ninputs
        return ninput_items_required

    def process_next(self,sym_in):
        # precise time syncronization
        # calclulate average phase increase per sample
        group_phase_per_sample_avg = []
        for group_idx in range(len(self.pilot_groups_idx)):
            pilots_idx = np.array(self.pilot_groups_idx[group_idx])
            pilots_val = np.array(self.pilot_groups_vals[group_idx])

            pilot_diffs_est =   np.angle(sym_in[pilots_idx[1:]]) - \
                                np.angle(sym_in[pilots_idx[:-1]])
            pilot_diffs_est[pilot_diffs_est < 0] += 2*np.pi

            pilot_diffs_val =   np.angle(pilots_val[1:]) - \
                                np.angle(pilots_val[:-1])
            pilot_diffs_val[pilot_diffs_val < 0] += 2*np.pi

            pilot_idx_diff =    pilots_idx[1:] - \
                                pilots_idx[:-1]

            group_phase_per_sample_avg.append(
                np.mean((pilot_diffs_est - pilot_diffs_val)/pilot_idx_diff)
            )
        
        phase_per_sample_avg = np.mean(group_phase_per_sample_avg)

        if self.report_freq_off and time.time() - self.last_report_time > 0.5:
            shift_est = phase_per_sample_avg*self.nfft/(2*np.pi)
            print("precise sync : shift_est = {:.3f}".format(shift_est))
            self.last_report_time = time.time()

        
        # eliminate phase increase
        # fftfreq to account that second part is actually negative frequency
        sym_in = sym_in * np.exp(-1j*phase_per_sample_avg*np.fft.fftfreq(self.nfft, 1./self.nfft))

        # remoove first pilot phase diff
        phase_diff = np.angle(sym_in[self.pilot_groups_idx[0][0]]) - np.angle(self.pilot_groups_vals[0][0])
        sym_in *= np.exp(-1j*phase_diff)

        # remove average pilot phase diff
        group_phase_diff_avg = []
        for group_idx in range(len(self.pilot_groups_idx)):
            pilots_idx = np.array(self.pilot_groups_idx[group_idx])
            pilots_val = np.array(self.pilot_groups_vals[group_idx])

            phase_diff = np.angle(sym_in[pilots_idx]) - np.angle(pilots_val)
            phase_diff[phase_diff <= np.pi] += 2*np.pi
            phase_diff[phase_diff > np.pi] -= 2*np.pi

            group_phase_diff_avg.append(np.mean(phase_diff))

        phase_diff_avg = np.mean(group_phase_diff_avg)
        sym_in *= np.exp(-1j*phase_diff_avg)

        # scale average pilot amplitude
        #mul = np.mean(np.abs(self.pilot_carriers_vals) / np.abs(sym_in[self.pilot_carriers_idx]))
        #sym_in *= mul

        return sym_in

    def general_work(self, input_items, output_items):
        ninput_items = len(input_items[0])
        noutput_items = len(output_items[0])

        items_processed = min(ninput_items, noutput_items)
        for i in range(items_processed):
            output_items[0][i] = self.process_next(input_items[0][i])

        self.consume_each(items_processed)
        return items_processed



