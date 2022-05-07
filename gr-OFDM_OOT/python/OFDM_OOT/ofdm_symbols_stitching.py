#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class ofdm_symbols_stitching(gr.basic_block):
    """
    docstring for block ofdm_symbols_stitching
    """
    def __init__(self, nfft=1024, nguard=128):
        gr.basic_block.__init__(self,
            name="ofdm_symbols_stitching",
            in_sig=[(np.complex64, nfft), ],
            out_sig=[np.complex64, ])
        
        self.nfft = nfft
        self.nguard = nguard
        
        self.set_output_multiple(self.nfft + self.nguard)

    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [noutput_items//(self.nfft+self.nguard)] * ninputs
        return ninput_items_required

    def general_work(self, input_items, output_items):
        ninput_items = len(input_items[0])
        noutput_ofdm_symbols = min(len(output_items[0])//(self.nfft+self.nguard), ninput_items)
        
        for i in range(noutput_ofdm_symbols):
            output_items[0][i*(self.nfft+self.nguard): (i+1)*(self.nfft+self.nguard)] = \
                np.hstack([input_items[0][i][-self.nguard:], input_items[0][i]])

        self.consume_each(noutput_ofdm_symbols)
        return noutput_ofdm_symbols * (self.nfft+self.nguard)

