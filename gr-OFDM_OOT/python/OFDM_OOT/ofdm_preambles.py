#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
import numpy as np

def cox_schmerzmittel(nfft=64, nguard=16, carriers_available=None, seed=1349):
    if carriers_available is None:
        carriers_available = np.arange(nfft)
    carrier_idx = np.intersect1d(np.arange(2, nfft, 2), carriers_available)

    np.random.seed(seed)
    carrier_val = np.random.choice([-1, 1], carrier_idx.size)
    
    train_sym_f = np.zeros(nfft, dtype=np.complex64)
    train_sym_f[carrier_idx] = carrier_val
    
    train_sym_t = np.fft.ifft(train_sym_f)
    train_sym_t = train_sym_t * np.sqrt(train_sym_t.size / np.sum(np.abs(train_sym_t)**2))
    
    preamble = np.hstack([train_sym_t[-nguard:], train_sym_t])
    
    return preamble
