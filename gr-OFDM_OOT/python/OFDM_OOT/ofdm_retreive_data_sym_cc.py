#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class ofdm_retreive_data_sym_cc(gr.basic_block):
    """
    @brief retrieves vector of data carriers from vector of ofdm symbol
    
    @param nfft
    @param data_carriers_idx - carriers to be retrieved
    """
    def __init__(self, nfft=1024, data_carriers_idx=[]):
        gr.basic_block.__init__(self,
            name="ofdm_retreive_data_sym_cc",
            in_sig=[(np.complex64, nfft), ],
            out_sig=[(np.complex64, len(data_carriers_idx)), ])
        
        self.nfft = nfft
        self.data_carriers_idx = data_carriers_idx

    def forecast(self, noutput_items, ninputs):
        # ninputs is the number of input connections
        # setup size of input_items[i] for work call
        # the required number of input items is returned
        #   in a list where each element represents the
        #   number of required items for each input
        ninput_items_required = [noutput_items] * ninputs
        return ninput_items_required

    def general_work(self, input_items, output_items):
        # For this sample code, the general block is made to behave like a sync block
        ninput_items = len(input_items[0])
        noutput_items = len(output_items[0])

        items_processed = min(ninput_items, noutput_items)
        for i in range(items_processed):
            output_items[0][i] = input_items[0][i][self.data_carriers_idx]

        # debug purpose
        # print('retrieve_data.general_work(ninput_items={}, noutput_items={})->items_processed={}'.format(
        #     ninput_items, noutput_items, items_processed
        # ))

        self.consume_each(items_processed)
        return items_processed

