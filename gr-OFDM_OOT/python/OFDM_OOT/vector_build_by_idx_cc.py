#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class vector_build_by_idx_cc(gr.sync_block):
    """
    docstring for block vector_build_by_idx_cc
    """
    def __init__(self, vlen_out=1, vlen_in=1, data_idx=[]):
        self.vlen_out = vlen_out
        self.vlen_in = vlen_in
        self.data_idx = np.array(data_idx, dtype=int)
        assert len(self.data_idx)==self.vlen_in
        gr.sync_block.__init__(self,
            name="vector_build_by_idx_cc",
            in_sig=[(np.complex64, self.vlen_in), ],
            out_sig=[(np.complex64, self.vlen_out), ])


    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]

        out[:, :] = 0
        out[:, self.data_idx] = in0[:, :]
        return len(out)
