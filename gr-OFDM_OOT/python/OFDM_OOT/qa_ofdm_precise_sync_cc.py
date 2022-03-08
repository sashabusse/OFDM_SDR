#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from gnuradio import gr, gr_unittest
# from gnuradio import blocks
from gnuradio.OFDM_OOT import ofdm_precise_sync_cc

class qa_ofdm_precise_sync_cc(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        instance = ofdm_precise_sync_cc(1024, np.arange(1, 100, 1), np.array([1]*99))

    #def test_001_just_run_without_fail(self):
        # set up fg
        #self.tb.run()
        # check data


if __name__ == '__main__':
    gr_unittest.run(qa_ofdm_precise_sync_cc)
