#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2022 @sashabusse.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

import numpy as np

def sco_estimate(sym1_f, sym2_f, sym_shift, pilot_idx):
    assert sym1_f.size == sym2_f.size
    R = sym1_f.conj()*sym2_f

    pilot_idx_symmetric = pilot_idx
    pilot_idx_symmetric[pilot_idx_symmetric > sym1_f.size]