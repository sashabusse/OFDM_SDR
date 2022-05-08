#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
import numpy as np

def random_ofdm_sym(nfft, data_carriers_idx, pilot_carriers_idx, pilot_values):
    sym = np.zeros(nfft, dtype=np.complex64)
    sym[data_carriers_idx] = np.random.choice([-1, 1], data_carriers_idx.size)
    sym[pilot_carriers_idx] = pilot_values
    return sym

