#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import OFDM_OOT
from gnuradio import blocks
from gnuradio import digital
from gnuradio import fec
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import numpy as np



from gnuradio import qtgui

class flowgraph(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "flowgraph")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.pilot_carriers_idx = pilot_carriers_idx = [i for i in range(1, 2+2*128, 2)]
        self.g_qpsk_constellation = g_qpsk_constellation = digital.constellation_qpsk().base()
        self.data_carriers_idx = data_carriers_idx = [i for i in range(2, 3+2*127, 2)]
        self.samp_rate = samp_rate = int(1e6)
        self.pilot_carriers_vals = pilot_carriers_vals = ([2, -2]*(len(pilot_carriers_idx)//2)) + ([2]*(len(pilot_carriers_idx)%2))
        self.g_constellation = g_constellation = g_qpsk_constellation
        self.data_vec = data_vec = np.random.randint(0, 4, len(data_carriers_idx))
        self.carrier_freq = carrier_freq = int(2.050e9)

        ##################################################
        # Blocks
        ##################################################
        self._carrier_freq_range = Range(int(1.8e9), int(2.2e9), int(0.001e9), int(2.050e9), 200)
        self._carrier_freq_win = RangeWidget(self._carrier_freq_range, self.set_carrier_freq, "carrier_freq", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._carrier_freq_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.snr_est = qtgui.number_sink(
            gr.sizeof_float,
            1,
            qtgui.NUM_GRAPH_NONE,
            1,
            None # parent
        )
        self.snr_est.set_update_time(0.10)
        self.snr_est.set_title("SNR est")

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.snr_est.set_min(i, 0)
            self.snr_est.set_max(i, 3)
            self.snr_est.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.snr_est.set_label(i, "Data {0}".format(i))
            else:
                self.snr_est.set_label(i, labels[i])
            self.snr_est.set_unit(i, units[i])
            self.snr_est.set_factor(i, factor[i])

        self.snr_est.enable_autoscale(False)
        self._snr_est_win = sip.wrapinstance(self.snr_est.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._snr_est_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_vector_sink_f_0 = qtgui.vector_sink_f(
            1024,
            0,
            1.0,
            "x-Axis",
            "y-Axis",
            "ofdm symbol spectrum",
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_0.set_update_time(0.10)
        self.qtgui_vector_sink_f_0.set_y_axis(0, 5)
        self.qtgui_vector_sink_f_0.enable_autoscale(False)
        self.qtgui_vector_sink_f_0.enable_grid(True)
        self.qtgui_vector_sink_f_0.set_x_axis_units("")
        self.qtgui_vector_sink_f_0.set_y_axis_units("")
        self.qtgui_vector_sink_f_0.set_ref_level(0)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_vector_sink_f_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_0.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_0.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_0.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_0.set_line_alpha(i, alphas[i])

        self._qtgui_vector_sink_f_0_win = sip.wrapinstance(self.qtgui_vector_sink_f_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_vector_sink_f_0_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            4096, #size
            1, #samp_rate
            "prefix correlation", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_AUTO, qtgui.TRIG_SLOPE_POS, 0.8, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 3, 0, 1, 2)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            carrier_freq, #fc
            samp_rate, #bw
            "pluto source", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_0_0 = qtgui.const_sink_c(
            len(data_carriers_idx), #size
            "data symbols", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0_0.set_update_time(0.2)
        self.qtgui_const_sink_x_0_0.set_y_axis(-5, 5)
        self.qtgui_const_sink_x_0_0.set_x_axis(-10, 10)
        self.qtgui_const_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0_0.enable_grid(True)
        self.qtgui_const_sink_x_0_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_0_win, 4, 1, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "ofdm decoded symbols", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.2)
        self.qtgui_const_sink_x_0.set_y_axis(-5, 5)
        self.qtgui_const_sink_x_0.set_x_axis(-10, 10)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(True)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win, 4, 0, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('' if '' else iio.get_pluto_uri(), [True, True], int(3e3))
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(carrier_freq)
        self.iio_pluto_source_0.set_samplerate(samp_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'slow_attack')
        self.iio_pluto_source_0.set_gain(0, 64)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('' if '' else iio.get_pluto_uri(), [True, True], int(samp_rate*2), True)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(2*samp_rate)
        self.iio_pluto_sink_0.set_frequency(carrier_freq)
        self.iio_pluto_sink_0.set_samplerate(samp_rate)
        self.iio_pluto_sink_0.set_attenuation(0, 30)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.fec_ber_bf_0 = fec.ber_bf(False, 10000000, -7.0)
        self.digital_constellation_encoder_bc_0_0 = digital.constellation_encoder_bc(g_constellation)
        self.digital_constellation_encoder_bc_0 = digital.constellation_encoder_bc(g_constellation)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(g_constellation)
        self.blocks_vector_to_stream_0_0_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, len(data_carriers_idx))
        self.blocks_vector_to_stream_0_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, len(data_carriers_idx))
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, 1024)
        self.blocks_vector_source_x_0_0 = blocks.vector_source_b(data_vec, True, 1, [])
        self.blocks_vector_source_x_0 = blocks.vector_source_b(data_vec, True, 1, [])
        self.blocks_sub_xx_0 = blocks.sub_cc(1)
        self.blocks_skiphead_0_1 = blocks.skiphead(gr.sizeof_gr_complex*1, 1000)
        self.blocks_skiphead_0_0 = blocks.skiphead(gr.sizeof_char*1, 1000)
        self.blocks_skiphead_0 = blocks.skiphead(gr.sizeof_char*1, 1000)
        self.blocks_rms_xx_0 = blocks.rms_cf(0.00001)
        self.blocks_repack_bits_bb_0_0 = blocks.repack_bits_bb(2, 8, "", False, gr.GR_LSB_FIRST)
        self.blocks_repack_bits_bb_0 = blocks.repack_bits_bb(2, 8, "", False, gr.GR_LSB_FIRST)
        self.blocks_complex_to_mag_1 = blocks.complex_to_mag(1024)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.ber_est_lg = qtgui.number_sink(
            gr.sizeof_float,
            1,
            qtgui.NUM_GRAPH_NONE,
            1,
            None # parent
        )
        self.ber_est_lg.set_update_time(0.10)
        self.ber_est_lg.set_title("BER est lg")

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.ber_est_lg.set_min(i, 0)
            self.ber_est_lg.set_max(i, 3)
            self.ber_est_lg.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.ber_est_lg.set_label(i, "Data {0}".format(i))
            else:
                self.ber_est_lg.set_label(i, labels[i])
            self.ber_est_lg.set_unit(i, units[i])
            self.ber_est_lg.set_factor(i, factor[i])

        self.ber_est_lg.enable_autoscale(False)
        self._ber_est_lg_win = sip.wrapinstance(self.ber_est_lg.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._ber_est_lg_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.OFDM_OOT_ofdm_retreive_data_sym_cc_0 = OFDM_OOT.ofdm_retreive_data_sym_cc(nfft=1024, data_carriers_idx=data_carriers_idx)
        self.OFDM_OOT_ofdm_precise_sync_cc_0 = OFDM_OOT.ofdm_precise_sync_cc(nfft=1024, pilot_carriers_idx=pilot_carriers_idx, pilot_carriers_vals=pilot_carriers_vals)
        self.OFDM_OOT_ofdm_modulator_cpp_cc_0 = OFDM_OOT.ofdm_modulator_cpp_cc(1024, data_carriers_idx, pilot_carriers_idx, pilot_carriers_vals, 128)
        self.OFDM_OOT_ofdm_corr_sync_demultiplex_cc_0 = OFDM_OOT.ofdm_corr_sync_demultiplex_cc(nfft=1024)
        self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0 = OFDM_OOT.ofdm_corr_sync_cpp_cc(nfft=1024, n_guard=128, corr_sz=64)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0, 0), (self.OFDM_OOT_ofdm_corr_sync_demultiplex_cc_0, 0))
        self.connect((self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0, 1), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.OFDM_OOT_ofdm_corr_sync_demultiplex_cc_0, 0), (self.OFDM_OOT_ofdm_precise_sync_cc_0, 0))
        self.connect((self.OFDM_OOT_ofdm_modulator_cpp_cc_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.OFDM_OOT_ofdm_precise_sync_cc_0, 0), (self.OFDM_OOT_ofdm_retreive_data_sym_cc_0, 0))
        self.connect((self.OFDM_OOT_ofdm_precise_sync_cc_0, 0), (self.blocks_complex_to_mag_1, 0))
        self.connect((self.OFDM_OOT_ofdm_precise_sync_cc_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.OFDM_OOT_ofdm_retreive_data_sym_cc_0, 0), (self.blocks_vector_to_stream_0_0, 0))
        self.connect((self.OFDM_OOT_ofdm_retreive_data_sym_cc_0, 0), (self.blocks_vector_to_stream_0_0_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_1, 0), (self.qtgui_vector_sink_f_0, 0))
        self.connect((self.blocks_repack_bits_bb_0, 0), (self.blocks_skiphead_0, 0))
        self.connect((self.blocks_repack_bits_bb_0_0, 0), (self.blocks_skiphead_0_0, 0))
        self.connect((self.blocks_rms_xx_0, 0), (self.snr_est, 0))
        self.connect((self.blocks_skiphead_0, 0), (self.fec_ber_bf_0, 0))
        self.connect((self.blocks_skiphead_0_0, 0), (self.fec_ber_bf_0, 1))
        self.connect((self.blocks_skiphead_0_1, 0), (self.blocks_rms_xx_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_skiphead_0_1, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.digital_constellation_encoder_bc_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.blocks_repack_bits_bb_0_0, 0))
        self.connect((self.blocks_vector_source_x_0_0, 0), (self.digital_constellation_encoder_bc_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.blocks_vector_to_stream_0_0, 0), (self.qtgui_const_sink_x_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0_0_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_vector_to_stream_0_0_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.blocks_repack_bits_bb_0, 0))
        self.connect((self.digital_constellation_encoder_bc_0, 0), (self.OFDM_OOT_ofdm_modulator_cpp_cc_0, 0))
        self.connect((self.digital_constellation_encoder_bc_0_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.fec_ber_bf_0, 0), (self.ber_est_lg, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.qtgui_freq_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "flowgraph")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_pilot_carriers_idx(self):
        return self.pilot_carriers_idx

    def set_pilot_carriers_idx(self, pilot_carriers_idx):
        self.pilot_carriers_idx = pilot_carriers_idx
        self.set_pilot_carriers_vals(([2, -2]*(len(self.pilot_carriers_idx)//2)) + ([2]*(len(self.pilot_carriers_idx)%2)))

    def get_g_qpsk_constellation(self):
        return self.g_qpsk_constellation

    def set_g_qpsk_constellation(self, g_qpsk_constellation):
        self.g_qpsk_constellation = g_qpsk_constellation
        self.set_g_constellation(self.g_qpsk_constellation)

    def get_data_carriers_idx(self):
        return self.data_carriers_idx

    def set_data_carriers_idx(self, data_carriers_idx):
        self.data_carriers_idx = data_carriers_idx
        self.set_data_vec(np.random.randint(0, 4, len(self.data_carriers_idx)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.iio_pluto_sink_0.set_bandwidth(2*self.samp_rate)
        self.iio_pluto_sink_0.set_samplerate(self.samp_rate)
        self.iio_pluto_source_0.set_samplerate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.carrier_freq, self.samp_rate)

    def get_pilot_carriers_vals(self):
        return self.pilot_carriers_vals

    def set_pilot_carriers_vals(self, pilot_carriers_vals):
        self.pilot_carriers_vals = pilot_carriers_vals

    def get_g_constellation(self):
        return self.g_constellation

    def set_g_constellation(self, g_constellation):
        self.g_constellation = g_constellation

    def get_data_vec(self):
        return self.data_vec

    def set_data_vec(self, data_vec):
        self.data_vec = data_vec
        self.blocks_vector_source_x_0.set_data(self.data_vec, [])
        self.blocks_vector_source_x_0_0.set_data(self.data_vec, [])

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq
        self.iio_pluto_sink_0.set_frequency(self.carrier_freq)
        self.iio_pluto_source_0.set_frequency(self.carrier_freq)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.carrier_freq, self.samp_rate)




def main(top_block_cls=flowgraph, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
