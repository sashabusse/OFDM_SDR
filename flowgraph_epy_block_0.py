"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class decimate_vec(gr.sync_block):

    def __init__(self, vlen_in=4*1024, n=4):
        gr.sync_block.__init__(
            self,
            name='decimate vec',
            in_sig=[(np.complex64, vlen_in)],
            out_sig=[(np.complex64, vlen_in//n)]
        )
        self.vlen_in = vlen_in
        self.n = n

    def work(self, input_items, output_items):
        output_items[0][:, :] = input_items[0][:, np.arange(0, self.vlen_in//self.n)]
        return len(output_items[0])
