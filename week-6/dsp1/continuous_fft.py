from PySide6.QtWidgets import QApplication, QMainWindow
import pyaudio
import pyqtgraph as pg
import sys
import numpy as np

import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


FS = 44100  # Hz
CHUNKSZ = 1024  # samples


class MicrophoneRecorder():
    def __init__(self, signal):
        self.signal = signal
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=FS,
                                  input=True,
                                  frames_per_buffer=CHUNKSZ)

    def read(self):
        data = self.stream.read(CHUNKSZ)
        # y = np.fromstring(data_fashionmnist, 'int16')
        y = np.frombuffer(data, 'int16')
        self.signal.emit(y)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


class MainWindow(QMainWindow):
    read_collected = pg.Qt.QtCore.Signal(np.ndarray)

    def __init__(self):
        super(MainWindow, self).__init__()

        self.win = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.win)
        self.win.setWindowTitle('Spectrum Analyzer')

        self.waveform = self.win.addPlot(title='Waveform', row=1, col=1)
        self.waveform.setYRange(0, 255, padding=0)
        self.waveform.setXRange(0, 2 * CHUNKSZ, padding=0.005)
        self.waveform_plot = self.waveform.plot(pen='c', width=3)

        self.spectrum = self.win.addPlot(title='Spectrum', row=2, col=1)
        self.spectrum.setLogMode(x=True, y=True)
        self.spectrum.setYRange(-4, 4, padding=0)
        self.spectrum.setXRange(np.log10(20), np.log10(FS / 2), padding=0.005)
        self.spectrum_plot = self.spectrum.plot(pen='m', width=3)

    def draw(self, chunk):
        x = np.arange(0, 2 * CHUNKSZ, 2)
        y = chunk - np.min(chunk)
        y = y / np.max(y) * 255
        self.waveform_plot.setData(x, y)

        f = np.linspace(0, FS / 2, int(CHUNKSZ / 2))
        window =  np.hanning(CHUNKSZ)
        spec = np.fft.rfft(chunk * window) / CHUNKSZ
        psd = abs(spec)
        psd = psd[:int(CHUNKSZ / 2)]
        self.spectrum_plot.setData(f, psd)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.read_collected.connect(w.draw)
    w.show()

    mic = MicrophoneRecorder(w.read_collected)
    # time (seconds) between reads
    interval = FS / CHUNKSZ
    t = pg.Qt.QtCore.QTimer()
    t.timeout.connect(mic.read)
    t.start(1000 / interval)  # QTimer takes ms

    app.exec()
    mic.close()
