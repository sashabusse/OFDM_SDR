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
from gnuradio import channels
from gnuradio import digital
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
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
        self.nfft = nfft = 256
        self.f_norm_min = f_norm_min = 0.1
        self.f_norm_max = f_norm_max = 0.26
        self.pilot_idx_group_1 = pilot_idx_group_1 = nfft + np.arange(-f_norm_min*nfft, -f_norm_max*nfft, -4, dtype=int)
        self.pilot_idx_group_0 = pilot_idx_group_0 = np.arange(f_norm_min*nfft, f_norm_max*nfft, 4, dtype=int)
        self.pilot_idx = pilot_idx = np.hstack([pilot_idx_group_0 , pilot_idx_group_1])
        self.data_constellation = data_constellation = digital.constellation_qpsk().base()
        self.seqN_len = seqN_len = 16
        self.seqN_N = seqN_N = 8
        self.data_idx = data_idx = np.setdiff1d(np.hstack([np.arange(f_norm_min*nfft, f_norm_max*nfft, dtype=int) , np.arange(-f_norm_min*nfft, -f_norm_max*nfft, -1, dtype=int)]), pilot_idx)[:-1]
        self.bits_per_iq = bits_per_iq = int(np.log2(len(data_constellation.s_points())))
        self.seqN_autocorr_sh = seqN_autocorr_sh = seqN_len
        self.preamble_seqN = preamble_seqN = OFDM_OOT.repeat_seqN(seqN_len, seqN_N, f_border=0.35)
        self.pilot_vals_group_1 = pilot_vals_group_1 = np.sqrt(2)*1.4 * np.exp(-2j*np.pi*np.arange(pilot_idx_group_1.size)/2)
        self.pilot_vals_group_0 = pilot_vals_group_0 = np.sqrt(2)*1.4 * np.exp(-2j*np.pi*np.arange(pilot_idx_group_0.size)/2)
        self.nguard = nguard = 32
        self.frame_sym_cnt = frame_sym_cnt = 16
        self.bits_per_sym = bits_per_sym = data_idx.size*bits_per_iq
        self.sync_autocorr_sh = sync_autocorr_sh = seqN_autocorr_sh
        self.seqN_autocorr_sz = seqN_autocorr_sz = seqN_len*(seqN_N-1)
        self.samp_rate = samp_rate = int(1e6)
        self.preamble_seqN_cfg = preamble_seqN_cfg = OFDM_OOT.repeat_seqN_cfg(seqN_len, seqN_N)
        self.pilot_vals = pilot_vals = np.hstack([pilot_vals_group_0, pilot_vals_group_1])
        self.ofdm_sym_sz = ofdm_sym_sz = nfft+nguard
        self.ofdm_preamble = ofdm_preamble = preamble_seqN
        self.carrier_freq = carrier_freq = int(1.980e9)
        self.bits_per_frame = bits_per_frame = bits_per_sym*frame_sym_cnt
        self.test_ofdm_sym = test_ofdm_sym = OFDM_OOT.random_ofdm_sym(nfft, data_idx, pilot_idx, pilot_vals, data_modulation='qpsk')
        self.sync_autocorr_sz = sync_autocorr_sz = seqN_autocorr_sz
        self.preamble_cox_s_cfg = preamble_cox_s_cfg = OFDM_OOT.cox_schmerzmittel_cfg(nfft, nguard)
        self.preamble_cox_s = preamble_cox_s = OFDM_OOT.cox_schmerzmittel(nfft, nguard, np.hstack([np.arange(25), nfft - np.arange(1, 26)]))
        self.ofdm_preamble_cfg = ofdm_preamble_cfg = preamble_seqN_cfg
        self.frame_sz = frame_sz = ofdm_preamble.size + ofdm_sym_sz*frame_sym_cnt
        self.frame_spacing = frame_spacing = (nfft+nguard)*3
        self.cox_s_autocorr_sz = cox_s_autocorr_sz = nfft//2 + nguard
        self.cox_s_autocorr_sh = cox_s_autocorr_sh = nfft//2
        self.bytes_per_frame = bytes_per_frame = bits_per_frame//8
        self.SFO_norm = SFO_norm = 160e-6
        self.CFO_norm_max_allowed = CFO_norm_max_allowed = 1/(2*sync_autocorr_sh)
        self.CFO_norm = CFO_norm = 10e-6*carrier_freq/samp_rate

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
        self.zeromq_pub_sink_0_0 = zeromq.pub_sink(gr.sizeof_char, bytes_per_frame, 'tcp://127.0.0.1:55556', 100, False, -1, '')
        self.zeromq_pub_sink_0 = zeromq.pub_sink(gr.sizeof_gr_complex, nfft, 'tcp://127.0.0.1:55557', 100, False, -1, '')
        self.qtgui_vector_sink_f_1 = qtgui.vector_sink_f(
            nfft,
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

        labels = ['default', 'mul -1', 'zeros', '', '',
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
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
            frame_sz*5, #size
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
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            carrier_freq, #fc
            samp_rate, #bw
            "rx stream spectrum", #name
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_1 = qtgui.const_sink_c(
            nfft*frame_sym_cnt, #size
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_1.set_update_time(0.10)
        self.qtgui_const_sink_x_1.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_1.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_1.enable_autoscale(True)
        self.qtgui_const_sink_x_1.enable_grid(True)
        self.qtgui_const_sink_x_1.enable_axis_labels(True)


        labels = ['sco compensated', 'sco non-compensated', '', '', '',
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
                self.qtgui_const_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_1.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_1.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_1_win = sip.wrapinstance(self.qtgui_const_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_const_sink_x_1_win)
        self.digital_constellation_decoder_cb_0 = digital.constellation_decoder_cb(data_constellation)
        self.channels_channel_model_0 = channels.channel_model(
            noise_voltage=0.00,
            frequency_offset=0*CFO_norm,
            epsilon=1+0*SFO_norm,
            taps=[1],
            noise_seed=0,
            block_tags=False)
        self.blocks_vector_to_stream_1_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, frame_sz+frame_spacing)
        self.blocks_vector_to_stream_1 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, nfft)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, data_idx.size)
        self.blocks_vector_source_x_1 = blocks.vector_source_c(np.zeros(frame_spacing), True, frame_spacing, [])
        self.blocks_vector_source_x_0 = blocks.vector_source_c(test_ofdm_sym, True, nfft, [])
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(bits_per_iq, gr.GR_MSB_FIRST)
        self.blocks_throttle_1_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_stream_to_vector_1 = blocks.stream_to_vector(gr.sizeof_char*1, bytes_per_frame)
        self.blocks_probe_rate_0 = blocks.probe_rate(gr.sizeof_gr_complex*1, 500.0, 0.15)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_cc(1)
        self.blocks_message_debug_0 = blocks.message_debug(True)
        self.blocks_file_sink_0_0_0 = blocks.file_sink(gr.sizeof_gr_complex*nfft, 'rx_tx_records/precise_sync_last_record.bin', False)
        self.blocks_file_sink_0_0_0.set_unbuffered(False)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_gr_complex*nfft, 'rx_tx_records/coarse_sync_last_record.bin', False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*frame_sz, 'rx_tx_records/frames_last_record.bin', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_complex_to_mag_1_0_0 = blocks.complex_to_mag(nfft)
        self.blocks_complex_to_mag_0_0 = blocks.complex_to_mag(1)
        self.OFDM_OOT_vector_retrive_by_idx_cc_0 = OFDM_OOT.vector_retrive_by_idx_cc(nfft, data_idx.size, data_idx)
        self.OFDM_OOT_vector_concat_0 = OFDM_OOT.vector_concat(frame_sz, frame_spacing)
        self.OFDM_OOT_vector_assign_cc_1 = OFDM_OOT.vector_assign_cc(nfft, pilot_idx, pilot_vals)
        self.OFDM_OOT_retrieve_vector_on_tag_cc_0 = OFDM_OOT.retrieve_vector_on_tag_cc('cfar', frame_sz, 0)
        self.OFDM_OOT_ofdm_precise_sync_cc_1 = OFDM_OOT.ofdm_precise_sync_cc(nfft=nfft, pilot_groups_idx=[pilot_idx_group_0, pilot_idx_group_1], pilot_groups_vals=[pilot_vals_group_0, pilot_vals_group_1], report_freq_off=True)
        self.OFDM_OOT_ofdm_preamble_sync_0 = OFDM_OOT.ofdm_preamble_sync(nfft, nguard, frame_sym_cnt, True, ofdm_preamble_cfg, True, True, 5, pilot_idx, frame_sz, True)
        self.OFDM_OOT_ofdm_frame_builder_0 = OFDM_OOT.ofdm_frame_builder(nfft, nguard, frame_sym_cnt, ofdm_preamble)
        self.OFDM_OOT_cfar_detector_cpp_0 = OFDM_OOT.cfar_detector_cpp([ -sync_autocorr_sz+1 - int(0.8*frame_spacing), -(sync_autocorr_sz)+1], 1e-30, int(sync_autocorr_sz*1.5), frame_sz)
        self.OFDM_OOT_autocorr_cpp_cc_0 = OFDM_OOT.autocorr_cpp_cc(sync_autocorr_sz, sync_autocorr_sh, False, False)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_probe_rate_0, 'rate'), (self.blocks_message_debug_0, 'print'))
        self.connect((self.OFDM_OOT_autocorr_cpp_cc_0, 0), (self.OFDM_OOT_cfar_detector_cpp_0, 0))
        self.connect((self.OFDM_OOT_autocorr_cpp_cc_0, 1), (self.OFDM_OOT_cfar_detector_cpp_0, 1))
        self.connect((self.OFDM_OOT_cfar_detector_cpp_0, 0), (self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 0))
        self.connect((self.OFDM_OOT_cfar_detector_cpp_0, 1), (self.blocks_complex_to_mag_0_0, 0))
        self.connect((self.OFDM_OOT_cfar_detector_cpp_0, 0), (self.blocks_probe_rate_0, 0))
        self.connect((self.OFDM_OOT_ofdm_frame_builder_0, 0), (self.OFDM_OOT_vector_concat_0, 0))
        self.connect((self.OFDM_OOT_ofdm_preamble_sync_0, 0), (self.OFDM_OOT_ofdm_precise_sync_cc_1, 0))
        self.connect((self.OFDM_OOT_ofdm_preamble_sync_0, 0), (self.blocks_file_sink_0_0, 0))
        self.connect((self.OFDM_OOT_ofdm_precise_sync_cc_1, 0), (self.OFDM_OOT_vector_retrive_by_idx_cc_0, 0))
        self.connect((self.OFDM_OOT_ofdm_precise_sync_cc_1, 0), (self.blocks_complex_to_mag_1_0_0, 0))
        self.connect((self.OFDM_OOT_ofdm_precise_sync_cc_1, 0), (self.blocks_file_sink_0_0_0, 0))
        self.connect((self.OFDM_OOT_ofdm_precise_sync_cc_1, 0), (self.blocks_vector_to_stream_1, 0))
        self.connect((self.OFDM_OOT_ofdm_precise_sync_cc_1, 0), (self.zeromq_pub_sink_0, 0))
        self.connect((self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 0), (self.OFDM_OOT_ofdm_preamble_sync_0, 0))
        self.connect((self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.OFDM_OOT_retrieve_vector_on_tag_cc_0, 1), (self.blocks_null_sink_0, 0))
        self.connect((self.OFDM_OOT_vector_assign_cc_1, 0), (self.OFDM_OOT_ofdm_frame_builder_0, 0))
        self.connect((self.OFDM_OOT_vector_concat_0, 0), (self.blocks_vector_to_stream_1_0, 0))
        self.connect((self.OFDM_OOT_vector_retrive_by_idx_cc_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_complex_to_mag_0_0, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.blocks_complex_to_mag_1_0_0, 0), (self.qtgui_vector_sink_f_1, 0))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.blocks_throttle_1_0, 0))
        self.connect((self.blocks_stream_to_vector_1, 0), (self.zeromq_pub_sink_0_0, 0))
        self.connect((self.blocks_throttle_1_0, 0), (self.channels_channel_model_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.blocks_stream_to_vector_1, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.OFDM_OOT_vector_assign_cc_1, 0))
        self.connect((self.blocks_vector_source_x_1, 0), (self.OFDM_OOT_vector_concat_0, 1))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.digital_constellation_decoder_cb_0, 0))
        self.connect((self.blocks_vector_to_stream_1, 0), (self.qtgui_const_sink_x_1, 0))
        self.connect((self.blocks_vector_to_stream_1_0, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.channels_channel_model_0, 0), (self.OFDM_OOT_autocorr_cpp_cc_0, 0))
        self.connect((self.channels_channel_model_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.digital_constellation_decoder_cb_0, 0), (self.blocks_unpacked_to_packed_xx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "flowgraph")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_nfft(self):
        return self.nfft

    def set_nfft(self, nfft):
        self.nfft = nfft
        self.set_cox_s_autocorr_sh(self.nfft//2)
        self.set_cox_s_autocorr_sz(self.nfft//2 + self.nguard)
        self.set_data_idx(np.setdiff1d(np.hstack([np.arange(self.f_norm_min*self.nfft, self.f_norm_max*self.nfft, dtype=int) , np.arange(-self.f_norm_min*self.nfft, -self.f_norm_max*self.nfft, -1, dtype=int)]), self.pilot_idx)[:-1])
        self.set_frame_spacing((self.nfft+self.nguard)*3)
        self.set_ofdm_sym_sz(self.nfft+self.nguard)
        self.set_pilot_idx_group_0(np.arange(self.f_norm_min*self.nfft, self.f_norm_max*self.nfft, 4, dtype=int))
        self.set_pilot_idx_group_1(self.nfft + np.arange(-self.f_norm_min*self.nfft, -self.f_norm_max*self.nfft, -4, dtype=int))
        self.set_preamble_cox_s(OFDM_OOT.cox_schmerzmittel(self.nfft, self.nguard, np.hstack([np.arange(25), self.nfft - np.arange(1, 26)])))
        self.set_preamble_cox_s_cfg(OFDM_OOT.cox_schmerzmittel_cfg(self.nfft, self.nguard))
        self.set_test_ofdm_sym(OFDM_OOT.random_ofdm_sym(self.nfft, self.data_idx, self.pilot_idx, self.pilot_vals, data_modulation='qpsk'))

    def get_f_norm_min(self):
        return self.f_norm_min

    def set_f_norm_min(self, f_norm_min):
        self.f_norm_min = f_norm_min
        self.set_data_idx(np.setdiff1d(np.hstack([np.arange(self.f_norm_min*self.nfft, self.f_norm_max*self.nfft, dtype=int) , np.arange(-self.f_norm_min*self.nfft, -self.f_norm_max*self.nfft, -1, dtype=int)]), self.pilot_idx)[:-1])
        self.set_pilot_idx_group_0(np.arange(self.f_norm_min*self.nfft, self.f_norm_max*self.nfft, 4, dtype=int))
        self.set_pilot_idx_group_1(self.nfft + np.arange(-self.f_norm_min*self.nfft, -self.f_norm_max*self.nfft, -4, dtype=int))

    def get_f_norm_max(self):
        return self.f_norm_max

    def set_f_norm_max(self, f_norm_max):
        self.f_norm_max = f_norm_max
        self.set_data_idx(np.setdiff1d(np.hstack([np.arange(self.f_norm_min*self.nfft, self.f_norm_max*self.nfft, dtype=int) , np.arange(-self.f_norm_min*self.nfft, -self.f_norm_max*self.nfft, -1, dtype=int)]), self.pilot_idx)[:-1])
        self.set_pilot_idx_group_0(np.arange(self.f_norm_min*self.nfft, self.f_norm_max*self.nfft, 4, dtype=int))
        self.set_pilot_idx_group_1(self.nfft + np.arange(-self.f_norm_min*self.nfft, -self.f_norm_max*self.nfft, -4, dtype=int))

    def get_pilot_idx_group_1(self):
        return self.pilot_idx_group_1

    def set_pilot_idx_group_1(self, pilot_idx_group_1):
        self.pilot_idx_group_1 = pilot_idx_group_1
        self.set_pilot_idx(np.hstack([self.pilot_idx_group_0 , self.pilot_idx_group_1]))

    def get_pilot_idx_group_0(self):
        return self.pilot_idx_group_0

    def set_pilot_idx_group_0(self, pilot_idx_group_0):
        self.pilot_idx_group_0 = pilot_idx_group_0
        self.set_pilot_idx(np.hstack([self.pilot_idx_group_0 , self.pilot_idx_group_1]))

    def get_pilot_idx(self):
        return self.pilot_idx

    def set_pilot_idx(self, pilot_idx):
        self.pilot_idx = pilot_idx
        self.set_data_idx(np.setdiff1d(np.hstack([np.arange(self.f_norm_min*self.nfft, self.f_norm_max*self.nfft, dtype=int) , np.arange(-self.f_norm_min*self.nfft, -self.f_norm_max*self.nfft, -1, dtype=int)]), self.pilot_idx)[:-1])
        self.set_test_ofdm_sym(OFDM_OOT.random_ofdm_sym(self.nfft, self.data_idx, self.pilot_idx, self.pilot_vals, data_modulation='qpsk'))

    def get_data_constellation(self):
        return self.data_constellation

    def set_data_constellation(self, data_constellation):
        self.data_constellation = data_constellation

    def get_seqN_len(self):
        return self.seqN_len

    def set_seqN_len(self, seqN_len):
        self.seqN_len = seqN_len
        self.set_preamble_seqN(OFDM_OOT.repeat_seqN(self.seqN_len, self.seqN_N, f_border=0.35))
        self.set_preamble_seqN_cfg(OFDM_OOT.repeat_seqN_cfg(self.seqN_len, self.seqN_N))
        self.set_seqN_autocorr_sh(self.seqN_len)
        self.set_seqN_autocorr_sz(self.seqN_len*(self.seqN_N-1))

    def get_seqN_N(self):
        return self.seqN_N

    def set_seqN_N(self, seqN_N):
        self.seqN_N = seqN_N
        self.set_preamble_seqN(OFDM_OOT.repeat_seqN(self.seqN_len, self.seqN_N, f_border=0.35))
        self.set_preamble_seqN_cfg(OFDM_OOT.repeat_seqN_cfg(self.seqN_len, self.seqN_N))
        self.set_seqN_autocorr_sz(self.seqN_len*(self.seqN_N-1))

    def get_data_idx(self):
        return self.data_idx

    def set_data_idx(self, data_idx):
        self.data_idx = data_idx
        self.set_test_ofdm_sym(OFDM_OOT.random_ofdm_sym(self.nfft, self.data_idx, self.pilot_idx, self.pilot_vals, data_modulation='qpsk'))

    def get_bits_per_iq(self):
        return self.bits_per_iq

    def set_bits_per_iq(self, bits_per_iq):
        self.bits_per_iq = bits_per_iq
        self.set_bits_per_sym(data_idx.size*self.bits_per_iq)

    def get_seqN_autocorr_sh(self):
        return self.seqN_autocorr_sh

    def set_seqN_autocorr_sh(self, seqN_autocorr_sh):
        self.seqN_autocorr_sh = seqN_autocorr_sh
        self.set_sync_autocorr_sh(self.seqN_autocorr_sh)

    def get_preamble_seqN(self):
        return self.preamble_seqN

    def set_preamble_seqN(self, preamble_seqN):
        self.preamble_seqN = preamble_seqN
        self.set_ofdm_preamble(self.preamble_seqN)

    def get_pilot_vals_group_1(self):
        return self.pilot_vals_group_1

    def set_pilot_vals_group_1(self, pilot_vals_group_1):
        self.pilot_vals_group_1 = pilot_vals_group_1
        self.set_pilot_vals(np.hstack([self.pilot_vals_group_0, self.pilot_vals_group_1]))

    def get_pilot_vals_group_0(self):
        return self.pilot_vals_group_0

    def set_pilot_vals_group_0(self, pilot_vals_group_0):
        self.pilot_vals_group_0 = pilot_vals_group_0
        self.set_pilot_vals(np.hstack([self.pilot_vals_group_0, self.pilot_vals_group_1]))

    def get_nguard(self):
        return self.nguard

    def set_nguard(self, nguard):
        self.nguard = nguard
        self.set_cox_s_autocorr_sz(self.nfft//2 + self.nguard)
        self.set_frame_spacing((self.nfft+self.nguard)*3)
        self.set_ofdm_sym_sz(self.nfft+self.nguard)
        self.set_preamble_cox_s(OFDM_OOT.cox_schmerzmittel(self.nfft, self.nguard, np.hstack([np.arange(25), self.nfft - np.arange(1, 26)])))
        self.set_preamble_cox_s_cfg(OFDM_OOT.cox_schmerzmittel_cfg(self.nfft, self.nguard))

    def get_frame_sym_cnt(self):
        return self.frame_sym_cnt

    def set_frame_sym_cnt(self, frame_sym_cnt):
        self.frame_sym_cnt = frame_sym_cnt
        self.set_bits_per_frame(self.bits_per_sym*self.frame_sym_cnt)
        self.set_frame_sz(ofdm_preamble.size + self.ofdm_sym_sz*self.frame_sym_cnt)

    def get_bits_per_sym(self):
        return self.bits_per_sym

    def set_bits_per_sym(self, bits_per_sym):
        self.bits_per_sym = bits_per_sym
        self.set_bits_per_frame(self.bits_per_sym*self.frame_sym_cnt)

    def get_sync_autocorr_sh(self):
        return self.sync_autocorr_sh

    def set_sync_autocorr_sh(self, sync_autocorr_sh):
        self.sync_autocorr_sh = sync_autocorr_sh
        self.set_CFO_norm_max_allowed(1/(2*self.sync_autocorr_sh))

    def get_seqN_autocorr_sz(self):
        return self.seqN_autocorr_sz

    def set_seqN_autocorr_sz(self, seqN_autocorr_sz):
        self.seqN_autocorr_sz = seqN_autocorr_sz
        self.set_sync_autocorr_sz(self.seqN_autocorr_sz)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_CFO_norm(10e-6*self.carrier_freq/self.samp_rate)
        self.blocks_throttle_1_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.carrier_freq, self.samp_rate)

    def get_preamble_seqN_cfg(self):
        return self.preamble_seqN_cfg

    def set_preamble_seqN_cfg(self, preamble_seqN_cfg):
        self.preamble_seqN_cfg = preamble_seqN_cfg
        self.set_ofdm_preamble_cfg(self.preamble_seqN_cfg)

    def get_pilot_vals(self):
        return self.pilot_vals

    def set_pilot_vals(self, pilot_vals):
        self.pilot_vals = pilot_vals
        self.set_test_ofdm_sym(OFDM_OOT.random_ofdm_sym(self.nfft, self.data_idx, self.pilot_idx, self.pilot_vals, data_modulation='qpsk'))

    def get_ofdm_sym_sz(self):
        return self.ofdm_sym_sz

    def set_ofdm_sym_sz(self, ofdm_sym_sz):
        self.ofdm_sym_sz = ofdm_sym_sz
        self.set_frame_sz(ofdm_preamble.size + self.ofdm_sym_sz*self.frame_sym_cnt)

    def get_ofdm_preamble(self):
        return self.ofdm_preamble

    def set_ofdm_preamble(self, ofdm_preamble):
        self.ofdm_preamble = ofdm_preamble

    def get_carrier_freq(self):
        return self.carrier_freq

    def set_carrier_freq(self, carrier_freq):
        self.carrier_freq = carrier_freq
        self.set_CFO_norm(10e-6*self.carrier_freq/self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.carrier_freq, self.samp_rate)

    def get_bits_per_frame(self):
        return self.bits_per_frame

    def set_bits_per_frame(self, bits_per_frame):
        self.bits_per_frame = bits_per_frame
        self.set_bytes_per_frame(self.bits_per_frame//8)

    def get_test_ofdm_sym(self):
        return self.test_ofdm_sym

    def set_test_ofdm_sym(self, test_ofdm_sym):
        self.test_ofdm_sym = test_ofdm_sym
        self.blocks_vector_source_x_0.set_data(self.test_ofdm_sym, [])

    def get_sync_autocorr_sz(self):
        return self.sync_autocorr_sz

    def set_sync_autocorr_sz(self, sync_autocorr_sz):
        self.sync_autocorr_sz = sync_autocorr_sz

    def get_preamble_cox_s_cfg(self):
        return self.preamble_cox_s_cfg

    def set_preamble_cox_s_cfg(self, preamble_cox_s_cfg):
        self.preamble_cox_s_cfg = preamble_cox_s_cfg

    def get_preamble_cox_s(self):
        return self.preamble_cox_s

    def set_preamble_cox_s(self, preamble_cox_s):
        self.preamble_cox_s = preamble_cox_s

    def get_ofdm_preamble_cfg(self):
        return self.ofdm_preamble_cfg

    def set_ofdm_preamble_cfg(self, ofdm_preamble_cfg):
        self.ofdm_preamble_cfg = ofdm_preamble_cfg

    def get_frame_sz(self):
        return self.frame_sz

    def set_frame_sz(self, frame_sz):
        self.frame_sz = frame_sz

    def get_frame_spacing(self):
        return self.frame_spacing

    def set_frame_spacing(self, frame_spacing):
        self.frame_spacing = frame_spacing
        self.blocks_vector_source_x_1.set_data(np.zeros(self.frame_spacing), [])

    def get_cox_s_autocorr_sz(self):
        return self.cox_s_autocorr_sz

    def set_cox_s_autocorr_sz(self, cox_s_autocorr_sz):
        self.cox_s_autocorr_sz = cox_s_autocorr_sz

    def get_cox_s_autocorr_sh(self):
        return self.cox_s_autocorr_sh

    def set_cox_s_autocorr_sh(self, cox_s_autocorr_sh):
        self.cox_s_autocorr_sh = cox_s_autocorr_sh

    def get_bytes_per_frame(self):
        return self.bytes_per_frame

    def set_bytes_per_frame(self, bytes_per_frame):
        self.bytes_per_frame = bytes_per_frame

    def get_SFO_norm(self):
        return self.SFO_norm

    def set_SFO_norm(self, SFO_norm):
        self.SFO_norm = SFO_norm
        self.channels_channel_model_0.set_timing_offset(1+0*self.SFO_norm)

    def get_CFO_norm_max_allowed(self):
        return self.CFO_norm_max_allowed

    def set_CFO_norm_max_allowed(self, CFO_norm_max_allowed):
        self.CFO_norm_max_allowed = CFO_norm_max_allowed

    def get_CFO_norm(self):
        return self.CFO_norm

    def set_CFO_norm(self, CFO_norm):
        self.CFO_norm = CFO_norm
        self.channels_channel_model_0.set_frequency_offset(0*self.CFO_norm)




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
