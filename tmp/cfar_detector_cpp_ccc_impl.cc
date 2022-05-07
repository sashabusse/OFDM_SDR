/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "cfar_detector_cpp_ccc_impl.h"
#include <gnuradio/io_signature.h>

#define _USE_MATH_DEFINES
#include <math.h>

namespace gr {
namespace OFDM_OOT {


cfar_detector_cpp_ccc::sptr cfar_detector_cpp_ccc::make(gr_vector_int train_regions,
                                                        float p_false_alarm,
                                                        int n_search_forward,
                                                        int n_skip_after_detect)
{
    return gnuradio::make_block_sptr<cfar_detector_cpp_ccc_impl>(
        train_regions, p_false_alarm, n_search_forward, n_skip_after_detect);
}


cfar_detector_cpp_ccc_impl::cfar_detector_cpp_ccc_impl(gr_vector_int train_regions,
                                                       float p_false_alarm,
                                                       int n_search_forward,
                                                       int n_skip_after_detect)
    : gr::block("cfar_detector_cpp_ccc",
                gr::io_signature::make(2, 2, sizeof(gr_complex)),
                gr::io_signature::make(2, 2, sizeof(gr_complex))),
      train_regions(train_regions),
      p_false_alarm(p_false_alarm),
      n_search_forward(n_search_forward),
      n_skip_after_detect(n_skip_after_detect),
      noise_power_est(0)
{
    assert((this->train_regions.size() > 0) && ((this->train_regions.size() % 2) == 0));
    for (size_t i = 0; i < this->train_regions.size(); i += 2) {
        assert(this->train_regions[i + 1] > this->train_regions[i]);
    }

    // precalculate number of train cell for later averaging
    this->train_len = 0;
    for (size_t i = 0; i < this->train_regions.size(); i += 2) {
        this->train_len += this->train_regions[i + 1] - this->train_regions[i];
    }

    // calculate needed history
    assert(n_search_forward >= 0);
    int max_idx_needed = n_search_forward;
    int min_idx_needed = 0;
    for (size_t i = 0; i < this->train_regions.size(); i += 2) {
        max_idx_needed = std::max(max_idx_needed,
                                  this->train_regions[i + 1] - 1); // -1 cause intervals
        min_idx_needed = std::min(min_idx_needed, this->train_regions[i]);
    }
    this->set_history(max_idx_needed - min_idx_needed + 1);
    // skip data cause first taps are zero which can lead to false alarm
    this->skip_left = this->history();

    // positions of regions and cut in relation to first sample
    this->cut_rel_pos = -min_idx_needed;
    this->train_regions_rel_pos = this->train_regions;
    for (size_t i = 0; i < this->train_regions.size(); i += 1) {
        this->train_regions_rel_pos[i] -= min_idx_needed;
    }

    // treshold factor
    int N = 0;
    for (size_t i = 0; i < this->train_regions.size(); i += 2) {
        N += this->train_regions[i + 1] - this->train_regions[i];
    }
    this->treshold_factor = N * (std::pow(this->p_false_alarm, -1. / N) - 1);
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
        out_signal[i] = in_signal[i + this->cut_rel_pos];
        out_corr[i] = in_corr[i + this->cut_rel_pos];
    }

    for (int i = 0; i < items_processed; i++) {
        this->process_next(in_corr + i, i);
    }

    consume_each(items_processed);

    return items_processed;
}


void cfar_detector_cpp_ccc_impl::process_next(const gr_complex* in_corr, int tg_idx)
{
    // add new taps
    for (size_t i = 0; i < this->train_regions_rel_pos.size(); i += 2) {
        this->noise_power_est +=
            std::abs(in_corr[this->train_regions_rel_pos[i + 1] - 1]) / this->train_len;
    }

    float current_noise_power_est = this->noise_power_est;

    // substract taps that shouldn't be for the next step
    for (size_t i = 0; i < this->train_regions_rel_pos.size(); i += 2) {
        this->noise_power_est -=
            std::abs(in_corr[this->train_regions_rel_pos[i]]) / this->train_len;
    }

    // tag streams
    // spacing to tag peak only once
    if (this->skip_left == 0) {
        float treshold = this->treshold_factor * current_noise_power_est;
        gr_complex cut = in_corr[this->cut_rel_pos];

        if (std::abs(cut) > treshold) {
            // search for maximal corr value (idx relative to cut)
            // int max_idx = std::distance(
            //    in_corr,
            //    std::max_element(in_corr + this->cut_rel_pos,
            //                     in_corr + this->cut_rel_pos + this->n_search_forward,
            //                     [](gr_complex a, gr_complex b) {
            //                         return std::abs(a) < std::abs(b);
            //                     }));
            int max_idx = 0;
            for (int i = 0; i < this->n_search_forward; i++) {
                if (std::abs(in_corr[this->cut_rel_pos + i]) >
                    std::abs(in_corr[this->cut_rel_pos + max_idx])) {
                    max_idx = i;
                }
            }

            this->skip_left = max_idx + this->n_skip_after_detect;

            float corr_arg = -std::arg(in_corr[this->cut_rel_pos + max_idx]);
            this->add_item_tag(0,
                               this->nitems_written(0) + tg_idx + max_idx,
                               pmt::intern("cfar"),
                               pmt::from_float(corr_arg));

            this->add_item_tag(1,
                               this->nitems_written(1) + tg_idx + max_idx,
                               pmt::intern("cfar"),
                               pmt::from_float(corr_arg));
        }
    }
    this->skip_left = std::max(0, this->skip_left - 1);
}

} /* namespace OFDM_OOT */
} /* namespace gr */