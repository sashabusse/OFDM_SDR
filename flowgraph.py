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
import pmt
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
        self.samp_rate = samp_rate = int(1e6)
        self.g_qam16_cd = g_qam16_cd = {"map": np.array(digital.qam_16()[0])[digital.qam_16()[1]]*4/np.linalg.norm(digital.qam_16()[0]), 'bw': 4}
        self.lpf_taps = lpf_taps = firdes.low_pass(1.0, 4*samp_rate, samp_rate,samp_rate/8, window.WIN_HAMMING, 6.76)
        self.g_qpsk_cd = g_qpsk_cd = {"map": [-1-1j, -1+1j, 1-1j, 1+1j], "bw": 2}
        self.g_cd = g_cd = g_qam16_cd
        self.g_bpsk_cd = g_bpsk_cd = {"map": [-1., 1.], "bw": 1}
        self.carrier_freq = carrier_freq = int(1.970e9)

        ##################################################
        # Blocks
        ##################################################
        self._carrier_freq_range = Range(int(1.8e9), int(2.2e9), int(0.001e9), int(1.970e9), 200)
        self._carrier_freq_win = RangeWidget(self._carrier_freq_range, self.set_carrier_freq, "carrier_freq", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._carrier_freq_win)
        self.qtgui_vector_sink_f_0 = qtgui.vector_sink_f(
            1024,
            0,
            1.0,
            "x-Axis",
            "y-Axis",
            "",
            1, # Number of inputs
            None # parent
        )
        self.qtgui_vector_sink_f_0.set_update_time(0.10)
        self.qtgui_vector_sink_f_0.set_y_axis(0, 20)
        self.qtgui_vector_sink_f_0.enable_autoscale(False)
        self.qtgui_vector_sink_f_0.enable_grid(False)
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
        self.top_layout.addWidget(self._qtgui_vector_sink_f_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            4096, #size
            1, #samp_rate
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
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
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32('' if '' else iio.get_pluto_uri(), [True, True], int(samp_rate/10))
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(carrier_freq)
        self.iio_pluto_source_0.set_samplerate(samp_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'slow_attack')
        self.iio_pluto_source_0.set_gain(0, 64)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('' if '' else iio.get_pluto_uri(), [True, True], int(samp_rate/10), False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(20000000)
        self.iio_pluto_sink_0.set_frequency(carrier_freq)
        self.iio_pluto_sink_0.set_samplerate(samp_rate)
        self.iio_pluto_sink_0.set_attenuation(0, 10)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bc(g_cd['map'], 1)
        self.blocks_packed_to_unpacked_xx_0 = blocks.packed_to_unpacked_bb(g_cd['bw'], gr.GR_MSB_FIRST)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_gr_complex*1024)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, '/home/sashabusse/dev/SDR/OFDM/data/cat.jpg', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_complex_to_mag_1 = blocks.complex_to_mag(1024)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.OFDM_OOT_ofdm_modulator_cpp_cc_0 = OFDM_OOT.ofdm_modulator_cpp_cc(1024, [i for i in range(2, 301, 2)], [i for i in range(1, 302, 2)], [1]*151, 128)
        self.OFDM_OOT_ofdm_corr_sync_demultiplex_0 = OFDM_OOT.ofdm_corr_sync_demultiplex(1024)
        self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0 = OFDM_OOT.ofdm_corr_sync_cpp_cc(nfft=1024, n_guard=128, corr_sz=64)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0, 0), (self.OFDM_OOT_ofdm_corr_sync_demultiplex_0, 0))
        self.connect((self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0, 1), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.OFDM_OOT_ofdm_corr_sync_demultiplex_0, 0), (self.blocks_complex_to_mag_1, 0))
        self.connect((self.OFDM_OOT_ofdm_corr_sync_demultiplex_0, 0), (self.blocks_null_sink_0_0, 0))
        self.connect((self.OFDM_OOT_ofdm_modulator_cpp_cc_0, 0), (self.iio_pluto_sink_0, 0))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_complex_to_mag_1, 0), (self.qtgui_vector_sink_f_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.blocks_packed_to_unpacked_xx_0, 0))
        self.connect((self.blocks_packed_to_unpacked_xx_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.OFDM_OOT_ofdm_modulator_cpp_cc_0, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.OFDM_OOT_ofdm_corr_sync_cpp_cc_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "flowgraph")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_lpf_taps(firdes.low_pass(1.0, 4*self.samp_rate, self.samp_rate, self.samp_rate/8, window.WIN_HAMMING, 6.76))
        self.iio_pluto_sink_0.set_samplerate(self.samp_rate)
        self.iio_pluto_source_0.set_samplerate(self.samp_rate)

    def get_g_qam16_cd(self):
        return self.g_qam16_cd

    def set_g_qam16_cd(self, g_qam16_cd):
        self.g_qam16_cd = g_qam16_cd
        self.set_g_cd(self.g_qam16_cd)

    def get_lpf_taps(self):
        return self.lpf_taps

    def set_lpf_taps(self, lpf_taps):
        self.lpf_taps = lpf_taps

    def get_g_qpsk_cd(self):
        return self.g_qpsk_cd

    def set_g_qpsk_cd(self, g_qpsk_cd):
        self.g_qpsk_cd = g_qpsk_cd

    def get_g_cd(self):
        return self.g_cd

    def set_g_cd(self, g_cd):
        self.g_cd = g_cd
        self.digital_chunks_to_symbols_xx_0.set_symbol_table(self.g_cd['map'])

    def get_g_bpsk_cd(self):
        return self.g_bpsk_cd

    def set_g_bpsk_cd(self, g_bpsk_cd):
        self.g_bpsk_cd = g_bpsk_cd

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq
        self.iio_pluto_sink_0.set_frequency(self.carrier_freq)
        self.iio_pluto_source_0.set_frequency(self.carrier_freq)




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
