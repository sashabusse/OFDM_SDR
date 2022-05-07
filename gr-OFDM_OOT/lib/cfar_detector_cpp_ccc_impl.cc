/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "cfar_detector_cpp_ccc_impl.h"
#include <gnuradio/io_signature.h>

namespace gr {
namespace OFDM_OOT {


cfar_detector_cpp_ccc::sptr cfar_detector_cpp_ccc::make(int n_train,
                                                        int n_gap,
                                                        float p_false_alarm,
                                                        int n_search_forward,
                                                        int n_skip_after_detect)
{
    return gnuradio::make_block_sptr<cfar_detector_cpp_ccc_impl>(
        n_train, n_gap, p_false_alarm, n_search_forward, n_skip_after_detect);
}


cfar_detector_cpp_ccc_impl::cfar_detector_cpp_ccc_impl(int n_train,
                                                       int n_gap,
                                                       float p_false_alarm,
                                                       int n_search_forward,
                                                       int n_skip_after_detect)
    : gr::block("cfar_detector_cpp_ccc",
                gr::io_signature::make(2, 2, sizeof(gr_complex)),
                gr::io_signature::make(2, 2, sizeof(gr_complex))),
      n_train(n_train),
      n_gap(n_gap),
      n_search_forward(n_search_forward),
      n_skip_after_detect(n_skip_after_detect),
      p_false_alarm(p_false_alarm),
      noise_power_est(0)
{
    assert(n_search_forward <= n_gap + n_train);
    this->set_history(1 + 2 * (this->n_train + this->n_gap));

    int N = 2 * n_train;
    this->treshold_factor = N * (std::pow(this->p_false_alarm, -1. / N) - 1);

    // std::cout << "cfar created: alpha = " << this->treshold_factor << std::endl
    //           << std::flush;
}


cfar_detector_cpp_ccc_impl::~cfar_detector_cpp_ccc_impl() {}

void cfar_detector_cpp_ccc_impl::forecast(int noutput_items,
                                          gr_vector_int& ninput_items_required)
{
    ninput_items_required[0] = this->history() + noutput_items - 1;
    ninput_items_required[1] = this->history() + noutput_items - 1;
}

int cfar_detector_cpp_ccc_impl::general_work(int noutput_items,
                                             gr_vector_int& ninput_items,
                                             gr_vector_const_void_star& input_items,
                                             gr_vector_void_star& output_items)
{
    auto in_signal = static_cast<const gr_complex*>(input_items[0]);
    auto in_corr = static_cast<const gr_complex*>(input_items[1]);
    auto out_signal = static_cast<gr_complex*>(output_items[0]);
    auto out_corr = static_cast<gr_complex*>(output_items[1]);

    int in_available = std::min(ninput_items[0], ninput_items[1]) - (this->history() - 1);
    int items_processed = std::min(noutput_items, in_available);

    for (int i = 0; i < items_processed; i++) {
        out_signal[i] = in_signal[i + this->n_train + this->n_gap];
        out_corr[i] = in_corr[i + this->n_train + this->n_gap];
    }

    // skip some first elements for accurate noise estimation
    static int skip_left = 2 * (this->n_gap + this->n_train) + 1;
    for (int i = 0; i < items_processed; i++) {
        this->process_next(in_corr + i, skip_left > 0, i);
        skip_left = std::max(0, skip_left - 1);
    }

    consume_each(items_processed);

    return items_processed;
}


void cfar_detector_cpp_ccc_impl::process_next(const gr_complex* in_corr,
                                              bool dont_tag,
                                              int tg_idx)
{
    // add new taps
    this->noise_power_est +=
        (std::abs(in_corr[this->n_train - 1]) +
         std::abs(in_corr[2 * (this->n_train + this->n_gap) + 1 - 1])) /
        (2 * this->n_train);

    float current_est = this->noise_power_est;

    // substract taps that shouldn't be for the next step
    this->noise_power_est -=
        (std::abs(in_corr[0]) + std::abs(in_corr[this->n_train + 2 * this->n_gap + 1])) /
        (2 * this->n_train);


    // tag streams
    // spacing to tag peak only once
    static int skip_left = 0;
    if ((!dont_tag) && (skip_left == 0)) {
        float treshold = this->treshold_factor * current_est;
        int cut_idx = this->n_train + this->n_gap;
        gr_complex cut = in_corr[cut_idx];

        if (std::abs(cut) > treshold) {
            // search for maximal corr value
            int max_idx = 0;
            for (int i = 1; i < this->n_search_forward; i++) {
                if (std::abs(in_corr[cut_idx + i]) >
                    std::abs(in_corr[cut_idx + max_idx])) {
                    max_idx = i;
                }
            }
            skip_left = max_idx + this->n_skip_after_detect;
            float corr_angle = -std::arg(in_corr[cut_idx + max_idx]);
            this->add_item_tag(0,
                               this->nitems_written(0) + tg_idx + max_idx,
                               pmt::intern("cfar"),
                               pmt::from_float(corr_angle));

            this->add_item_tag(1,
                               this->nitems_written(1) + tg_idx + max_idx,
                               pmt::intern("cfar"),
                               pmt::from_float(corr_angle));
        }
    }
    skip_left = std::max(0, skip_left - 1);
}

} /* namespace OFDM_OOT */
} /* namespace gr */