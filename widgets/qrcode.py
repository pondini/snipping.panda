from pathlib import Path
from urllib.parse import urlparse
import webbrowser

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QCursor
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QApplication
from PIL.ImageQt import ImageQt
import cv2
import numpy as np
from PIL import Image

from widgets.screenshot import ScreenshotTool

class QRCodeReaderMenu(QWidget):
    def __init__(self, main = None):
        super(QRCodeReaderMenu, self).__init__()
        self.main_window = main
        
        self.screenshot_tool = ScreenshotTool(outer=self.main_window, image_callback=self.update_qr_code)
        
        self.qr_code_image_label = QLabel(self)
        self.qr_code_image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.qr_code_image_label.setAlignment(Qt.AlignCenter)
        
        geometry = self.screen().geometry()
        self.qr_code_image_label.setMinimumSize(geometry.width() / 8, geometry.height() / 8)
        
        qr_code_text_layout = QHBoxLayout()
        
        self.qr_code_text_label = QTextEdit(self)
        self.qr_code_text_label.setReadOnly(True)
        self.qr_code_text_label.setMaximumHeight(30)
        self.qr_code_text_label.setVisible(False)
        
        # self.qr_code_copy_button = QPushButton("C", self)
        # self.qr_code_copy_button.setMaximumWidth(30)
        # self.qr_code_copy_button.setVisible(False)
        
        qr_code_text_layout.addWidget(self.qr_code_text_label)
        # qr_code_text_layout.addWidget(self.qr_code_copy_button)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.qr_code_image_label)
        # main_layout.addWidget(self.qr_code_text_label)
        main_layout.addLayout(qr_code_text_layout)
        
        buttons = QHBoxLayout()
        self.new = QPushButton("Crop QR", self)
        self.new.setMaximumWidth(80)
        self.new.clicked.connect(self.crop_qr)
        
        buttons.addWidget(self.new)
        
        main_layout.addLayout(buttons)
        
    def uri_validator(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except AttributeError:
            return False
        
    def crop_qr(self):
        self.screenshot_tool.take_area_screenshot()
        
    def update_qr_code(self, img):
        self.image = img
        
        decoder = cv2.QRCodeDetector()
        retval, info, bboxes, codes = decoder.detectAndDecodeMulti(np.array(img))
        
        if not retval:            
            path = Path(__file__).resolve().parent.parent
            no_qr = Image.open(f"{path}/static/no_qr_code.png")
            
            self.set_pixmap(no_qr)
            
            self.qr_code_text_label.setText(None)
            self.qr_code_text_label.setVisible(False)
            # self.qr_code_copy_button.setVisible(False)
            
            return
        
        img = cv2.cvtColor(np.array(self.image), cv2.COLOR_BGR2RGB)
        
        # currently only one qr code supported
        index = 0
        
        self.qr_code_text_label.setText(info[index])
        self.qr_code_text_label.mousePressEvent = self.copy_link
        self.qr_code_text_label.setVisible(True)
        # self.qr_code_copy_button.setVisible(True)
        
        top_left = (int(bboxes[index][0][0]), int(bboxes[index][0][1]))
        bottom_right = (int(bboxes[index][2][0]), int(bboxes[index][2][1]))
        
        img = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        image = Image.fromarray(img)
        self.set_pixmap(image)
        
        if not self.uri_validator(info[index]):
            self.qr_code_image_label.setCursor(QCursor(Qt.CursorShape.ForbiddenCursor))
            return
        
        self.qr_code_image_label.mouseDoubleClickEvent = self.open_link
        self.qr_code_image_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
    def open_link(self, event):       
        text = self.qr_code_text_label.toPlainText()
        
        if not self.uri_validator(text):
            return
        
        webbrowser.open_new_tab(text)
        
    def copy_link(self, event):
        text = self.qr_code_text_label.toPlainText()
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        
    def set_pixmap(self, img):
        image = ImageQt(img)
        pixmap = QPixmap.fromImage(image)
            
        self.qr_code_image_label.setPixmap(
            pixmap.scaled(
                self.qr_code_image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        
        
        