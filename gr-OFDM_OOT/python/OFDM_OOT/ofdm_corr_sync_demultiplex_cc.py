#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import pmt


class ofdm_corr_sync_demultiplex_cc(gr.basic_block):
    """
    @brief  implements ofdm demultiplexing 
            with freq_offset elimination 
            triggered by 'ofdm_corr_sync' tag.
    
    @param nfft

    @output stream is vec_complex and is stream of ofdm symbols with rough syncronization
    """
    def __init__(self, nfft=1024):
        gr.basic_block.__init__(self,
            name="ofdm_corr_sync_demultiplex",
            in_sig=[np.complex64, ],
            out_sig=[(np.complex64, nfft), ]) # we will output vectors
        
        self.nfft = nfft
        self.nguard = 128

    def forecast(self, noutput_items, ninputs):
        # ninputs is the number of input connections
        # setup size of input_items[i] for work call
        # the required number of input items is returned
        #   in a list where each element represents the
        #   number of required items for each input

        ninput_items_required = [noutput_items*self.nfft + 1] * ninputs

        # debug purposes
        # print("ofdm_corr_sync_demultiplex.forecast(noutput_items={}, ninputs={})->ninput_items_required={}".format(
        #     noutput_items, ninputs, ninput_items_required), flush=True)

        return ninput_items_required

    def general_work(self, input_items, output_items):
        # For this sample code, the general block is made to behave like a sync block
        ninput_items = len(input_items[0])
        noutput_items = len(output_items[0])



        tags = self.get_tags_in_window(0, 0, ninput_items-self.nfft - self.nguard + 1)

        items_processed = 0
        for tag in tags:
            if pmt.to_python(tag.key) != 'cfar':
                continue
            if items_processed >= noutput_items:
                break
            
            tag_rel_offset = tag.offset - self.nitems_read(0)
            vec = np.array(input_items[0][tag_rel_offset + self.nguard//2:tag_rel_offset + self.nguard//2 + self.nfft], 
                            dtype=np.complex64)

            corr_angle = pmt.to_python(tag.value)
            output_items[0][items_processed] = np.fft.fft( vec*np.exp(-1j*(corr_angle/self.nfft)*np.arange(self.nfft)) ) * \
                                                np.exp(-2j*np.pi*np.arange(self.nfft)*(self.nguard - self.nguard//2)/self.nfft)

            items_processed += 1

        # if no tags just consume input otherwise program will hang
        self.consume_each(ninput_items-self.nfft-self.nguard + 1)
        return items_processed
