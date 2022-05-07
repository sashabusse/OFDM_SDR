#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

nfft = 64
ncp = 16

pilot_carriers = np.hstack([np.arange(10, 21, 4)])
pilot_values = 1.3 * np.exp(2j*np.pi*0.5*np.arange(pilot_carriers.size))

class ofdm_source(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self,
            name="ofdm_source",
            in_sig=None,
            out_sig=[(np.complex64, (nfft + ncp)*2 + 200), ])


    def work(self, input_items, output_items):
        out = output_items[0]
        out_sz = len(out)

        train_sym1_f = np.zeros(nfft, dtype=complex)
        np.random.seed(1349)
        train_sym1_f[np.arange(2, 23, 2)] = np.random.choice([-1, 1], np.arange(2, 23, 2).size)
        train_sym1_f[np.arange(-2, -23, -2)] = np.random.choice([-1, 1], np.arange(-2, -23, -2).size)
        #train_sym1_f[np.arange(2, 23, 2)] = np.exp(1j*np.pi*np.arange(2, 23, 2)/2)
        #train_sym1_f[np.arange(-2, -23, -2)] = -np.exp(1j*np.pi*np.arange(2, 23, 2)/2)

        ofdm_sym_f = np.zeros(nfft, dtype=complex)
        np.random.seed(123)
        ofdm_sym_f[5:25] = np.random.choice([1, -1], 25-5) #+ 1j*np.random.choice([1, -1], 20-10)
        ofdm_sym_f[-25:-5] = np.random.choice([1, -1], 25-5) #+ 1j*np.random.choice([1, -1], 20-10)
        ofdm_sym_f[pilot_carriers] = pilot_values

        train_sym1_t = np.fft.ifft(train_sym1_f)
        train_sym1_t = train_sym1_t * np.sqrt(train_sym1_t.size / np.sum(np.abs(train_sym1_t)**2))
        ofdm_sym_t = np.fft.ifft(ofdm_sym_f)
        ofdm_sym_t = ofdm_sym_t * np.sqrt(ofdm_sym_t.size / np.sum(np.abs(ofdm_sym_t)**2))

        frame = np.hstack([train_sym1_t[-ncp:], train_sym1_t] + [ofdm_sym_t[-ncp:], ofdm_sym_t] + [np.zeros(200)])

        out[0] = frame
        return 1
