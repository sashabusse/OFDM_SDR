/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autocorr_cpp_cccc_impl.h"
#include <gnuradio/blocks/delay.h>
#include <gnuradio/io_signature.h>
#include <volk/volk.h>

namespace gr {
namespace OFDM_OOT {


autocorr_cpp_cccc::sptr autocorr_cpp_cccc::make(int sz, int dn)
{
    return gnuradio::make_block_sptr<autocorr_cpp_cccc_impl>(sz, dn);
}


autocorr_cpp_cccc_impl::autocorr_cpp_cccc_impl(int sz, int dn)
    : gr::block("autocorr_cpp_cccc",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(2, 2, sizeof(gr_complex))),
      sz(sz),
      dn(dn)
{
    this->set_history(dn + sz);
}


autocorr_cpp_cccc_impl::~autocorr_cpp_cccc_impl() {}

void autocorr_cpp_cccc_impl::forecast(int noutput_items,
                                      gr_vector_int& ninput_items_required)
{
    ninput_items_required[0] = dn + sz + noutput_items - 1;
}

int autocorr_cpp_cccc_impl::general_work(int noutput_items,
                                         gr_vector_int& ninput_items,
                                         gr_vector_const_void_star& input_items,
                                         gr_vector_void_star& output_items)
{
    auto in = static_cast<const gr_complex*>(input_items[0]);
    auto out_bypass = static_cast<gr_complex*>(output_items[0]);
    auto out_corr = static_cast<gr_complex*>(output_items[1]);

    int items_processed = std::min(ninput_items[0] - (dn + sz) + 1, noutput_items);

    // debug purpose
    // std::cout << "autocorr.work:" << std::endl;
    // std::cout << "\tninput_items = " << ninput_items[0] << std::endl
    //          << "\tnoutput_items = " << noutput_items << std::endl
    //          << "items_processed = " << items_processed << std::endl
    //          << std::flush;

    // bypass signal
    for (int i = 0; i < items_processed; i++) {
        out_bypass[i] = in[i];
    }

    // calculate correlations
    for (int i = 0; i < items_processed; i++) {
        out_corr[i] = correlation(in + i, in + i + this->dn, this->sz);
    }
    consume_each(items_processed);

    return items_processed;
}

gr_complex
autocorr_cpp_cccc_impl::correlation(const gr_complex* in1, const gr_complex* in2, int sz)
{

    // gr_complex s1s1;
    // gr_complex s2s2;
    gr_complex s1s2;
    volk_32fc_x2_conjugate_dot_prod_32fc(&s1s2, in1, in2, sz);
    // volk_32fc_x2_conjugate_dot_prod_32fc(&s1s1, in1, in1, sz);
    // volk_32fc_x2_conjugate_dot_prod_32fc(&s2s2, in2, in2, sz);

    // normalize correlation
    // float norm = sqrt(abs(s1s1) * abs(s2s2));
    // if (norm == 0) {
    //    s1s2 = 0;
    //} else {
    //    s1s2 = s1s2 / norm;
    //}

    return s1s2;
}


} /* namespace OFDM_OOT */
} /* namespace gr */
