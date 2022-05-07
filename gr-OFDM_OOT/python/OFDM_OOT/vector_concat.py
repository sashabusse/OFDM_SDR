#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class vector_concat(gr.sync_block):
    """
    docstring for block vector_concat
    """
    def __init__(self, v1_sz, v2_sz):
        gr.sync_block.__init__(self,
            name="vector_concat",
            in_sig=[(np.complex64, v1_sz), ],
            out_sig=[(np.complex64, v2_sz), ])


    def work(self, input_items, output_items):
        output_items[0][:] = np.vstack(input_items)
        return len(output_items[0])
