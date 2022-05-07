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

class test_block(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(self,
            name="test_block",
            in_sig=[(np.complex64, (nfft + ncp)*2), np.complex64],
            out_sig=[(np.complex64, nfft), ])

    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [noutput_items] * ninputs
        return ninput_items_required

    def general_work(self, input_items, output_items):
        ninput_items = min([len(items) for items in input_items])
        noutput_items = min(len(output_items[0]), ninput_items)

        for i in range(noutput_items):
            output_items[0][i] = self.process_next(input_items[0][i], input_items[1][i])

        self.consume_each(noutput_items)
        return noutput_items
    
    def process_next(self, iq_t, corr_arg):
        # determine frequency offset from repeatative train sym
        train_sym_corr = iq_t[ncp//2:ncp//2+nfft//2].conj() @ iq_t[ncp//2+nfft//2: ncp//2 + nfft]
        freq_offset = np.angle(train_sym_corr)/(nfft//2)/(2*np.pi)
        
        # eliminate freq offset
        iq_t *= np.exp(-2j*np.pi*freq_offset*np.arange(iq_t.size))

        # retrieve data ofdm sym
        ofdm_sym_t = iq_t[(ncp+nfft)+ncp//2:(ncp+nfft)+ncp//2+nfft]
        ofdm_sym_f = np.fft.ifft(ofdm_sym_t) 
        # eliminate phase rotation caused by taking start from middle of cp
        ofdm_sym_f *= np.exp(2j*np.pi*np.arange(nfft)*(ncp//2)/nfft)

        # precise time syncronization
        # calclulate average phase increase per sample
        pilot_diffs_est = np.angle(ofdm_sym_f[pilot_carriers[1:]]) - np.angle(ofdm_sym_f[pilot_carriers[:-1]])
        pilot_diffs_est[pilot_diffs_est < 0] += 2*np.pi
        pilot_diffs_val = np.angle(pilot_values[1:]) - np.angle(pilot_values[:-1])
        pilot_diffs_val[pilot_diffs_val < 0] += 2*np.pi
        
        pilot_idx_diff = np.array(pilot_carriers[1:]) - np.array(pilot_carriers[:-1])
        
        phase_per_sample_avg = np.mean((pilot_diffs_est - pilot_diffs_val)/pilot_idx_diff)
        
        # eliminate phase increase
        ofdm_sym_f = ofdm_sym_f * np.exp(-1j*phase_per_sample_avg*np.fft.fftfreq(nfft, 1./nfft))
        
        # remoove first pilot phase diff
        phase_diff = np.angle(ofdm_sym_f[pilot_carriers[0]]) - np.angle(pilot_values[0])
        ofdm_sym_f *= np.exp(-1j*phase_diff)
        
        # remove average pilot phase diff
        phase_diff = np.angle(ofdm_sym_f[pilot_carriers]) - np.angle(pilot_values)
        phase_diff[phase_diff <= np.pi] += 2*np.pi
        phase_diff[phase_diff > np.pi] -= 2*np.pi
        ofdm_sym_f *= np.exp(-1j*np.mean(phase_diff))

        # scale average pilot amplitude
        #mul = np.mean(np.abs(pilot_values) / np.abs(ofdm_sym_f[pilot_carriers]))
        #ofdm_sym_f *= mul

        ofdm_sym_f_tx = np.zeros(nfft, dtype=complex)
        np.random.seed(123)
        ofdm_sym_f_tx[5:25] = np.random.choice([1, -1], 25-5) #+ 1j*np.random.choice([1, -1], 20-10)
        ofdm_sym_f_tx[-25:-5] = np.random.choice([1, -1], 25-5) #+ 1j*np.random.choice([1, -1], 20-10)
        ofdm_sym_f_tx[pilot_carriers] = pilot_values

        ofdm_sym_f[ofdm_sym_f_tx!=0] *= ofdm_sym_f_tx.conj()[ofdm_sym_f_tx!=0]
        #ofdm_sym_f[pilot_carriers] = 0

        return ofdm_sym_f

        

