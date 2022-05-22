#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 Vladislav.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class channel_est(gr.sync_block):
    """
    docstring for block channel_est
    """
    def __init__(self,nfft,n_pilot_carriers,pilot_carriers_idx,pilot_vals):
        gr.sync_block.__init__(self,
            name="channel_est",
            in_sig=[(np.complex64,nfft) ],
            out_sig=[(np.complex64,n_pilot_carriers) ])
        self.n_pilot_carriers = n_pilot_carriers
        self.pilot_carriers_idx = pilot_carriers_idx
        self.pilot_vals = pilot_vals


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        
        
        H_FD = in0[:,self.pilot_carriers_idx]*(np.conj(self.pilot_vals)/(self.pilot_vals*np.conj(self.pilot_vals)))
        H_TD = np.fft.fft(H_FD,self.n_pilot_carriers)
        
        
        
        out[:] = H_TD
        out[:,:] = np.mean(H_TD,axis=0)
        #out[:] = np.zeros(np.shape(out),dtype=np.complex64)
        
        return len(output_items[0])
