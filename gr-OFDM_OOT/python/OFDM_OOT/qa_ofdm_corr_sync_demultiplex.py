#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from gnuradio import blocks
from gnuradio import gr, gr_unittest
# from gnuradio import blocks
from gnuradio.OFDM_OOT import ofdm_corr_sync_demultiplex

class qa_ofdm_corr_sync_demultiplex(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        instance = ofdm_corr_sync_demultiplex(1024)

    # just run and nat fall
    def test_001_just_run(self):
        mod = ofdm_corr_sync_demultiplex(1024)
        src = blocks.vector_source_c(np.random.rand(1024) + 1j*np.random.rand(1024))
        dst = blocks.vector_sink_c(vlen=1024)

        self.tb.connect(src, mod)
        self.tb.connect(mod, dst)
        self.tb.run()

if __name__ == '__main__':
    gr_unittest.run(qa_ofdm_corr_sync_demultiplex)
