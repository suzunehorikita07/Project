## Project Name : Image Processing

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PIL import Image
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import os


class ImageApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Smart Image Editor")
        self.setGeometry(100, 100, 1300, 700)

        self.image = None
        self.original_image = None
        self.base_image = None
        self.image_path = None
        self.brightness = 0
        self.contrast = 1.0
        self.dark_theme = True
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.save_path = None
        self.edited_folder = os.path.join(os.path.dirname(__file__), "edited_photos")
        os.makedirs(self.edited_folder, exist_ok=True)

        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        if self.dark_theme:
            main_widget.setStyleSheet("background-color: #1e1e1e;")
        else:
            main_widget.setStyleSheet("background-color: #f0f0f0;")

        main_layout = QVBoxLayout()

        # Top layout: sidebar + image
        top_layout = QHBoxLayout()

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(280)
        self.update_sidebar_style()

        sidebar_layout = QVBoxLayout()

        # Theme switch
        self.theme_btn = QPushButton("Dark Theme" if self.dark_theme else "Light Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)

        # Buttons with icons
        btn_upload = QPushButton("Upload Image")
        btn_upload.clicked.connect(self.load_image)

        btn_gray = QPushButton("Grayscale")
        btn_gray.clicked.connect(self.apply_grayscale)

        btn_blur = QPushButton("Blur")
        btn_blur.clicked.connect(self.apply_blur)

        btn_edge = QPushButton("Edge Detection")
        btn_edge.clicked.connect(self.apply_edge)

        btn_detect = QPushButton("Face Detection")
        btn_detect.clicked.connect(self.apply_detection)

        btn_rotate_cw = QPushButton("Rotate CW")
        btn_rotate_cw.clicked.connect(self.rotate_cw)

        btn_rotate_ccw = QPushButton("Rotate CCW")
        btn_rotate_ccw.clicked.connect(self.rotate_ccw)

        btn_flip_h = QPushButton("Flip Horizontal")
        btn_flip_h.clicked.connect(self.flip_horizontal)

        btn_flip_v = QPushButton("Flip Vertical")
        btn_flip_v.clicked.connect(self.flip_vertical)

        btn_invert = QPushButton("Invert Colors")
        btn_invert.clicked.connect(self.invert_colors)

        btn_sepia = QPushButton("Sepia")
        btn_sepia.clicked.connect(self.apply_sepia)

        btn_sharpen = QPushButton("Sharpen")
        btn_sharpen.clicked.connect(self.apply_sharpen)

        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self.reset_image)

        btn_download = QPushButton("Download Image")
        btn_download.clicked.connect(self.download_image)

        # Sliders
        brightness_label = QLabel("Brightness")
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.adjust_brightness_contrast)

        contrast_label = QLabel("Contrast")
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.adjust_brightness_contrast)

        for widget in [self.theme_btn, btn_upload, btn_gray, btn_blur, btn_edge, btn_detect, btn_rotate_cw, btn_rotate_ccw, btn_flip_h, btn_flip_v, btn_invert, btn_sepia, btn_sharpen, btn_reset, btn_download, brightness_label, self.brightness_slider, contrast_label, self.contrast_slider]:
            if isinstance(widget, QPushButton):
                widget.setMinimumHeight(45)
            sidebar_layout.addWidget(widget)

        sidebar_layout.addStretch()
        self.sidebar.setLayout(sidebar_layout)

        # Image Display Area
        self.image_label = QLabel("Upload an Image or Drag & Drop")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.update_image_label_style()
        self.image_label.setAcceptDrops(True)
        self.image_label.installEventFilter(self)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setMinimumSize(400, 300)

        top_layout.addWidget(self.sidebar)
        top_layout.addWidget(self.image_label)

        # Histogram Panel
        self.histogram_label = QLabel("Histogram")
        self.histogram_label.setAlignment(Qt.AlignCenter)
        self.update_histogram_style()
        self.histogram_label.setFixedHeight(200)
        self.histogram_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.update_status_style()

        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.histogram_label)
        main_layout.addWidget(self.status_label)

        main_widget.setLayout(main_layout)

    def update_sidebar_style(self):
        if self.dark_theme:
            style = """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2e2e3e, stop:1 #1a1a2a);
                border: 1px solid #444;
                border-radius: 10px;
            }
            QPushButton {
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a4a5a, stop:1 #2a2a3a);
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5a5a6a, stop:1 #3a3a4a);
                border: 1px solid #666;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a4a, stop:1 #1a1a2a);
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;  
            }
            """
        else:
            style = """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f0f0, stop:1 #e0e0e0);
                border: 1px solid #ccc;
                border-radius: 10px;
            }
            QPushButton {
                color: #333333;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #e8e8e8);
                border: 1px solid #bbb;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8f8f8, stop:1 #d8d8d8);
                border: 1px solid #aaa;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e0e0e0, stop:1 #c0c0c0);
            }
            QLabel {
                color: #333333;
                font-size: 12px;
                font-weight: bold;
            }
            """
        self.sidebar.setStyleSheet(style)

    def update_image_label_style(self):
        if self.dark_theme:
            style = """
            QLabel {
                background-color: #2b2b2b;
                color: white;
                font-size: 18px;
                border: 2px dashed #444;
            }
            """
        else:
            style = """
            QLabel {
                background-color: #e8e8e8;
                color: #333;
                font-size: 18px;
                border: 2px dashed #888;
            }
            """
        self.image_label.setStyleSheet(style)

    def update_histogram_style(self):
        if self.dark_theme:
            style = """
            QLabel {
                background-color: #2b2b2b;
                color: white;
                font-size: 14px;
                border: 1px solid #444;
            }
            """
        else:
            style = """
            QLabel {
                background-color: #e8e8e8;
                color: #333;
                font-size: 14px;
                border: 1px solid #888;
            }
            """
        self.histogram_label.setStyleSheet(style)

    def update_status_style(self):
        if self.dark_theme:
            style = """
            QLabel {
                color: white;
                font-size: 12px;
            }
            """
        else:
            style = """
            QLabel {
                color: #333;
                font-size: 12px;
            }
            """
        self.status_label.setStyleSheet(style)

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.theme_btn.setText("Dark Theme" if self.dark_theme else "Light Theme")
        self.update_sidebar_style()
        self.update_image_label_style()
        self.update_histogram_style()
        self.update_status_style()
        if self.dark_theme:
            self.centralWidget().setStyleSheet("background-color: #1e1e1e;")
            plt.style.use('dark_background')
        else:
            self.centralWidget().setStyleSheet("background-color: #f0f0f0;")
            plt.style.use('default')
        self.update_histogram()

    def adjust_brightness_contrast(self):
        if self.base_image is not None:
            self.brightness = self.brightness_slider.value()
            self.contrast = self.contrast_slider.value() / 100.0
            self.image = cv2.convertScaleAbs(self.base_image, alpha=self.contrast, beta=self.brightness)
            self.display_image(self.image)

    def apply_detection(self):
        if self.image is not None:
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            for (x, y, w, h) in faces:
                cv2.rectangle(self.image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            self.display_image(self.image)
        else:
            self.status_label.setText("Load an image first")

    def rotate_cw(self):
        if self.base_image is not None:
            self.base_image = cv2.rotate(self.base_image, cv2.ROTATE_90_CLOCKWISE)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def rotate_ccw(self):
        if self.base_image is not None:
            self.base_image = cv2.rotate(self.base_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def flip_horizontal(self):
        if self.base_image is not None:
            self.base_image = cv2.flip(self.base_image, 1)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def flip_vertical(self):
        if self.base_image is not None:
            self.base_image = cv2.flip(self.base_image, 0)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def invert_colors(self):
        if self.base_image is not None:
            self.base_image = cv2.bitwise_not(self.base_image)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def apply_sepia(self):
        if self.base_image is not None:
            kernel = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
            self.base_image = cv2.transform(self.base_image, kernel)
            self.base_image = np.clip(self.base_image, 0, 255).astype(np.uint8)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def apply_sharpen(self):
        if self.base_image is not None:
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            self.base_image = cv2.filter2D(self.base_image, -1, kernel)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def reset_image(self):
        if self.original_image is not None:
            self.base_image = self.original_image.copy()
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def eventFilter(self, source, event):
        if source == self.image_label:
            if event.type() == QEvent.DragEnter:
                if event.mimeData().hasUrls():
                    event.accept()
                else:
                    event.ignore()
                return True
            elif event.type() == QEvent.Drop:
                files = [u.toLocalFile() for u in event.mimeData().urls()]
                if files:
                    self.image_path = files[0]
                    self.image = cv2.imread(files[0])
                    self.original_image = self.image.copy()
                    self.base_image = self.image.copy()
                    self.adjust_brightness_contrast()
                    self.status_label.setText(f"Image loaded: {os.path.basename(files[0])}")
                return True
        return super().eventFilter(source, event)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName()
        if path:
            self.image_path = path
            self.image = cv2.imread(path)
            self.original_image = self.image.copy()
            self.base_image = self.image.copy()
            self.adjust_brightness_contrast()
            self.status_label.setText(f"Image loaded: {os.path.basename(path)}")

    def display_image(self, img):
        if img is None:
            return

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        h, w, ch = img.shape
        bytes_per_line = ch * w
        qt_img = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)

        pix = QPixmap.fromImage(qt_img)
        self.image_label.setPixmap(pix.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio
        ))
        self.update_histogram()

    def update_histogram(self):
        if self.image is None:
            self.histogram_label.setPixmap(QPixmap())
            return

        fig, ax = plt.subplots(figsize=(6, 2))
        if len(self.image.shape) == 2:
            ax.hist(self.image.ravel(), bins=256, range=(0, 256), color='gray', alpha=0.7)
        else:
            colors = ('b', 'g', 'r')
            for i, color in enumerate(colors):
                hist = cv2.calcHist([self.image], [i], None, [256], [0, 256])
                ax.plot(hist, color=color)

        ax.set_title('Histogram')
        ax.set_xlabel('Pixel Value')
        ax.set_ylabel('Frequency')
        fig.canvas.draw()
        w, h = fig.canvas.get_width_height()
        buf = fig.canvas.buffer_rgba()
        qimg = QImage(buf, w, h, QImage.Format_RGBA8888)
        pix = QPixmap.fromImage(qimg)
        self.histogram_label.setPixmap(pix.scaled(self.histogram_label.width(), self.histogram_label.height(), Qt.KeepAspectRatio))
        plt.close(fig)

    def apply_grayscale(self):
        if self.base_image is not None:
            self.base_image = cv2.cvtColor(self.base_image, cv2.COLOR_BGR2GRAY)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def apply_blur(self):
        if self.base_image is not None:
            self.base_image = cv2.GaussianBlur(self.base_image, (15, 15), 0)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    def apply_edge(self):
        if self.base_image is not None:
            self.base_image = cv2.Canny(self.base_image, 100, 200)
            self.adjust_brightness_contrast()
        else:
            self.status_label.setText("Load an image first")

    # def apply_bg_remove(self):
    #     if self.image_path:
    #         input_image = Image.open(self.image_path)
    #         output = remove(input_image)
    #         self.base_image = cv2.cvtColor(np.array(output), cv2.COLOR_RGBA2RGB)
    #         self.adjust_brightness_contrast()

    def download_image(self):
        if self.image is not None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"edited_image_{timestamp}.png"
            path = os.path.join(self.edited_folder, filename)
            cv2.imwrite(path, self.image)
            self.save_path = path
            self.status_label.setText(f"Image downloaded to: {path}")
            # Open the folder
            os.startfile(self.edited_folder)
        else:
            self.status_label.setText("No image to download")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Dark Theme
    app.setStyle("Fusion")

    window = ImageApp()
    window.show()

    sys.exit(app.exec_())
    
    ## python image.py
