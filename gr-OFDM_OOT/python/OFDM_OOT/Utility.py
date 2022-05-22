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


def zcsequence(u, seq_length, q=0):
    """
    Generate a Zadoff-Chu (ZC) sequence.
    Parameters
    ----------
    u : int
        Root index of the the ZC sequence: u>0.
    seq_length : int
        Length of the sequence to be generated. Usually a prime number:
        u<seq_length, greatest-common-denominator(u,seq_length)=1.
    q : int
        Cyclic shift of the sequence (default 0).
    Returns
    -------
    zcseq : 1D ndarray of complex floats
        ZC sequence generated.
    """

    for el in [u,seq_length,q]:
        if not float(el).is_integer():
            raise ValueError('{} is not an integer'.format(el))
    if u<=0:
        raise ValueError('u is not stricly positive')
    if u>=seq_length:
        raise ValueError('u is not stricly smaller than seq_length')
    if np.gcd(u,seq_length)!=1:
        raise ValueError('the greatest common denominator of u and seq_length is not 1')

    cf = seq_length%2
    n = np.arange(seq_length)
    zcseq = np.exp( -1j * np.pi * u * n * (n+cf+2.*q) / seq_length)

    return zcseq