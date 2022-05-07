/* -*- c++ -*- */
/*
 * Copyright 2022 @sasha.busse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_AUTOCORR_CPP_CC_H
#define INCLUDED_OFDM_OOT_AUTOCORR_CPP_CC_H

#include <gnuradio/OFDM_OOT/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace OFDM_OOT {

/*!
 * \brief <+description of block+>
 * \ingroup OFDM_OOT
 *
 */
class OFDM_OOT_API autocorr_cpp_cc : virtual public gr::block
{
public:
    typedef std::shared_ptr<autocorr_cpp_cc> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of OFDM_OOT::autocorr_cpp_cc.
     *
     * To avoid accidental use of raw pointers, OFDM_OOT::autocorr_cpp_cc's
     * constructor is in a private implementation
     * class. OFDM_OOT::autocorr_cpp_cc::make is the public interface for
     * creating new instances.
     */
    static sptr make(int sz = 48,
                     int dn = 32,
                     bool normalize = false,
                     bool conjugate_second_term = false);
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_AUTOCORR_CPP_CC_H */
