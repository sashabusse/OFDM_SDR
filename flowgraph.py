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
        self.pilot_carriers_idx = pilot_carriers_idx = np.arange(1, 2*128, 4) + 40
        self.g_qpsk_constellation = g_qpsk_constellation = digital.constellation_qpsk().base()
        self.g_constellation = g_constellation = g_qpsk_constellation
        self.data_carriers_idx = data_carriers_idx = np.setdiff1d(np.arange(1, 1+2*128)+40, pilot_carriers_idx)
        self.samp_rate = samp_rate = int(2e6)
        self.pilot_carriers_vals = pilot_carriers_vals = 1.9 * np.exp(-2j*np.pi*np.arange(pilot_carriers_idx.size)/2)
        self.nguard = nguard = 128
        self.nfft = nfft = 1024
        self.data_vec = data_vec = np.random.randint(0, len(g_constellation.s_points()), len(data_carriers_idx))
        self.carrier_freq = carrier_freq = int(1.980e9)

        ##################################################
        # Blocks
        ##################################################
        self._carrier_freq_range = Range(int(0.6e9), int(2.2e9), int(0.001e9), int(1.980e9), 200)
        self._carrier_freq_win = RangeWidget(self._carrier_freq_range, self.set_carrier_freq, "carrier_freq", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._carrier_freq_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_vector_sink_f_2 = qtgui.vector_sink_f(
            64,
            0,
            1.0,
            "x-Axis",
            "y-Axis",
            "RX OFDM SYM ARG",
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_2.set_update_time(0.10)
        self.qtgui_vector_sink_f_2.set_y_axis(-np.pi, np.pi)
        self.qtgui_vector_sink_f_2.enable_autoscale(False)
        self.qtgui_vector_sink_f_2.enable_grid(False)
        self.qtgui_vector_sink_f_2.set_x_axis_units("")
        self.qtgui_vector_sink_f_2.set_y_axis_units("")
        self.qtgui_vector_sink_f_2.set_ref_level(0)

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
                self.qtgui_vector_sink_f_2.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_2.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_2.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_2.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_2.set_line_alpha(i, alphas[i])

        self._qtgui_vector_sink_f_2_win = sip.wrapinstance(self.qtgui_vector_sink_f_2.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_vector_sink_f_2_win)
        self.qtgui_vector_sink_f_1 = qtgui.vector_sink_f(
            64,
            0,
            1.0,
            "x-Axis",
            "y-Axis",
            '"RX OFDM SYM AMPLITUDE',
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_1.set_update_time(0.10)
        self.qtgui_vector_sink_f_1.set_y_axis(-140, 10)
        self.qtgui_vector_sink_f_1.enable_autoscale(True)
        self.qtgui_vector_sink_f_1.enable_grid(False)
        self.qtgui_vector_sink_f_1.set_x_axis_units("")
        self.qtgui_vector_sink_f_1.set_y_axis_units("")
        self.qtgui_vector_sink_f_1.set_ref_level(0)

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
                self.qtgui_vector_sink_f_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_vector_sink_f_1.set_line_label(i, labels[i])
            self.qtgui_vector_sink_f_1.set_line_width(i, widths[i])
            self.qtgui_vector_sink_f_1.set_line_color(i, colors[i])
            self.qtgui_vector_sink_f_1.set_line_alpha(i, alphas[i])

        self._qtgui_vector_sink_f_1_win = sip.wrapinstance(self.qtgui_vector_sink_f_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_vector_sink_f_1_win)
        self.qtgui_time_sink_x_2 = qtgui.time_sink_c(
            1024+128+64*16, #size
            samp_rate, #samp_rate
            "tx time", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_2.set_update_time(0.10)
        self.qtgui_time_sink_x_2.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_2.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_2.enable_tags(True)
        self.qtgui_time_sink_x_2.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_2.enable_autoscale(False)
        self.qtgui_time_sink_x_2.enable_grid(False)
        self.qtgui_time_sink_x_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_2.enable_control_panel(False)
        self.qtgui_time_sink_x_2.enable_stem_plot(False)


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


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_2.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_2.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_2_win = sip.wrapinstance(self.qtgui_time_sink_x_2.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_2_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
            (64+16)*10, #size
            1, #samp_rate
            "prefix correlation", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(0, 1)

        self.qtgui_time_sink_x_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.7, 0, 0, "cfar")
        self.qtgui_time_sink_x_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(True)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)


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
                self.qtgui_time_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
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
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('ip:192.168.3.1' if 'ip:192.168.3.1' else iio.get_pluto_uri(), [True, True], ((128+32)*1 + 16*4 + 128*2+32)*100)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(carrier_freq)
        self.iio_pluto_source_0.set_samplerate(1*samp_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'slow_attack')
        self.iio_pluto_source_0.set_gain(0, 64)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('ip:192.168.2.1' if 'ip:192.168.2.1' else iio.get_pluto_uri(), [True, True], ((128+32)*1 + 16*4 + 128*2+32)*100, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(int(samp_rate))
        self.iio_pluto_sink_0.set_frequency(carrier_freq)
        self.iio_pluto_sink_0.set_samplerate(1*samp_rate)
        self.iio_pluto_sink_0.set_attenuation(0, 10)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, ((64+16)*2))
        self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_file_sink_1 = blocks.file_sink(gr.sizeof_gr_complex*((64+16)*2), 'data/tmp', False)
        self.blocks_file_sink_1.set_unbuffered(False)
        self.blocks_complex_to_mag_1_0_0 = blocks.complex_to_mag(64)
        self.blocks_complex_to_mag_0_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_arg_0 = blocks.complex_to_arg(64)
        self.OFDM_OOT_test_block_0 = OFDM_OOT.test_block()
        self.OFDM_OOT_retrieve_vector_on_tag_cc_0 = OFDM_OOT.retrieve_vector_on_tag_cc('cfar', ((64+16)*2))
        self.OFDM_OOT_ofdm_source_1 = OFDM_OOT.ofdm_source()
        self.OFDM_OOT_cfar_detector_cpp_ccc_0 = OFDM_OOT.cfar_detector_cpp_ccc(100, 30, 0.01, 32, (64+16)*2)
        self.OFDM_OOT_autocorr_cpp_cccc_0 = OFDM_OOT.autocorr_cpp_cccc(32+16, 32)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.OFDM_OOT_autocorr_cpp_cccc_0, 1), (self.OFDM_OOT_cfar_detector_cpp_ccc_0, 1))
        self.connect((self.OFDM_OOT_autocorr_cpp_cccc_0, 0), (self.OFDM_OOT_cfar_detector_cpp_ccc_0, 0))
        self.connect((self.OFDM_OOT_autocorr_cpp_cccc_0, 0), (self.blocks_null_sink_1, 0))
        self.connect((self.OFDM_OOT_autocorr_cpp_cccc_0, 1), (self.blocks_null_sink_1, 1))
        self.connect((self.OFDM_OOT_cfar_detector_cpp_ccc_0, 0), (self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 0))
        self.connect((self.OFDM_OOT_cfar_detector_cpp_ccc_0, 1), (self.blocks_complex_to_mag_0_0, 0))
        self.connect((self.OFDM_OOT_ofdm_source_1, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 0), (self.OFDM_OOT_test_block_0, 0))
        self.connect((self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 1), (self.OFDM_OOT_test_block_0, 1))
        self.connect((self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 0), (self.blocks_file_sink_1, 0))
        self.connect((self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 1), (self.blocks_null_sink_0, 0))
        self.connect((self.OFDM_OOT_test_block_0, 0), (self.blocks_complex_to_arg_0, 0))
        self.connect((self.OFDM_OOT_test_block_0, 0), (self.blocks_complex_to_mag_1_0_0, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.qtgui_vector_sink_f_2, 0))
        self.connect((self.blocks_complex_to_mag_0_0, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.blocks_complex_to_mag_1_0_0, 0), (self.qtgui_vector_sink_f_1, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.qtgui_time_sink_x_2, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.OFDM_OOT_autocorr_cpp_cccc_0, 0))
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
        self.set_data_carriers_idx(np.setdiff1d(np.arange(1, 1+2*128)+40, self.pilot_carriers_idx))

    def get_g_qpsk_constellation(self):
        return self.g_qpsk_constellation

    def set_g_qpsk_constellation(self, g_qpsk_constellation):
        self.g_qpsk_constellation = g_qpsk_constellation
        self.set_g_constellation(self.g_qpsk_constellation)

    def get_g_constellation(self):
        return self.g_constellation

    def set_g_constellation(self, g_constellation):
        self.g_constellation = g_constellation

    def get_data_carriers_idx(self):
        return self.data_carriers_idx

    def set_data_carriers_idx(self, data_carriers_idx):
        self.data_carriers_idx = data_carriers_idx
        self.set_data_vec(np.random.randint(0, len(g_constellation.s_points()), len(self.data_carriers_idx)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.iio_pluto_sink_0.set_bandwidth(int(self.samp_rate))
        self.iio_pluto_sink_0.set_samplerate(1*self.samp_rate)
        self.iio_pluto_source_0.set_samplerate(1*self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.carrier_freq, self.samp_rate)
        self.qtgui_time_sink_x_2.set_samp_rate(self.samp_rate)

    def get_pilot_carriers_vals(self):
        return self.pilot_carriers_vals

    def set_pilot_carriers_vals(self, pilot_carriers_vals):
        self.pilot_carriers_vals = pilot_carriers_vals

    def get_nguard(self):
        return self.nguard

    def set_nguard(self, nguard):
        self.nguard = nguard

    def get_nfft(self):
        return self.nfft

    def set_nfft(self, nfft):
        self.nfft = nfft

    def get_data_vec(self):
        return self.data_vec

    def set_data_vec(self, data_vec):
        self.data_vec = data_vec

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
