import numpy as np
import pyqtgraph as pg
import pyaudio
from pyqtgraph.Qt import QtCore, QtWidgets


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


class SpectrogramWidget(pg.PlotWidget):
    read_collected = QtCore.Signal(np.ndarray)

    def __init__(self):
        super(SpectrogramWidget, self).__init__()
        self.img = pg.ImageItem()
        self.addItem(self.img)

        self.ring_buffer_size = 64
        self.img_array = np.zeros((self.ring_buffer_size, int(CHUNKSZ / 2) + 1))

        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0, 255, 255, 255],
                          [255, 255, 0, 255],
                          [0, 0, 0, 255],
                          [0, 0, 255, 255],
                          [255, 0, 0, 255]],
                         dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.img.setLookupTable(lut)
        self.img.setLevels([-50, 40])
        self.img.scale()

        self.setLabel('left', 'Frequency', units='Hz')

        self.win = np.hanning(CHUNKSZ)
        self.show()

    def update(self, chunk):
        # normalized, windowed frequencies in data_fashionmnist chunk
        spec = np.fft.rfft(chunk * self.win) / CHUNKSZ
        # get magnitude
        psd = abs(spec)
        # convert to dB scale
        psd = 20 * np.log10(psd)

        # roll down one and replace leading edge with new data_fashionmnist
        self.img_array = np.roll(self.img_array, -1, 0)
        self.img_array[-1:] = psd

        self.img.setImage(self.img_array, autoLevels=False)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = SpectrogramWidget()
    w.read_collected.connect(w.update)

    mic = MicrophoneRecorder(w.read_collected)

    # time (seconds) between reads
    interval = FS / CHUNKSZ
    t = QtCore.QTimer()
    t.timeout.connect(mic.read)
    t.start(1000 / interval)  # QTimer takes ms

    app.exec_()
    mic.close()
