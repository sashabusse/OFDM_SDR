/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_AUTOCORR_CPP_CCCC_IMPL_H
#define INCLUDED_OFDM_OOT_AUTOCORR_CPP_CCCC_IMPL_H

#include <gnuradio/OFDM_OOT/autocorr_cpp_cccc.h>

namespace gr {
namespace OFDM_OOT {

class autocorr_cpp_cccc_impl : public autocorr_cpp_cccc
{
private:
    int sz = 1;
    int dn = 1;
    bool normalize = false;


public:
    autocorr_cpp_cccc_impl(int sz, int dn, bool normalize);
    ~autocorr_cpp_cccc_impl();

    // Where all the action really happens
    void forecast(int noutput_items, gr_vector_int& ninput_items_required);

    int general_work(int noutput_items,
                     gr_vector_int& ninput_items,
                     gr_vector_const_void_star& input_items,
                     gr_vector_void_star& output_items);

private:
    gr_complex correlation(const gr_complex* in1, const gr_complex* in2, int sz);
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_AUTOCORR_CPP_CCCC_IMPL_H */
