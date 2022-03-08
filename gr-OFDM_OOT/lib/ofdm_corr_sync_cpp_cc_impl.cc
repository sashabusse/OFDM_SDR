/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "ofdm_corr_sync_cpp_cc_impl.h"
#include <gnuradio/io_signature.h>
#include <volk/volk.h>

#define _USE_MATH_DEFINES
#include <math.h>

namespace gr {
namespace OFDM_OOT {

ofdm_corr_sync_cpp_cc::sptr
ofdm_corr_sync_cpp_cc::make(int nfft, int n_guard, int corr_sz)
{
    return gnuradio::make_block_sptr<ofdm_corr_sync_cpp_cc_impl>(nfft, n_guard, corr_sz);
}


/*
 * The private constructor
 */
ofdm_corr_sync_cpp_cc_impl::ofdm_corr_sync_cpp_cc_impl(int nfft, int n_guard, int corr_sz)
    : gr::block("ofdm_corr_sync_cpp_cc",
                gr::io_signature::make(1, 1, sizeof(gr_complex)),
                gr::io_signature::make(2, 2, sizeof(gr_complex))),
      nfft(nfft),
      n_guard(n_guard),
      corr_sz(corr_sz)
{
    // initialize buffer for correlation peak detection
    this->corr_buf.resize(2 * peak_len());
    std::fill(this->corr_buf.begin(), this->corr_buf.end(), gr_complex(0, 0));
    this->corr_buf_st = 0;

    // let's delay correlation to aproximately mid of our buffer
    this->corr_delay = peak_len();

    // nfft+guard for estimation; buf_sz - 1 previous input to form syncronized output of
    // bypass input
    this->set_history(this->nfft + this->n_guard + (this->corr_buf.size() - 1));
}

/*
 * Our virtual destructor.
 */
ofdm_corr_sync_cpp_cc_impl::~ofdm_corr_sync_cpp_cc_impl() {}

void ofdm_corr_sync_cpp_cc_impl::forecast(int noutput_items,
                                          gr_vector_int& ninput_items_required)
{
    ninput_items_required[0] = noutput_items + this->history() - 1;
}

int ofdm_corr_sync_cpp_cc_impl::general_work(int noutput_items,
                                             gr_vector_int& ninput_items,
                                             gr_vector_const_void_star& input_items,
                                             gr_vector_void_star& output_items)
{
    auto in = static_cast<const gr_complex*>(input_items[0]);
    auto out_bypass = static_cast<gr_complex*>(output_items[0]);
    auto out_corr = static_cast<gr_complex*>(output_items[1]);

    // calculate maximal number of items we can process
    int processed_items =
        std::min(noutput_items, ninput_items[0] - ((int)(this->history()) - 1));

    // process correlation
    for (int i = 0; i < processed_items; i++) {
        this->process_next_correlation(in + i + (corr_buf.size() - 1), out_corr + i, i);
    }

    // just bypass with given delay
    for (int i = 0; i < processed_items; i++) {
        out_bypass[i] = in[corr_buf.size() - 1 - this->corr_delay + i];
    }

    // Tell runtime system how many input items we consumed on
    // each input stream.
    consume_each(processed_items);

    // Tell runtime system how many output items we produced.
    return processed_items;
}

/**
 * @brief process single correlation point
 *  - detects peak of correlation
 *  - estimates mid of cyclic prefix
 *  - estimates freq_offset
 *  - adds tag to bypass output tag('ofdm_corr_sync', freq_offset)
 *    this tag should be used to form vectors of ofdm symbols and freq_offset elimination
 *    (ofdm_corr_sync_demultiplex module)
 *
 * @param in - pointer to the start of the input
 * @param out - pointer to output point
 * @param out_ind - index of out point is processing on this call of general work
 * (needed to calculate tag index probably can be replaced with call of produce(...) in
 * general work)
 */
void ofdm_corr_sync_cpp_cc_impl::process_next_correlation(const gr_complex* in,
                                                          gr_complex* out,
                                                          int out_ind)
{
    // update circular buffer
    this->corr_buf[corr_buf_st] = this->correlation(in);
    corr_buf_st = (corr_buf_st + 1) % corr_buf.size();

    // provide element for output
    size_t out_rel_pos = corr_buf.size() - 1 - this->corr_delay;
    *out = this->corr_buf[(corr_buf_st + out_rel_pos) % corr_buf.size()];

    // counter to prevent several sync tags in raw
    static int no_sync_counter = 0;
    no_sync_counter = std::max(no_sync_counter - 1, 0);

    if (no_sync_counter == 0) {
        // peak detector via averrage corr abs
        // (trying to detect when peak is close to the mid of circular buffer)
        float avg_corr = 0;
        for (int i = std::ceil(peak_len() / 2);
             i < std::ceil(peak_len() / 2) + peak_len();
             i++) {
            avg_corr +=
                std::abs(corr_buf[(corr_buf_st + i) % corr_buf.size()]) / peak_len();
        }

        if (avg_corr >= this->sync_corr_lvl) { // peak detected
            // calculate weight average of freq offset
            // and estimate middle position more precisely
            float tot_weight = 0;
            float freq_offset = 0;
            float mid_position = 0;
            for (size_t rel_ind = 0; rel_ind < corr_buf.size(); rel_ind++) {
                size_t abs_ind = (corr_buf_st + rel_ind) % corr_buf.size();
                if (std::abs(corr_buf[abs_ind]) > this->sync_corr_lvl) {
                    float weight =
                        std::abs(corr_buf[abs_ind]) * std::abs(corr_buf[abs_ind]);
                    tot_weight += weight;

                    freq_offset +=
                        (-std::arg(corr_buf[abs_ind]) / (2 * M_PI * this->nfft)) * weight;

                    mid_position += rel_ind * weight;
                }
            }
            freq_offset /= tot_weight;
            mid_position /= tot_weight;

            // add tags
            this->add_item_tag(1,
                               this->nitems_written(1) + out_ind +
                                   (static_cast<int>(mid_position) - out_rel_pos),
                               pmt::intern("ofdm_corr_sync"),
                               pmt::from_float(freq_offset));

            this->add_item_tag(0,
                               this->nitems_written(0) + out_ind +
                                   (static_cast<int>(mid_position) - out_rel_pos) +
                                   corr_sz / 2,
                               pmt::intern("ofdm_corr_sync"),
                               pmt::from_float(freq_offset));

            // update no sync
            no_sync_counter = n_guard;
        }
    }
}

gr_complex ofdm_corr_sync_cpp_cc_impl::correlation(const gr_complex* in)
{
    auto s1 = in;
    auto s2 = in + nfft;

    gr_complex s1s1;
    gr_complex s2s2;
    gr_complex s1s2;
    volk_32fc_x2_conjugate_dot_prod_32fc(&s1s2, s1, s2, corr_sz);
    volk_32fc_x2_conjugate_dot_prod_32fc(&s1s1, s1, s1, corr_sz);
    volk_32fc_x2_conjugate_dot_prod_32fc(&s2s2, s2, s2, corr_sz);

    // normalize correlation
    gr_complex norm = sqrt(s1s1 * s2s2);
    if (std::abs(norm) == 0) {
        s1s2 = 0;
    } else {
        s1s2 = s1s2 / norm;
    }

    return s1s2;
}


} /* namespace OFDM_OOT */
} /* namespace gr */
