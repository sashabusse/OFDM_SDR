/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_OFDM_CORR_SYNC_CPP_CC_IMPL_H
#define INCLUDED_OFDM_OOT_OFDM_CORR_SYNC_CPP_CC_IMPL_H

#include <gnuradio/OFDM_OOT/ofdm_corr_sync_cpp_cc.h>
#include <gnuradio/gr_complex.h>

namespace gr {
namespace OFDM_OOT {

/**
 * @brief implements cyclic preffix detection and frequency offset estimation
 *  - detects cyclic prefix
 *  - estimates mid-point of cyclic prefix
 *  - estimates frequency offset
 *
 *
 *
 * @param nfft
 * @param n_guard - cyclic prefix length
 * @param corr_sz - length of window for correlation calculation
 * @param sync_corr_lvl - minimal level of correlation  for cyclic prefix detection and
 * freq_offset estimation
 *
 * circular buffer is used to store previous results
 * @param corr_buf_st - correlation circular buffer start index
 * @param corr_buf - correlation circular buffer
 * @param corr_delay - delay incured by usage of circular buffer
 *
 */
class ofdm_corr_sync_cpp_cc_impl : public ofdm_corr_sync_cpp_cc
{
private:
    int nfft = 1024;
    int n_guard = 128;
    int corr_sz = 64;
    float sync_corr_lvl = 0.8;

    int corr_buf_st = 0;
    std::vector<gr_complex> corr_buf;

    int corr_delay = 0;

public:
    ofdm_corr_sync_cpp_cc_impl(int nfft, int n_guard, int corr_sz);
    ~ofdm_corr_sync_cpp_cc_impl();

    // Where all the action really happens
    void forecast(int noutput_items, gr_vector_int& ninput_items_required);

    int general_work(int noutput_items,
                     gr_vector_int& ninput_items,
                     gr_vector_const_void_star& input_items,
                     gr_vector_void_star& output_items);

private:
    // process next point of correlation
    void process_next_correlation(const gr_complex* in, gr_complex* out, int out_ind);

    // estimate correlation between [in:in+corr_sz] and [in+nfft:in+nfft+corr_sz]
    gr_complex correlation(const gr_complex* in);

    // returns expected lenght of flat peak of correlation
    inline int peak_len() { return this->n_guard - this->corr_sz + 1; };
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_OFDM_CORR_SYNC_CPP_CC_IMPL_H */
