/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "ofdm_modulator_cpp_cc_impl.h"
#include <gnuradio/io_signature.h>


// uncomment to enable debug outputs
//#define OFDM_MODULATOR_CPP_DEBUG_OUT


namespace gr {
namespace OFDM_OOT {

using input_type = gr_complex;
using output_type = gr_complex;

ofdm_modulator_cpp_cc::sptr ofdm_modulator_cpp_cc::make(int nfft,
                                                        gr_vector_int data_carriers_idx,
                                                        gr_vector_int pilot_carriers_idx,
                                                        std::vector<gr_complex> pilot_carriers_vals,
                                                        int n_guard)
{
    return gnuradio::make_block_sptr<ofdm_modulator_cpp_cc_impl>(
        nfft, data_carriers_idx, pilot_carriers_idx, pilot_carriers_vals);
}


/*
 * The private constructor
 */
ofdm_modulator_cpp_cc_impl::ofdm_modulator_cpp_cc_impl(int nfft,
                                                       gr_vector_int data_carriers_idx,
                                                       gr_vector_int pilot_carriers_idx,
                                                       std::vector<gr_complex> pilot_carriers_vals,
                                                       int n_guard)
    : gr::block("ofdm_modulator_cpp_cc",
                gr::io_signature::make(1, 1, sizeof(input_type)),
                gr::io_signature::make(1, 1, sizeof(output_type))),
      nfft(nfft),
      n_guard(n_guard),
      data_carriers_idx(data_carriers_idx),
      pilot_carriers_idx(pilot_carriers_idx),
      pilot_carriers_vals(pilot_carriers_vals)
{
#ifdef OFDM_MODULATOR_CPP_DEBUG_OUT
    std::cout << "ofdm_modulator_cpp_cc.constructor(nfft=" << this->nfft;
    std::cout << ", n_gurad=" << this->n_guard << ", ...)" << std::endl << std::flush;
#endif

    this->fft_sptr = std::make_shared<gr::fft::fft_complex_rev>(this->nfft, 1);
    set_output_multiple(this->nfft + this->n_guard);
}

/*
 * Our virtual destructor.
 */
ofdm_modulator_cpp_cc_impl::~ofdm_modulator_cpp_cc_impl() {}

void ofdm_modulator_cpp_cc_impl::forecast(int noutput_items,
                                          gr_vector_int& ninput_items_required)
{
    ninput_items_required[0] =
        (noutput_items / (nfft + n_guard)) * data_carriers_idx.size();

#ifdef OFDM_MODULATOR_CPP_DEBUG_OUT
    std::cout << "ofdm_modulator_cpp_cc.forecast(noutput_items=" << noutput_items; 
    std::cout << ", ninput_items_required[0]=" << ninput_items_required[0] << ")" << std::endl << std::flush;
#endif
}

int ofdm_modulator_cpp_cc_impl::general_work(int noutput_items,
                                             gr_vector_int& ninput_items,
                                             gr_vector_const_void_star& input_items,
                                             gr_vector_void_star& output_items)
{
    auto in = static_cast<const input_type*>(input_items[0]);
    auto out = static_cast<output_type*>(output_items[0]);

    int sym_len = nfft + n_guard;
    int sym_data_cnt = data_carriers_idx.size();

    // calculate maximal number of ofdm symbols we can produced from ninputs to noutputs
    int sym_cnt_in = ninput_items[0] / sym_data_cnt;
    int sym_cnt_out = noutput_items / sym_len;
    int sym_cnt = std::min(sym_cnt_in, sym_cnt_out);

    
#ifdef OFDM_MODULATOR_CPP_DEBUG_OUT
    std::cout << "ofdm_modulator_cpp_cc.general_work(noutput_items=" << noutput_items; 
    std::cout << ", ninput_items[0]=" << ninput_items[0]; 
    std::cout << ", sym_cnt=" << sym_cnt << ")" << std::endl << std::flush;
#endif

    // multiplex data and pilots to ofdm symbols
    for (int i = 0; i < sym_cnt; i++) {
        multiplex(in + sym_data_cnt * i, out + i * sym_len);
    }

    // Tell runtime system how many input items we consumed on
    // each input stream.
    consume_each(sym_cnt * sym_data_cnt);

    // Tell runtime system how many output items we produced.
    return sym_len * sym_cnt;
}

/**
 * @brief function for multiplexing of single OFDM symbol
 *          forms ofdm spectrum and add guarding prefix
 *
 * @param in_iq - pointer to the start of input data
 * @param out - pointer to the start of region to place output data
 */

void ofdm_modulator_cpp_cc_impl::multiplex(const gr_complex* in_iq, gr_complex* out)
{
    gr_complex* fft_in = fft_sptr->get_inbuf();
    
    // fill in spectrum

    std::fill(fft_in, fft_in+nfft, gr_complex(0, 0));
    for(size_t i=0;i<data_carriers_idx.size();i++)
    {
        fft_in[data_carriers_idx[i]] = in_iq[i];
    }
    for(size_t i=0;i<pilot_carriers_idx.size();i++)
    {
        fft_in[pilot_carriers_idx[i]] = pilot_carriers_vals[i];
    }

    // compute ifft to out
    fft_sptr->execute();

    std::copy(fft_sptr->get_outbuf(), fft_sptr->get_outbuf() + nfft, out + n_guard);
    // fft is implemented without 1/N probably may be ommited
    for(int i=0;i<nfft;i++)
    {
        out[i+n_guard]/=nfft;
    }

    // add guard
    std::copy(out + nfft, out + nfft + n_guard, out);
}

} /* namespace OFDM_OOT */
} /* namespace gr */
