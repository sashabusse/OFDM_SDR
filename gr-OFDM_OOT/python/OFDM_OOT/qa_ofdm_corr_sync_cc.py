#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr, gr_unittest
# from gnuradio import blocks
from gnuradio.OFDM_OOT import ofdm_corr_sync_cc

class qa_ofdm_corr_sync_cc(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        instance = ofdm_corr_sync_cc(nfft=1024, n_guard=128, corr_sz=64)

    #def test_001_descriptive_test_name(self):
        # set up fg
        #self.tb.run()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_ofdm_corr_sync_cc)
