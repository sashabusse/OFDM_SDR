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


class ofdm_corr_sync_demultiplex(gr.basic_block):
    """
    docstring for block ofdm_corr_sync_demultiplex
    """
    def __init__(self, nfft=1024):
        gr.basic_block.__init__(self,
            name="ofdm_corr_sync_demultiplex",
            in_sig=[np.complex64, ],
            out_sig=[(np.complex64, nfft), ]) # we will output vectors
        
        self.nfft = nfft

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

        tags = self.get_tags_in_window(0, 0, ninput_items-self.nfft)

        items_processed = 0
        input_consumed = 0
        for tag in tags:
            if pmt.to_python(tag.key) != 'ofdm_corr_sync':
                continue
            if items_processed >= noutput_items:
                break
            
            tag_rel_offset = tag.offset - self.nitems_read(0)
            vec = np.array(input_items[0][tag_rel_offset:tag_rel_offset+self.nfft], dtype=np.complex64)

            freq_offset = pmt.to_python(tag.value)
            output_items[0][items_processed] = np.fft.fft( vec*np.exp(-1j*(2*np.pi)*freq_offset*np.arange(self.nfft)) )

            input_consumed = max(input_consumed, tag_rel_offset + 1)

            items_processed += 1


        # debug purposes
        # print("ofdm_corr_sync_demultiplex.general_work("
        #         "noutput_items={},"
        #         "ninput_items={})->"
        #         "(items_processed={}, input_consumed={}".format(
        #     noutput_items, ninput_items, items_processed, input_consumed), flush=True)

        # if no tags just consume input otherwise program will hang
        if len(tags) == 0:
            self.consume_each(ninput_items)
        else:
            self.consume_each(input_consumed)
        return items_processed

