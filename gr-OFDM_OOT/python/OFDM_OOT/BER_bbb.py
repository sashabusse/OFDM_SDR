#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class BER_bbb(gr.basic_block):
    """
    @brief: 

    @param: out_mode = 'lg10' or 'normal'
        'lg10' - output log10(ber)
        'normal' - output ber

    @param: mode = 'exponential' or 'total'
        'exponential' - applies exponential filtering with given alpha
        'total' - calculates total BER from start
    
    @param: option for mode='exponential
    """
    def __init__(self, out_mode='lg10', mode='exponential', alpha=1e-3):
        gr.basic_block.__init__(self,
            name="BER_bbb",
            in_sig=[np.byte, np.byte ],
            out_sig=[np.float32, ])
        
        self.out_mode = out_mode
        self.mode = mode
        self.alpha = alpha
        self.total_errors=0
        self.total_bits=0
        self.ber = 0

        # lookup table for fast counting bits
        self.ones_cnt = np.array([bin(x).count("1") for x in range(256)], dtype=np.int8)

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
        ninput_items = min(len(input_items[0]), len(input_items[1]))
        noutput_items = len(output_items[0])
        items_processed =  min(ninput_items, noutput_items)

        diff_bits_cnt = self.ones_cnt[np.bitwise_xor(input_items[0][:items_processed], 
                                                     input_items[1][:items_processed])]
        
        if self.mode == 'total':
            for i in range(items_processed):
                self.total_bits += 8
                self.total_errors += diff_bits_cnt[i]
                output_items[0][i] = self.total_errors/self.total_bits
            self.ber = self.total_errors/self.total_bits

        elif self.mode == 'exponential':
            for i in range(items_processed):
                self.ber = self.ber*(1-self.alpha) + self.alpha*(diff_bits_cnt[i]/8)
                output_items[0][i] = self.ber

        if self.out_mode == 'lg10':
            output_items[0][:items_processed] = np.log10(output_items[0][:items_processed] + 1e-20)

        self.consume_each(items_processed)
        return items_processed

