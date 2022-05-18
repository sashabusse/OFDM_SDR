#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import time
from gnuradio import OFDM_OOT


class ofdm_preamble_sync(gr.basic_block):
    """
    produces frame synchronization with preamble or cp
    """
    def __init__(   
        self, 
        nfft=64, 
        nguard=16, 
        frame_sym_cnt=1, 
        # freq sync parameters
        compensate_cfo=True,
        cfo_est_cfg=None,
        use_cfo_cp_avg_est=False,
        # sco sync paramters
        compensate_sco = False,
        sco_interp_order = 3,
        pilot_idx=np.zeros((0, ), dtype=int),
        # debug and utility functions
        in_sz=0,
        debug_report=False
        ):

        self.nfft = nfft
        self.nguard = nguard
        self.frame_sym_cnt = frame_sym_cnt
        
        # cfo estimate parameters
        self.compensate_cfo = compensate_cfo
        self.cfo_est_cfg = cfo_est_cfg
        if self.cfo_est_cfg is None:
            self.cfo_est_cfg = OFDM_OOT.ofdm_preambles.cox_schmerzmittel_cfg(self.nfft, self.nguard)
        assert all(x in self.cfo_est_cfg for x in ['sz', 'cfo_est_func', 'cfo_est_args']), 'wrong preamble cfg'
        self.use_cfo_cp_avg_est = use_cfo_cp_avg_est

        # sco estimate parameters
        self.compensate_sco = compensate_sco
        self.sco_interp_order = sco_interp_order
        assert np.all(pilot_idx%1 == 0), 'pilot_idx should be integer array'
        self.pilot_idx=np.array(pilot_idx, dtype=int)
        self.sco_est = 0

        # debug/utility
        self.in_sz = in_sz
        assert self.in_sz != 0
        self.debug_report = debug_report
        self.last_report_time = time.time()
        
        # derived parameters
        self.frame_sz = self.cfo_est_cfg['sz'] + (nfft+nguard)*frame_sym_cnt
        gr.basic_block.__init__(self,
            name="ofdm_preamble_sync",
            in_sig=[(np.complex64, self.in_sz), ],
            out_sig=[(np.complex64, nfft), ])
        
    
    def forecast(self, noutput_items, ninputs):
        ninput_items_required = [(noutput_items + self.frame_sym_cnt - 1)//self.frame_sym_cnt] * ninputs
        return ninput_items_required


    def general_work(self, input_items, output_items):
        in_frame = input_items[0]
        out_ofdm_sym = output_items[0]

        frames_to_process = np.min([len(in_frame), 
                                    len(out_ofdm_sym)//self.frame_sym_cnt])

        preamble_sz = self.cfo_est_cfg['sz']
        
        for frame_idx in range(frames_to_process):
            # eliminate sco
            if self.compensate_sco:
                in_frame[frame_idx] = OFDM_OOT.ofdm_sco_sync.sco_interpolate_spline(in_frame[frame_idx], self.sco_est, self.sco_interp_order)

            # cfo estimation/compensation ==============================================================
            cfo_est = self.cfo_est_cfg['cfo_est_func'](
                in_frame[frame_idx][:preamble_sz], 
                *self.cfo_est_cfg['cfo_est_args']
            )
            cfo_est_report = cfo_est

            # compensate freq
            in_frame[frame_idx] *= np.exp(-2j*np.pi*cfo_est*np.arange(in_frame[frame_idx].size))
            
            # calculate residual freq offset in range (-0.5, 0.5)bin if desirable
            if self.use_cfo_cp_avg_est:
                cfo_cp_est = OFDM_OOT.ofdm_preambles.cp_average_est(
                    in_frame[frame_idx][preamble_sz:self.frame_sz], 
                    self.nfft, self.nguard, self.frame_sym_cnt
                )
                cfo_est_report += cfo_cp_est

                # compensate
                in_frame[frame_idx] *= np.exp(-2j*np.pi*cfo_cp_est*np.arange(in_frame[frame_idx].size))
            # ============================================================================================

            # sco estimation ============================================================================
            frame_sco_est = OFDM_OOT.ofdm_sco_sync.sco_estimate_frame(
                in_frame[frame_idx][preamble_sz:], 
                self.nfft, 
                self.nguard, 
                self.frame_sym_cnt, 
                self.pilot_idx
            )
            sco_est_report = frame_sco_est

            if self.compensate_sco:
                self.sco_est += frame_sco_est
                sco_est_report = self.sco_est
            # ============================================================================================

            if self.debug_report and time.time() - self.last_report_time > 0.5:
                print('preamble_sync: \n\tcfo_est = {:.2e}\n\tsco_est = {:.3e}'.format(cfo_est_report, sco_est_report))
                self.last_report_time = time.time()

            for ofdm_sym_idx in range(self.frame_sym_cnt):
                ofdm_sym_start_idx = preamble_sz + (self.nfft+self.nguard)*ofdm_sym_idx + self.nguard//2
                ofdm_sym_t = in_frame[frame_idx][ofdm_sym_start_idx: ofdm_sym_start_idx + self.nfft]

                ofdm_sym_f = np.fft.fft(ofdm_sym_t)
                # compensate roll caused by taking symbol from the middle of cyclic prefix
                ofdm_sym_f *= np.exp(2j*np.pi*np.arange(self.nfft)*(self.nguard - self.nguard//2)/self.nfft)

                out_ofdm_sym[frame_idx*self.frame_sym_cnt + ofdm_sym_idx] = ofdm_sym_f

        self.consume_each(frames_to_process)
        return frames_to_process*self.frame_sym_cnt
