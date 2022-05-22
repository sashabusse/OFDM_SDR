#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class vector_assign_cc(gr.sync_block):
    """
    docstring for block vector_assign_cc
    """
    def __init__(self, vlen=1, idx=[], data=[]):
        self.vlen = vlen
        self.idx = np.array(idx, dtype=int)
        self.data = np.array(data, dtype=np.complex64)

        assert len(self.idx) == len(self.data)
        assert np.all(self.idx < vlen)

        gr.sync_block.__init__(self,
            name="vector_assign_cc",
            in_sig=[(np.complex64, vlen), ],
            out_sig=[(np.complex64, vlen), ])


    def work(self, input_items, output_items):
        in_sym = input_items[0]
        out_sym = output_items[0]

        out_sym[:] = in_sym[:]
        out_sym[:, self.idx] = self.data

        return len(out_sym)
