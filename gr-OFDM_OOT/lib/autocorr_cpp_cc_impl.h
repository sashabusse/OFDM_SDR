/* -*- c++ -*- */
/*
 * Copyright 2022 @sasha.busse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_AUTOCORR_CPP_CC_IMPL_H
#define INCLUDED_OFDM_OOT_AUTOCORR_CPP_CC_IMPL_H

#include <gnuradio/OFDM_OOT/autocorr_cpp_cc.h>
#include <gnuradio/gr_complex.h>

namespace gr {
namespace OFDM_OOT {

class autocorr_cpp_cc_impl : public autocorr_cpp_cc
{
private:
    int sz = 1;
    int dn = 1;
    bool normalize = false;
    bool conjugate_second_term = false;

    gr_complex s1s2;
    float s1s1;
    float s2s2;

public:
    autocorr_cpp_cc_impl(int sz, int dn, bool normalize, bool conjugate_second_term);
    ~autocorr_cpp_cc_impl();

    // Where all the action really happens
    void forecast(int noutput_items, gr_vector_int& ninput_items_required);

    int general_work(int noutput_items,
                     gr_vector_int& ninput_items,
                     gr_vector_const_void_star& input_items,
                     gr_vector_void_star& output_items);

    gr_complex process_next_correlation(const gr_complex* in_signal);
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_AUTOCORR_CPP_CC_IMPL_H */
