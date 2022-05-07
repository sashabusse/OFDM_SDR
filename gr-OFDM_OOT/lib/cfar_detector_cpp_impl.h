/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_IMPL_H
#define INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_IMPL_H

#include <gnuradio/OFDM_OOT/cfar_detector_cpp.h>
#include <gnuradio/gr_complex.h>

namespace gr {
namespace OFDM_OOT {

class cfar_detector_cpp_impl : public cfar_detector_cpp
{
private:
    gr_vector_int train_regions;
    float p_false_alarm;
    int n_search_forward;
    int n_skip_after_detect;

    int skip_left;

    float noise_power_est;
    float treshold_factor;

    int cut_rel_pos;
    gr_vector_int train_regions_rel_pos;
    int train_len;

public:
    cfar_detector_cpp_impl(gr_vector_int train_regions,
                           float p_false_alarm,
                           int n_search_forward,
                           int n_skip_after_detect);
    ~cfar_detector_cpp_impl();

    // Where all the action really happens
    void forecast(int noutput_items, gr_vector_int& ninput_items_required);

    int general_work(int noutput_items,
                     gr_vector_int& ninput_items,
                     gr_vector_const_void_star& input_items,
                     gr_vector_void_star& output_items);

private:
    void process_next(const gr_complex* in_corr, int tg_idx);
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_IMPL_H */
