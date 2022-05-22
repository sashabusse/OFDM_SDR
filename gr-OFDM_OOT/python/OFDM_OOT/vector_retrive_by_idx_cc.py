#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class vector_retrive_by_idx_cc(gr.sync_block):
    """
    docstring for block vector_retrive_by_idx_cc
    """
    def __init__(self, vlen_in=1, vlen_out=1, data_idx=[]):
        self.vlen_in = vlen_in
        self.vlen_out = vlen_out
        self.data_idx = np.array(data_idx, dtype=int)
        assert self.vlen_out == len(self.data_idx)
        gr.sync_block.__init__(self,
            name="vector_retrive_by_idx_cc",
            in_sig=[(np.complex64, vlen_in), ],
            out_sig=[(np.complex64, vlen_out), ])


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        out[:] = in0[:, self.data_idx]
        return len(output_items[0])
