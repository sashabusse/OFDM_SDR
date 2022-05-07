/* -*- c++ -*- */
/*
 * Copyright 2022 @sasha_busse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_CCC_H
#define INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_CCC_H

#include <gnuradio/OFDM_OOT/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace OFDM_OOT {

/*!
 * \brief <+description of block+>
 * \ingroup OFDM_OOT
 *
 */
class OFDM_OOT_API cfar_detector_cpp_ccc : virtual public gr::block
{
public:
    typedef std::shared_ptr<cfar_detector_cpp_ccc> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of OFDM_OOT::cfar_detector_cpp_ccc.
     *
     * To avoid accidental use of raw pointers, OFDM_OOT::cfar_detector_cpp_ccc's
     * constructor is in a private implementation
     * class. OFDM_OOT::cfar_detector_cpp_ccc::make is the public interface for
     * creating new instances.
     */
    static sptr make(int n_train = 100,
                     int n_gap = 1,
                     float p_false_alarm = 0.001,
                     int n_search_forward = 0,
                     int n_skip_after_detect = 0);
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_CCC_H */
