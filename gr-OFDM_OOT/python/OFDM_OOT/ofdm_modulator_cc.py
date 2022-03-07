#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr


class ofdm_modulator_cc(gr.basic_block):
    """
    ofdm_modulator_cc:
    nfft - fft operation length
    data_carriers_idx - data carriers indices.      type: ndarray(int) or convertible via np.array(.., dtype=int)       watch some utility functions below
    pilot_carriers_idx - pilot carriers indices.    type: ndarray(int) or convertible via np.array(.., dtype=int)       watch some utility functions below
    pilot_carriers_vals - pilot carriers values.    type: complex or ndarray(complex)                                   watch some utility functions below
    (TODO: probably later lambda may be allowed for dynamic generation of idx/vals)
    n_guard - count of samples for prefix guard
    """
    def __init__(self, nfft=1024, data_carriers_idx=[], pilot_carriers_idx=[], pilot_carriers_vals=0, n_guard=0):
        gr.basic_block.__init__(self,
            name="ofdm_modulator_cc",
            in_sig=[np.complex64, ],
            out_sig=[np.complex64, ])

        self.nfft = nfft
        self.data_carriers_idx = np.array(data_carriers_idx, dtype=int)
        self.pilot_carriers_idx = np.array(pilot_carriers_idx, dtype=int)
        self.n_guard = n_guard

        if type(pilot_carriers_vals) is complex:
            self.pilot_carriers_vals = np.full((self.pilot_carriers_idx.size,), pilot_carriers_vals, dtype=complex)
        else:
            self.pilot_carriers_vals = np.array(pilot_carriers_vals)

        self.set_output_multiple(self.nfft + self.n_guard)

        # let it be here for debug purposes
        #print("ofdm_mod({}, {}, {}, {}, {})".format(nfft, data_carriers_idx, pilot_carriers_idx, pilot_carriers_vals, n_guard))

    def forecast(self, noutput_items, ninputs):
        # ninputs is the number of input connections
        # setup size of input_items[i] for work call
        # the required number of input items is returned
        #   in a list where each element represents the
        #   number of required items for each input

        ninput_items_required = [noutput_items//(self.nfft + self.n_guard) * self.data_carriers_idx.size] * ninputs

        # let it be here for debug purposes
        #print("forecast: nout={}, inputs={}, req_input={}".format(noutput_items, ninputs, ninput_items_required), flush=True)

        return ninput_items_required

    def general_work(self, input_items, output_items):
        # just run multiplexing for block of data

        # we have just 1 input and 1 but leave as generale decision
        ninput_items = min([len(items) for items in input_items])
        noutput_items = len(output_items[0])

        # let it be here for debug purposes
        #print("general_work: nin={}, nout={}".format(noutput_items, ninput_items), flush=True)

        sym_len = self.nfft + self.n_guard
        sym_data_cnt = self.data_carriers_idx.size

        sym_cnt_in = ninput_items//sym_data_cnt
        sym_cnt_out = noutput_items//sym_len
        sym_cnt = min(sym_cnt_in, sym_cnt_out)
        for i in range(sym_cnt):
            output_items[0][i*sym_len:(i+1)*sym_len] = self._multiplex(input_items[0][i*sym_data_cnt:(i+1)*sym_data_cnt])

        self.consume_each(sym_cnt*sym_data_cnt)
        return sym_len*sym_cnt

    def _multiplex(self, in_iq):
        # function for multiplexing of single OFDM symbol
        # forms ofdm spectrum and add guarding prefix

        spectrum = np.zeros(self.nfft, dtype=complex)
        spectrum[self.data_carriers_idx] = in_iq
        spectrum[self.pilot_carriers_idx] = self.pilot_carriers_vals

        ofdm_iq = np.fft.ifft(spectrum)
        out_iq = np.pad(ofdm_iq, ((self.n_guard, 0)), mode='wrap')
        return out_iq



def ofdm_data_pilot_idx_every_nth(data_carrier_cnt, n):
    # produce data_carrier_idx and pilot_carrier_idx
    # with every nth carrier being pilot
    # for simplicity data_carrier_cnt should be devisible by n-1
    #
    # data_carrier_cnt - count of data carriers (should be divisible by n-1). type: int or integral (will be floored if float)
    # n - type: int or integral (will be floored if float)

    data_carrier_cnt = int(data_carrier_cnt)
    n = int(n)

    assert data_carrier_cnt%(n-1)==0, 'data_carrier_cnt should be divisible by n-1, got data_carrier_cnt={}, n={}'.format(data_carrier_cnt, n)
    pilot_carrier_cnt = data_carrier_cnt//(n-1) + 1

    data_carrier_idx = np.empty((data_carrier_cnt,), dtype=int)
    pilot_carrier_idx = np.empty((pilot_carrier_cnt,), dtype=int)
    pilot_carrier_idx[0] = np.arange(1, 1+n*(pilot_carrier_cnt-1)+1, n, dtype=int)
    for i in range(pilot_carrier_cnt-1):
        data_carrier_idx[i*n:i*n + (n-1)] = np.arange(i*(n-1), (i+1)*(n-1), dtype=int)
    
    return data_carrier_idx, pilot_carrier_idx



