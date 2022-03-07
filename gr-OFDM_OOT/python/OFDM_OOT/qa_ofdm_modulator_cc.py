#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from gnuradio import gr, gr_unittest
from gnuradio import blocks
from pkg_resources import SOURCE_DIST
# from gnuradio import blocks
from gnuradio.OFDM_OOT import ofdm_modulator_cc

class qa_ofdm_modulator_cc(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):
        instance = ofdm_modulator_cc(1024, [2, 4, 6], [1, 3, 5, 7], 1.2, 128)
        
    def test_001_just_run_without_falling(self):
        nfft = 1024
        n_guard = 128
        pilot_val = 1.2
        pilot_idx = [1, 3, 5, 7]
        data_idx = [2, 4, 6]
        src_iq = np.random.rand(3) + 1j*np.random.rand(3)
        
        spec = np.zeros(nfft, dtype=complex)
        spec[data_idx] = src_iq
        spec[pilot_idx] = pilot_val
        exp_res = np.pad(np.fft.ifft(spec), (n_guard, 0), mode='wrap')

        mod = ofdm_modulator_cc(nfft, data_idx, pilot_idx, pilot_val, n_guard)
        src = blocks.vector_source_c(tuple(src_iq))
        dst = blocks.vector_sink_c()

        print("before connecting", flush=True)
        self.tb.connect(src, mod)
        self.tb.connect(mod, dst)
        self.tb.run()
        
        self.assertFloatTuplesAlmostEqual(list(exp_res), dst.data(), 7)

if __name__ == '__main__':
    gr_unittest.run(qa_ofdm_modulator_cc)
