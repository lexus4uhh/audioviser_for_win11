import sys
import threading
import numpy as np
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

BUFFER_SIZE = 4096
UPDATE_INTERVAL = 20
HIDE_THRESHOLD = 10

class AudioVisualizer:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        
        self.win = pg.GraphicsLayoutWidget(show=True, title="Optimized Audio Visualizer")
        self.win.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        self.win.resize(200, 150)
        self.win.move(1330, 650)
        self.win.setBackground('k')

        self.wave_plot = self.win.addPlot()
        self.wave_plot.setMouseEnabled(x=False, y=False)
        self.wave_plot.hideAxis('bottom')
        self.wave_plot.hideAxis('left')
        self.wave_curve = self.wave_plot.plot(pen='c')
        self.wave_plot.setYRange(-1, 1)

        self.data_buffer = np.zeros(BUFFER_SIZE)
        self.incoming_data = []
        self.lock = threading.Lock()

        self.input_thread = threading.Thread(target=self.read_stdin, daemon=True)
        self.input_thread.start()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(UPDATE_INTERVAL)

    def read_stdin(self):
        """ Runs in a separate thread to prevent GUI freezing """
        for line in sys.stdin:
            try:
                val = float(line.strip())
                with self.lock:
                    self.incoming_data.append(val)
            except ValueError:
                continue

    def update(self):
        mouse_pos = QtGui.QCursor.pos()
        win_geom = self.win.geometry()
        
        detection_zone = win_geom.adjusted(
            -HIDE_THRESHOLD, -HIDE_THRESHOLD, 
            HIDE_THRESHOLD, HIDE_THRESHOLD
        )

        if detection_zone.contains(mouse_pos):
            if self.win.isVisible():
                self.win.hide()
        else:
            if not self.win.isVisible():
                self.win.show()

        if self.incoming_data:
            with self.lock:
                values = np.array(self.incoming_data)
                self.incoming_data = []

            num_new = len(values)
            self.data_buffer = np.roll(self.data_buffer, -num_new)
            self.data_buffer[-num_new:] = values
            
            if self.win.isVisible():
                self.wave_curve.setData(self.data_buffer)

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    viz = AudioVisualizer()
    viz.run()