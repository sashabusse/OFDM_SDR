/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_OFDM_MODULATOR_CPP_CC_IMPL_H
#define INCLUDED_OFDM_OOT_OFDM_MODULATOR_CPP_CC_IMPL_H

#include <gnuradio/OFDM_OOT/ofdm_modulator_cpp_cc.h>
#include <gnuradio/fft/fft.h>
#include <gnuradio/gr_complex.h>

namespace gr {
namespace OFDM_OOT {

/**
 * @brief implements ofdm multiplexing
 *
 * @param nfft
 * @param n_guard length of cyclic prefix
 * @param data_carriers_idx indices to use for data multiplexing
 * @param pilot_carriers_idx indices to use for pilot placement
 * @param pilot_carriers_vals values to use for pilots
 *
 */
class ofdm_modulator_cpp_cc_impl : public ofdm_modulator_cpp_cc
{
private:
    int nfft = 1024;
    int n_guard = 128;
    gr_vector_int data_carriers_idx = gr_vector_int();
    gr_vector_int pilot_carriers_idx = gr_vector_int();
    std::vector<gr_complex> pilot_carriers_vals = std::vector<gr_complex>();

    std::shared_ptr<gr::fft::fft_complex_rev> fft_sptr;

public:
    ofdm_modulator_cpp_cc_impl(
        int nfft = 1024,
        gr_vector_int data_carriers_idx = gr_vector_int(),
        gr_vector_int pilot_carriers_idx = gr_vector_int(),
        std::vector<gr_complex> pilot_carriers_vals = std::vector<gr_complex>(),
        int n_guard = 128);

    ~ofdm_modulator_cpp_cc_impl();

    // Where all the action really happens
    void forecast(int noutput_items, gr_vector_int& ninput_items_required);

    int general_work(int noutput_items,
                     gr_vector_int& ninput_items,
                     gr_vector_const_void_star& input_items,
                     gr_vector_void_star& output_items);

private:
    // multiplex single ofdm symbol
    void multiplex(const gr_complex* in_iq, gr_complex* out);
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_OFDM_MODULATOR_CPP_CC_IMPL_H */
