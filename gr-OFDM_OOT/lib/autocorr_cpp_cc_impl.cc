/* -*- c++ -*- */
/*
 * Copyright 2022 @sasha.busse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autocorr_cpp_cc_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace OFDM_OOT {

autocorr_cpp_cc::sptr
autocorr_cpp_cc::make(int sz, int dn, bool normalize, bool conjugate_second_term)
{
    return gnuradio::make_block_sptr<autocorr_cpp_cc_impl>(
        sz, dn, normalize, conjugate_second_term);
}


/*
 * The private constructor
 */
autocorr_cpp_cc_impl::autocorr_cpp_cc_impl(int sz,
                                           int dn,
                                           bool normalize,
                                           bool conjugate_second_term)
    : gr::block("autocorr_cpp_cc",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(2, 2, sizeof(gr_complex))),
      sz(sz),
      dn(dn),
      normalize(normalize),
      conjugate_second_term(conjugate_second_term),
      s1s2(0),
      s1s1(0),
      s2s2(0)
{
    this->set_history(this->dn + this->sz);
}

/*
 * Our virtual destructor.
 */
autocorr_cpp_cc_impl::~autocorr_cpp_cc_impl() {}

void autocorr_cpp_cc_impl::forecast(int noutput_items,
                                    gr_vector_int& ninput_items_required)
{
    ninput_items_required[0] = dn + sz + noutput_items - 1;
}

int autocorr_cpp_cc_impl::general_work(int noutput_items,
                                       gr_vector_int& ninput_items,
                                       gr_vector_const_void_star& input_items,
                                       gr_vector_void_star& output_items)
{
    auto in_signal = static_cast<const gr_complex*>(input_items[0]);
    auto out_signal = static_cast<gr_complex*>(output_items[0]);
    auto out_corr = static_cast<gr_complex*>(output_items[1]);

    int items_processed = std::min(ninput_items[0] - (dn + sz) + 1, noutput_items);

    // bypass signal
    for (int i = 0; i < items_processed; i++) {
        out_signal[i] = in_signal[i];
    }

    // calculate correlations
    for (int i = 0; i < items_processed; i++) {
        out_corr[i] = this->process_next_correlation(in_signal + i);
    }
    consume_each(items_processed);

    return items_processed;
}

gr_complex autocorr_cpp_cc_impl::process_next_correlation(const gr_complex* in_signal)
{
    // add new tap
    gr_complex s1_new = in_signal[this->sz - 1];
    gr_complex s2_new = in_signal[this->dn + this->sz - 1];
    if (this->conjugate_second_term) {
        this->s1s2 += s1_new * std::conj(s2_new);
    } else {
        this->s1s2 += std::conj(s1_new) * s2_new;
    }

    gr_complex result = this->s1s2;

    if (this->normalize) {
        this->s1s1 += std::abs(s1_new) * std::abs(s1_new);
        this->s2s2 += std::abs(s2_new) * std::abs(s2_new);

        result /= std::sqrt(this->s1s1 * this->s2s2);
    }

    // substract taps which are not needed for later calculations
    gr_complex s1_old = in_signal[0];
    gr_complex s2_old = in_signal[this->dn];
    if (this->conjugate_second_term) {
        this->s1s2 -= s1_old * std::conj(s2_old);
    } else {
        this->s1s2 -= std::conj(s1_old) * s2_old;
    }

    if (this->normalize) {
        this->s1s1 -= std::abs(s1_old) * std::abs(s1_old);
        this->s2s2 -= std::abs(s2_old) * std::abs(s2_old);
    }

    return result;
}

} /* namespace OFDM_OOT */
} /* namespace gr */
