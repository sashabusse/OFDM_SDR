#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 Vladislav.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class channel_est_hr(gr.sync_block):
    """
    docstring for block channel_est
    """
    def __init__(self,nfft,n_pilot_carriers,pilot_carriers_idx,pilot_vals,Nt,sc_spacing):
        gr.sync_block.__init__(self,
            name="channel_est_hr",
            in_sig=[(np.complex64,nfft) ],
            out_sig=[(np.complex64,Nt) ])
        
        self.nfft = nfft
        self.n_pilot_carriers = n_pilot_carriers
        self.pilot_carriers_idx = pilot_carriers_idx
        self.pilot_vals = pilot_vals
        
        self.Rxx = np.zeros([n_pilot_carriers,n_pilot_carriers],dtype=np.complex64)
        self.step_update = 0.1
        
        self.df = sc_spacing
        self.Nt = Nt
        self.IR = np.zeros(self.Nt,dtype=np.complex64)
        self.current_state = 0
        self.max_state = 10
        self.first_iter = True
        self.iter = 0


    def work(self, input_items, output_items):
        self.iter = self.iter+1
        self.current_state = self.current_state+1
        
        in0 = input_items[0]
        out = output_items[0]
        
        H_FD = in0[:,self.pilot_carriers_idx]*(np.conj(self.pilot_vals)/(self.pilot_vals*np.conj(self.pilot_vals)))
        #H_TD = np.fft.fft(H_FD,self.n_pilot_carriers)
        
        Nsymb = len(H_FD)
        for symb in range(0,Nsymb):
            #if self.first_iter:
            #    first_iter = False
            #    self.Rxx = np.transpose(np.matrix(H_FD[symb,:])) * np.matrix(np.conj(H_FD[symb,:]))
            #else:
            #    self.Rxx = self.Rxx*(1-self.step_update) + self.step_update*np.transpose(np.matrix(H_FD[symb,:])) * np.matrix(np.conj(H_FD[symb,:]))
        
            self.Rxx = self.Rxx*(self.iter-1)/self.iter + 1/(self.iter)*np.transpose(np.matrix(H_FD[symb,:])) * np.matrix(np.conj(H_FD[symb,:]))
        # update IR
        if self.current_state == self.max_state:
            self.current_state = 0
            rel_threshold = 0.01
            
            D,V = np.linalg.eig(self.Rxx)
            
            D = np.real(D) / np.max(np.real(D))
            Lp = sum(D>rel_threshold)
            
            print(Lp)
            #print(D)
            #print(np.shape(V))
            #print(np.shape(D))
            
            Q = V[:,-Lp:]
            P = Q * np.transpose(np.conj(Q))
            
            T = np.linspace(0,1000e-9,self.Nt)
            
            for i in range(0,self.Nt):
                v = np.transpose(np.exp((-1j*2*np.pi*self.df*T[i])*np.linspace(0,self.n_pilot_carriers,self.n_pilot_carriers)))
                
                self.IR[i] = 1/(np.linalg.norm(v*np.transpose(P),ord='fro')**2)
        
        out[:] = self.IR
        
        return len(output_items[0])