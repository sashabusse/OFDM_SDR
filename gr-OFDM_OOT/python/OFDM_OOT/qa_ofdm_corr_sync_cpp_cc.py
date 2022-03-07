#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from gnuradio import gr, gr_unittest
# from gnuradio import blocks
try:
  from gnuradio.OFDM_OOT import ofdm_corr_sync_cpp_cc
except ImportError:
    import os
    import sys
    dirname, filename = os.path.split(os.path.abspath(__file__))
    sys.path.append(os.path.join(dirname, "bindings"))
    from gnuradio.OFDM_OOT import ofdm_corr_sync_cpp_cc

class qa_ofdm_corr_sync_cpp_cc(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        # FIXME: Test will fail until you pass sensible arguments to the constructor
        instance = ofdm_corr_sync_cpp_cc(nfft=1024, n_guard=128, corr_sz=64)

    #def test_001_descriptive_test_name(self):
        # set up fg
        #self.tb.run()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_ofdm_corr_sync_cpp_cc)
