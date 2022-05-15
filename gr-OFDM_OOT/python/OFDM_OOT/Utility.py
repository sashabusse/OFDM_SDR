#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
import numpy as np

def random_ofdm_sym(nfft, data_carriers_idx, pilot_carriers_idx, pilot_values, data_modulation='bpsk'):
    assert data_modulation in set(('bpsk', 'qpsk')), 'bad modulation'

    sym = np.zeros(nfft, dtype=np.complex64)
    
    if data_modulation == 'bpsk':
        sym[data_carriers_idx] = np.random.choice([-1, 1], data_carriers_idx.size)
    elif data_modulation == 'qpsk':
        sym[data_carriers_idx] = (np.random.choice([-1, 1], data_carriers_idx.size) + \
                                1j*np.random.choice([-1, 1], data_carriers_idx.size))/np.sqrt(2)
    else:
        assert False, 'bad modulation and assertion'

    sym[pilot_carriers_idx] = pilot_values
    return sym


def nearest_good_size(size, granularity=4096):
    return int(np.ceil(size/granularity)*granularity)