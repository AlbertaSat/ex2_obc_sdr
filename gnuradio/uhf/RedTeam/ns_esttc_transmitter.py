#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Northern SPIRIT ESTTC command transmitter
# Author: Steven Knudsen
# Copyright: AlbertaSat, 2023
# Description: A program that accepts UDP packets containing complete ESTTC commands, modulates them, and transmits.
# GNU Radio version: 3.9.7.0

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt5 import Qt
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
import pmt
from gnuradio import gr
from gnuradio.fft import window
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import uhd
import time
from uhf_pdu_modulate import uhf_pdu_modulate  # grc-generated hier_block
import math
import numpy as np



from gnuradio import qtgui

class ns_esttc_transmitter(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Northern SPIRIT ESTTC command transmitter", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Northern SPIRIT ESTTC command transmitter")
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

        self.settings = Qt.QSettings("GNU Radio", "ns_esttc_transmitter")

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
        self.es_mode = es_mode = 0
        self.samples_per_symbol = samples_per_symbol = 100
        self.freq_dev = freq_dev = {es_mode == 0: 600, es_mode==1: 600, es_mode==2:1200,es_mode==3:2400,es_mode==4:4800,es_mode==5:4800,es_mode==6:9600}.get(True,19200)
        self.data_rate = data_rate = {es_mode == 0: 1200, es_mode==1: 2400, es_mode==2:4800,es_mode==3:9600,es_mode==4:9600}.get(True,19200)
        self.sensitivity_tx = sensitivity_tx = 2*np.math.pi*(freq_dev/(data_rate*samples_per_symbol))
        self.mod_index = mod_index = {es_mode == 0: 1, es_mode==1: 0.5, es_mode==2:0.5,es_mode==3:0.5,es_mode==4:1,es_mode==5:0.5,es_mode==6:1}.get(True,2)
        self.tx_gain = tx_gain = 0.9
        self.sensitivity_label = sensitivity_label = sensitivity_tx
        self.samp_rate = samp_rate = data_rate*samples_per_symbol
        self.mod_index_label = mod_index_label = mod_index
        self.freq_dev_label = freq_dev_label = freq_dev
        self.es_mode_label = es_mode_label = es_mode
        self.data_rate_label = data_rate_label = data_rate
        self.center_freq = center_freq = 437875000

        ##################################################
        # Blocks
        ##################################################
        self.uhf_pdu_modulate_0 = uhf_pdu_modulate(
            FSK_level=2,
            fm_baud=data_rate,
            fm_modulation_index=mod_index,
            fm_samples_per_symbol=samples_per_symbol,
        )
        self.uhd_usrp_sink_0_0 = uhd.usrp_sink(
            ",".join(("", "")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            '',
        )
        self.uhd_usrp_sink_0_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_sink_0_0.set_center_freq(center_freq, 0)
        self.uhd_usrp_sink_0_0.set_antenna('TX/RX', 0)
        self.uhd_usrp_sink_0_0.set_normalized_gain(tx_gain, 0)
        self._sensitivity_label_tool_bar = Qt.QToolBar(self)

        if None:
            self._sensitivity_label_formatter = None
        else:
            self._sensitivity_label_formatter = lambda x: eng_notation.num_to_str(x)

        self._sensitivity_label_tool_bar.addWidget(Qt.QLabel("FM Sensitivity"))
        self._sensitivity_label_label = Qt.QLabel(str(self._sensitivity_label_formatter(self.sensitivity_label)))
        self._sensitivity_label_tool_bar.addWidget(self._sensitivity_label_label)
        self.top_grid_layout.addWidget(self._sensitivity_label_tool_bar, 0, 4, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 5):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            32768, #size
            window.WIN_FLATTOP, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(True)
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
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self._mod_index_label_tool_bar = Qt.QToolBar(self)

        if None:
            self._mod_index_label_formatter = None
        else:
            self._mod_index_label_formatter = lambda x: eng_notation.num_to_str(x)

        self._mod_index_label_tool_bar.addWidget(Qt.QLabel("Mod Index"))
        self._mod_index_label_label = Qt.QLabel(str(self._mod_index_label_formatter(self.mod_index_label)))
        self._mod_index_label_tool_bar.addWidget(self._mod_index_label_label)
        self.top_grid_layout.addWidget(self._mod_index_label_tool_bar, 0, 3, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_dev_label_tool_bar = Qt.QToolBar(self)

        if None:
            self._freq_dev_label_formatter = None
        else:
            self._freq_dev_label_formatter = lambda x: str(x)

        self._freq_dev_label_tool_bar.addWidget(Qt.QLabel("Freq Dev"))
        self._freq_dev_label_label = Qt.QLabel(str(self._freq_dev_label_formatter(self.freq_dev_label)))
        self._freq_dev_label_tool_bar.addWidget(self._freq_dev_label_label)
        self.top_grid_layout.addWidget(self._freq_dev_label_tool_bar, 0, 2, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._es_mode_label_tool_bar = Qt.QToolBar(self)

        if None:
            self._es_mode_label_formatter = None
        else:
            self._es_mode_label_formatter = lambda x: str(x)

        self._es_mode_label_tool_bar.addWidget(Qt.QLabel("EnduroSat UHF II Mode : "))
        self._es_mode_label_label = Qt.QLabel(str(self._es_mode_label_formatter(self.es_mode_label)))
        self._es_mode_label_tool_bar.addWidget(self._es_mode_label_label)
        self.top_grid_layout.addWidget(self._es_mode_label_tool_bar, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._data_rate_label_tool_bar = Qt.QToolBar(self)

        if None:
            self._data_rate_label_formatter = None
        else:
            self._data_rate_label_formatter = lambda x: str(x)

        self._data_rate_label_tool_bar.addWidget(Qt.QLabel("Data Rate"))
        self._data_rate_label_label = Qt.QLabel(str(self._data_rate_label_formatter(self.data_rate_label)))
        self._data_rate_label_tool_bar.addWidget(self._data_rate_label_label)
        self.top_grid_layout.addWidget(self._data_rate_label_tool_bar, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_socket_pdu_1 = blocks.socket_pdu('UDP_SERVER', '127.0.0.1', '52001', 10000, False)
        self.blocks_message_strobe_0_1_0 = blocks.message_strobe(pmt.dict_add( pmt.make_dict(), pmt.to_pmt('gpio'), pmt.to_pmt({'bank':'FP0', 'attr':'ATR_RX', 'value': 0, 'mask': 1})), 9000)
        self.blocks_message_strobe_0_1 = blocks.message_strobe(pmt.dict_add( pmt.make_dict(), pmt.to_pmt('gpio'), pmt.to_pmt({'bank':'FP0', 'attr':'ATR_0X', 'value': 0, 'mask': 1})), 8500)
        self.blocks_message_strobe_0_0_0 = blocks.message_strobe(pmt.dict_add( pmt.make_dict(), pmt.to_pmt('gpio'), pmt.to_pmt({'bank':'FP0', 'attr':'DDR', 'value': 0x0FFF, 'mask': 0xFFFF})), 8000)
        self.blocks_message_strobe_0_0 = blocks.message_strobe(pmt.dict_add( pmt.make_dict(), pmt.to_pmt('gpio'), pmt.to_pmt({'bank':'FP0', 'attr':'CTRL', 'value': 1, 'mask': 0xFFFF})), 7000)
        self.blocks_message_strobe_0 = blocks.message_strobe(pmt.dict_add( pmt.make_dict(), pmt.to_pmt('gpio'), pmt.to_pmt({'bank':'FP0', 'attr':'ATR_TX', 'value': 1, 'mask': 1})), 10000)
        self.blocks_message_debug_0 = blocks.message_debug(True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_message_strobe_0, 'strobe'), (self.uhd_usrp_sink_0_0, 'command'))
        self.msg_connect((self.blocks_message_strobe_0_0, 'strobe'), (self.uhd_usrp_sink_0_0, 'command'))
        self.msg_connect((self.blocks_message_strobe_0_0_0, 'strobe'), (self.uhd_usrp_sink_0_0, 'command'))
        self.msg_connect((self.blocks_message_strobe_0_1, 'strobe'), (self.uhd_usrp_sink_0_0, 'command'))
        self.msg_connect((self.blocks_message_strobe_0_1_0, 'strobe'), (self.uhd_usrp_sink_0_0, 'command'))
        self.msg_connect((self.blocks_socket_pdu_1, 'pdus'), (self.blocks_message_debug_0, 'print_pdu'))
        self.msg_connect((self.blocks_socket_pdu_1, 'pdus'), (self.uhf_pdu_modulate_0, 'pdus'))
        self.connect((self.blocks_throttle_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.uhd_usrp_sink_0_0, 0))
        self.connect((self.uhf_pdu_modulate_0, 0), (self.blocks_throttle_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "ns_esttc_transmitter")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_es_mode(self):
        return self.es_mode

    def set_es_mode(self, es_mode):
        self.es_mode = es_mode
        self.set_data_rate({self.es_mode == 0: 1200, self.es_mode==1: 2400, self.es_mode==2:4800,self.es_mode==3:9600,self.es_mode==4:9600}.get(True,19200))
        self.set_es_mode_label(self.es_mode)
        self.set_freq_dev({self.es_mode == 0: 600, self.es_mode==1: 600, self.es_mode==2:1200,self.es_mode==3:2400,self.es_mode==4:4800,self.es_mode==5:4800,self.es_mode==6:9600}.get(True,19200))
        self.set_mod_index({self.es_mode == 0: 1, self.es_mode==1: 0.5, self.es_mode==2:0.5,self.es_mode==3:0.5,self.es_mode==4:1,self.es_mode==5:0.5,self.es_mode==6:1}.get(True,2))

    def get_samples_per_symbol(self):
        return self.samples_per_symbol

    def set_samples_per_symbol(self, samples_per_symbol):
        self.samples_per_symbol = samples_per_symbol
        self.set_samp_rate(self.data_rate*self.samples_per_symbol)
        self.set_sensitivity_tx(2*np.math.pi*(self.freq_dev/(self.data_rate*self.samples_per_symbol)))
        self.uhf_pdu_modulate_0.set_fm_samples_per_symbol(self.samples_per_symbol)

    def get_freq_dev(self):
        return self.freq_dev

    def set_freq_dev(self, freq_dev):
        self.freq_dev = freq_dev
        self.set_freq_dev_label(self.freq_dev)
        self.set_sensitivity_tx(2*np.math.pi*(self.freq_dev/(self.data_rate*self.samples_per_symbol)))

    def get_data_rate(self):
        return self.data_rate

    def set_data_rate(self, data_rate):
        self.data_rate = data_rate
        self.set_data_rate_label(self.data_rate)
        self.set_samp_rate(self.data_rate*self.samples_per_symbol)
        self.set_sensitivity_tx(2*np.math.pi*(self.freq_dev/(self.data_rate*self.samples_per_symbol)))
        self.uhf_pdu_modulate_0.set_fm_baud(self.data_rate)

    def get_sensitivity_tx(self):
        return self.sensitivity_tx

    def set_sensitivity_tx(self, sensitivity_tx):
        self.sensitivity_tx = sensitivity_tx
        self.set_sensitivity_label(self.sensitivity_tx)

    def get_mod_index(self):
        return self.mod_index

    def set_mod_index(self, mod_index):
        self.mod_index = mod_index
        self.set_mod_index_label(self.mod_index)
        self.uhf_pdu_modulate_0.set_fm_modulation_index(self.mod_index)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.uhd_usrp_sink_0_0.set_normalized_gain(self.tx_gain, 0)

    def get_sensitivity_label(self):
        return self.sensitivity_label

    def set_sensitivity_label(self, sensitivity_label):
        self.sensitivity_label = sensitivity_label
        Qt.QMetaObject.invokeMethod(self._sensitivity_label_label, "setText", Qt.Q_ARG("QString", str(self._sensitivity_label_formatter(self.sensitivity_label))))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.uhd_usrp_sink_0_0.set_samp_rate(self.samp_rate)

    def get_mod_index_label(self):
        return self.mod_index_label

    def set_mod_index_label(self, mod_index_label):
        self.mod_index_label = mod_index_label
        Qt.QMetaObject.invokeMethod(self._mod_index_label_label, "setText", Qt.Q_ARG("QString", str(self._mod_index_label_formatter(self.mod_index_label))))

    def get_freq_dev_label(self):
        return self.freq_dev_label

    def set_freq_dev_label(self, freq_dev_label):
        self.freq_dev_label = freq_dev_label
        Qt.QMetaObject.invokeMethod(self._freq_dev_label_label, "setText", Qt.Q_ARG("QString", str(self._freq_dev_label_formatter(self.freq_dev_label))))

    def get_es_mode_label(self):
        return self.es_mode_label

    def set_es_mode_label(self, es_mode_label):
        self.es_mode_label = es_mode_label
        Qt.QMetaObject.invokeMethod(self._es_mode_label_label, "setText", Qt.Q_ARG("QString", str(self._es_mode_label_formatter(self.es_mode_label))))

    def get_data_rate_label(self):
        return self.data_rate_label

    def set_data_rate_label(self, data_rate_label):
        self.data_rate_label = data_rate_label
        Qt.QMetaObject.invokeMethod(self._data_rate_label_label, "setText", Qt.Q_ARG("QString", str(self._data_rate_label_formatter(self.data_rate_label))))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.uhd_usrp_sink_0_0.set_center_freq(self.center_freq, 0)




def main(top_block_cls=ns_esttc_transmitter, options=None):

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