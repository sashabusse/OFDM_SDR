#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class ofdm_corr_sync_cc(gr.basic_block):
    """
    docstring for block ofdm_corr_sync_cc
    """
    def __init__(self, nfft=1024, n_guard=128, corr_sz=64):
        gr.basic_block.__init__(self,
            name="ofdm_corr_sync_cc",
            in_sig=[np.complex64, ],
            out_sig=[np.complex64, np.complex64])
        
        self.nfft = nfft
        self.n_guard = n_guard
        self.corr_sz = corr_sz

        # to find correlation we need 
        self.set_history(self.nfft+self.n_guard)

    def forecast(self, noutput_items, ninputs):
        # ninputs is the number of input connections
        # setup size of input_items[i] for work call
        # the required number of input items is returned
        #   in a list where each element represents the
        #   number of required items for each input
        ninput_items_required = [noutput_items + self.nfft + self.n_guard - 1] * ninputs
        return ninput_items_required

    def general_work(self, input_items, output_items):
        # For this sample code, the general block is made to behave like a sync block
        noutput_items = min([len(items) for items in output_items] + [len(input_items[0]) - (self.nfft + self.n_guard - 1)])

        # let it be here for debug purposes
        #print("ofdm_corr_sync_cc.general_work: input.shape = {}, output.shape = {}".format(
        #    np.array(input_items).shape, np.array(output_items).shape), flush=True)

        # calculate correlations for 2nd output
        for i in range(noutput_items):
            s1 = np.array(input_items[0][i:i+self.corr_sz], dtype=np.complex64)
            s2 = np.array(input_items[0][i+self.nfft:i+self.nfft+self.corr_sz], dtype=np.complex64)

            output_items[1][i] = (s1 @ s2.conj())/np.sqrt((s1@s1.conj())*(s2@s2.conj()))

        # bypass signal on first output
        output_items[0][:] = input_items[0][-noutput_items:]

        self.consume_each(noutput_items)
        return noutput_items

