#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np
from scipy import interpolate

def sco_estimate(sym1_f, sym2_f, sym_dist_t, pilot_idx):
    assert sym1_f.size == sym2_f.size
    R = sym1_f.conj()*sym2_f

    pilot_idx_symmetric = pilot_idx.copy()
    pilot_idx_symmetric[pilot_idx_symmetric > sym1_f.size//2] = -(sym1_f.size - pilot_idx_symmetric[pilot_idx_symmetric > sym1_f.size//2])

    ang_diff = np.angle(sym1_f.conj()*sym2_f)[pilot_idx]
    sco_est = np.mean(np.sign(pilot_idx_symmetric)*ang_diff/np.abs(pilot_idx_symmetric))*sym1_f.size/sym_dist_t/(2*np.pi)

    return sco_est


# frame without header
def sco_estimate_frame(frame_t, nfft, nguard, frame_sym_cnt, pilot_idx):
    sco_est_avg = 0
    for sym_idx in range(frame_sym_cnt-1):
        sym1_st = sym_idx*(nfft+nguard) + nguard//2
        sym1_f = np.fft.fft(frame_t[sym1_st:sym1_st+nfft])
        sym2_st = (sym_idx+1)*(nfft+nguard) + nguard//2
        sym2_f = np.fft.fft(frame_t[sym2_st:sym2_st+nfft])

        sco_est_avg += sco_estimate(sym1_f, sym2_f, nfft+nguard, pilot_idx)/(frame_sym_cnt-1)
    
    return sco_est_avg


def sco_interpolate_spline(frame_t, sco_est, order=3):
    tck_real = interpolate.splrep(np.arange(frame_t.size), frame_t.real, k=order)
    tck_imag = interpolate.splrep(np.arange(frame_t.size), frame_t.imag, k=order)
    xnew = np.arange(frame_t.size)*(1-sco_est)
    frame_t_new = interpolate.splev(xnew, tck_real) + 1j*interpolate.splev(xnew, tck_imag)
    return frame_t_new
        
    




