#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class ofdm_frame_builder(gr.basic_block):
    def __init__(self, nfft=64, nguard=16, frame_sym_cnt=1, preamble=[]):
        self.nfft = nfft
        self.nguard = nguard
        self.frame_sym_cnt = frame_sym_cnt
        self.preamble = np.array(preamble, dtype=np.complex64)

        self.frame_sz = self.preamble.size + (self.nfft + self.nguard)*self.frame_sym_cnt

        gr.basic_block.__init__(self,
            name="ofdm_frame_builder",
            in_sig=[(np.complex64, self.nfft), ],
            out_sig=[(np.complex64, self.frame_sz), ])
        

    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [noutput_items*self.frame_sym_cnt, noutput_items]
        return ninput_items_required


    def generate_frame(self, in_sym):
        symbols_t = np.fft.ifft(in_sym, axis=1)
        for i in range(self.frame_sym_cnt):
            symbols_t[i] = symbols_t[i] * np.sqrt(self.nfft / np.sum(np.abs(symbols_t[i])**2))


        frame_list = [self.preamble]
        for sym_idx in range(self.frame_sym_cnt):
            frame_list += [symbols_t[sym_idx][-self.nguard:], symbols_t[sym_idx]]
        
        frame = np.hstack(frame_list)

        return frame


    def general_work(self, input_items, output_items):
        ofdm_sym_in = input_items[0]
        frame_out = output_items[0]

        ofdm_sym_available = len(ofdm_sym_in)
        frames_needed = len(frame_out)

        frames_processed = np.min([
            ofdm_sym_available//self.frame_sym_cnt, 
            frames_needed
        ])
        
        for i in range(frames_processed):
            frame = self.generate_frame(ofdm_sym_in[i*self.frame_sym_cnt:(i+1)*self.frame_sym_cnt])
            frame_out[i] = frame

        self.consume_each(frames_processed*self.frame_sym_cnt)
        return frames_processed

