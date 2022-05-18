#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
from termios import N_MOUSE
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


def cox_schmerzmittel_estimate(preamble_rx_sym, nfft=64, nguard=16):
    assert preamble_rx_sym.size == nfft+nguard, 'bad arguments'

    part1 = preamble_rx_sym[nguard//2:nguard//2+nfft//2]
    part2 = preamble_rx_sym[nguard//2+nfft//2:nguard//2+nfft]

    corr = part1.conj()@part2
    cfo_est = np.angle(corr)/(2*np.pi)/(nfft//2)
    return cfo_est


def cox_schmerzmittel_cfg(nfft=64, nguard=16):
    return {
        'sz': nfft+nguard,
        'cfo_est_func': cox_schmerzmittel_estimate,
        'cfo_est_args': (nfft, nguard)
    }    


def repeat_seqN(seq_len=32, N=4, f_border=0.35, seed=1349):

    np.random.seed(seed)
    fft_freq_cond = np.abs(np.fft.fftfreq(seq_len)) < f_border
    
    train_seq_f = np.zeros(seq_len, dtype=np.complex64)
    train_seq_f[fft_freq_cond] = np.random.choice([-1, 1], np.sum(fft_freq_cond))
    train_seq_f[0] = 0
    
    train_seq_t = np.fft.ifft(train_seq_f)
    train_seq_t = train_seq_t * np.sqrt(train_seq_t.size / np.sum(np.abs(train_seq_t)**2))
    
    preamble = np.hstack([train_seq_t]*N)
    
    return preamble


def repeat_seqN_estimate(preamble_rx, seq_len=32, N=4):
    assert preamble_rx.size == seq_len*N, 'bad arguments'
    corr = preamble_rx[:seq_len*(N-1)].conj() @ preamble_rx[seq_len:]
    cfo_est = np.angle(corr)/(2*np.pi)/seq_len
    return cfo_est


def repeat_seqN_cfg(seq_len=32, N=4):
    return {
        'sz': seq_len*N,
        'cfo_est_func': repeat_seqN_estimate,
        'cfo_est_args': (seq_len, N)
    }   


def cp_average_est(frame_symbols_t, nfft, nguard, frame_sym_cnt, margin=1):
    cfo_est_avg = 0
    for sym_idx in range(frame_sym_cnt):
        sym_st = sym_idx*(nfft+nguard)
        p1 = frame_symbols_t[sym_st + margin: sym_st + nguard - margin]
        p2 = frame_symbols_t[sym_st + nfft + margin: sym_st + nfft + nguard - margin]
        corr = p1.conj() @ p2
        cfo_est = np.angle(corr)/(2*np.pi)/nfft

        cfo_est_avg += cfo_est/frame_sym_cnt
    
    return cfo_est_avg

    