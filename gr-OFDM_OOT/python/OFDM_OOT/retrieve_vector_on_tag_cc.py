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

class retrieve_vector_on_tag_cc(gr.basic_block):
    """
    docstring for block retrieve_vector_on_tag_cc
    """
    def __init__(self, tag='tag', vlen=1 ):
        gr.basic_block.__init__(self,
            name="retrieve_vector_on_tag_cc",
            in_sig=[np.complex64, ],
            out_sig=[(np.complex64, vlen), np.complex64])
        self.vlen = vlen
        self.tag = tag

    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [noutput_items*self.vlen] * ninputs
        return ninput_items_required

    def general_work(self, input_items, output_items):
        ninput_items = len(input_items[0])
        noutput_items = len(output_items[0])

        tags = self.get_tags_in_window(0, 0, ninput_items-self.vlen+1)

        items_processed = 0
        for tag in tags:
            if pmt.to_python(tag.key) != self.tag:
                continue
            if items_processed >= noutput_items:
                break
            
            tag_rel_offset = tag.offset - self.nitems_read(0)
            vec = np.array(input_items[0][tag_rel_offset:tag_rel_offset + self.vlen], 
                            dtype=np.complex64)

            output_items[0][items_processed] = vec
            output_items[1][items_processed] = pmt.to_python(tag.value)

            items_processed += 1

        self.consume_each(ninput_items-self.vlen + 1)
        return items_processed

