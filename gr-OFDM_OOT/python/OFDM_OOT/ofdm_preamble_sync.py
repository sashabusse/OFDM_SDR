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

class ofdm_preamble_sync(gr.basic_block):
    """
    produces frame synchronization with preamble or cp
    """
    def __init__(self, nfft=64, nguard=16, frame_sym_cnt=1, report_freq_off=False):
        gr.basic_block.__init__(self,
            name="ofdm_preamble_sync",
            in_sig=[(np.complex64, (nfft+nguard) + (nfft+nguard)*frame_sym_cnt), np.complex64],
            out_sig=[(np.complex64, nfft), ])
        
        self.nfft = nfft
        self.nguard = nguard
        self.frame_sym_cnt = frame_sym_cnt
        
        self.report_freq_off = report_freq_off
        self.last_report_time = time.time()
    
    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [(noutput_items + self.frame_sym_cnt - 1)//self.frame_sym_cnt] * ninputs
        return ninput_items_required

    def general_work(self, input_items, output_items):
        in_frame = input_items[0]
        in_corr_arg = input_items[1]
        out_ofdm_sym = output_items[0]

        frames_to_process = np.min([len(in_frame), 
                                    len(in_corr_arg), 
                                    len(out_ofdm_sym)//self.frame_sym_cnt])

        preamble_sz = self.nfft + self.nguard
        
        for frame_idx in range(frames_to_process):
            freq_offset_est = in_corr_arg[frame_idx]/(2*np.pi)/(self.nfft/2)

            if self.report_freq_off and time.time() - self.last_report_time > 0.5:
                print('preamble_sync: freq_off_est = {:.5f} (max allowed = {:.5f})'.format(freq_offset_est, 0.5*(1/32)))
                self.last_report_time = time.time()

            for ofdm_sym_idx in range(self.frame_sym_cnt):
                ofdm_sym_start_idx = preamble_sz + (self.nfft+self.nguard)*ofdm_sym_idx + self.nguard//2
                ofdm_sym_t = in_frame[frame_idx][ofdm_sym_start_idx: ofdm_sym_start_idx + self.nfft]
                # compensate freq
                ofdm_sym_t *= np.exp(-2j*np.pi*freq_offset_est*np.arange(ofdm_sym_t.size))

                ofdm_sym_f = np.fft.fft(ofdm_sym_t)
                # compensate roll caused by taking symbol from the middle of cyclic prefix
                ofdm_sym_f *= np.exp(2j*np.pi*np.arange(self.nfft)*(self.nguard - self.nguard//2)/self.nfft)

                out_ofdm_sym[frame_idx*self.frame_sym_cnt + ofdm_sym_idx] = ofdm_sym_f

        self.consume_each(frames_to_process)
        return frames_to_process*self.frame_sym_cnt
