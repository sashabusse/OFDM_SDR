/* -*- c++ -*- */
/*
 * Copyright 2022 @sashabusse.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_H
#define INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_H

#include <gnuradio/OFDM_OOT/api.h>
#include <gnuradio/block.h>

namespace gr {
namespace OFDM_OOT {

/*!
 * \brief <+description of block+>
 * \ingroup OFDM_OOT
 *
 */
class OFDM_OOT_API cfar_detector_cpp : virtual public gr::block
{
public:
    typedef std::shared_ptr<cfar_detector_cpp> sptr;

    /*!
     * \brief Return a shared_ptr to a new instance of OFDM_OOT::cfar_detector_cpp.
     *
     * To avoid accidental use of raw pointers, OFDM_OOT::cfar_detector_cpp's
     * constructor is in a private implementation
     * class. OFDM_OOT::cfar_detector_cpp::make is the public interface for
     * creating new instances.
     */
    static sptr make(gr_vector_int train_regions,
                     float p_false_alarm,
                     int n_search_forward,
                     int n_skip_after_detect);
};

} // namespace OFDM_OOT
} // namespace gr

#endif /* INCLUDED_OFDM_OOT_CFAR_DETECTOR_CPP_H */
