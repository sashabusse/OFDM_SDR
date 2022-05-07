/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_OFDM_CORR_SYNC_CPP_CC_H
#define INCLUDED_OFDM_OOT_OFDM_CORR_SYNC_CPP_CC_H

#include <gnuradio/OFDM_OOT/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace OFDM_OOT {

/*!
 * \brief <+description of block+>
 * \ingroup OFDM_OOT
 *
 */
class OFDM_OOT_API ofdm_corr_sync_cpp_cc : virtual public gr::block
{
public:
    typedef std::shared_ptr<ofdm_corr_sync_cpp_cc> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of OFDM_OOT::ofdm_corr_sync_cpp_cc.
     *
     * To avoid accidental use of raw pointers, OFDM_OOT::ofdm_corr_sync_cpp_cc's
     * constructor is in a private implementation
     * class. OFDM_OOT::ofdm_corr_sync_cpp_cc::make is the public interface for
     * creating new instances.
     */
    static sptr
    make(int nfft = 1024, int n_guard = 128, int corr_sz = 64, float sync_corr_lvl = 0.8);
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_OFDM_CORR_SYNC_CPP_CC_H */
