#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from multiprocessing.connection import Listener
from gnuradio import gr

class socket_source_c(gr.sync_block):
    """
    docstring for block socket_source_c
    """
    def __init__(self, ip='localhost', port=6000):
        gr.sync_block.__init__(self,
            name="socket_source_c",
            in_sig=None,
            out_sig=[np.complex64, ])
        
        self.address = (ip, port)
        self.listener = Listener(self.address)
        self.connection = self.listener.accept()
        self.data = np.array([], dtype=np.complex64)


    def work(self, input_items, output_items):
        if self.connection.poll():
            r_data = self.connection.recv()
            self.data = np.hstack((self.data, r_data))
        
        if self.data.size > 0:
            out_max = len(output_items[0])
            out_done = min(out_max, self.data.size)
            output_items[0][:out_done] = self.data[:out_done]
            self.data = self.data[out_done:]
            return out_done
        return 0
