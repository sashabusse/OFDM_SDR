#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class autocorr_cc(gr.basic_block):
    def __init__(self, sz=48, dn=32, normalize=False, conjugate_second_term=False):
        gr.basic_block.__init__(self,
            name="autocorr_cc",
            in_sig=[np.complex64, ],
            out_sig=[np.complex64, np.complex64])
        
        self.sz = sz
        self.dn = dn
        self.normalize = normalize
        self.conjugate_second_term = conjugate_second_term

        self.s1s2 = 0

        # terms for normalization
        if self.normalize:
            self.s1s1 = 0
            self.s2s2 = 0

        self.set_history(self.dn + self.sz)


    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [self.history() + noutput_items - 1] * ninputs
        return ninput_items_required

    def process_next_correlation(self, in_signal):
        
        # add new tap
        s1_new = in_signal[self.sz-1]
        s2_new = in_signal[self.dn+self.sz-1]
        if self.conjugate_second_term:
            self.s1s2 += s1_new*s2_new.conj()
        else:
            self.s1s2 += s1_new.conj()*s2_new

        result = self.s1s2

        if self.normalize:
            self.s1s1 += np.abs(s1_new * s1_new.conj())
            self.s2s2 += np.abs(s2_new * s2_new.conj())

            result /= np.sqrt(self.s1s1 * self.s2s2)
        
        # substract taps which are not needed for later calculations
        s1_old = in_signal[0]
        s2_old = in_signal[self.dn]
        if self.conjugate_second_term:
            self.s1s2 -= s1_old*s2_old.conj()
        else:
            self.s1s2 -= s1_old.conj()*s2_old

        if self.normalize:
            self.s1s1 -= np.abs(s1_old * s1_old.conj())
            self.s2s2 -= np.abs(s2_old * s2_old.conj())

        return result


    def general_work(self, input_items, output_items):
        in_signal = input_items[0]
        out_signal = output_items[0]
        out_corr = output_items[1]

        in_available = len(in_signal) - (self.history() - 1)
        items_processed = np.min([len(out_signal), len(out_corr), in_available])

        # bypass signal
        out_signal[:items_processed] = in_signal[:items_processed]

        # calculate correlations
        for i in range(items_processed):
            out_corr[i] = self.process_next_correlation(in_signal[i:i+self.history()])

        self.consume_each(items_processed)
        return items_processed

