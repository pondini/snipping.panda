import time
from typing import Callable

from PySide6.QtCore import Qt, QPointF, QRectF, QStandardPaths, QDir
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QDialog, QMessageBox
from PySide6.QtGui import QCursor, QKeyEvent, QMouseEvent, QPaintEvent, QPainter, QColor, QPen, QPixmap, QImageWriter
from PIL import ImageGrab
from PIL.ImageQt import ImageQt
import cv2
import numpy as np

class ScreenshotTool(QWidget):
    def __init__(self, outer: QWidget = None, update_pixmap: Callable = None) -> None:
        super(ScreenshotTool, self).__init__()
        self.outer = outer
        
        self.update_pixmap = update_pixmap
        
        screen_size = self.screen().size()
        self.screen_width, self.screen_height = screen_size.width(), screen_size.height()
        
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        self.snipping = False
        
    def take_full_screenshot(self):
        screen = QApplication.primaryScreen()
        window = self.windowHandle()
        
        if window:
            screen = window.screen()
            
        if not screen:
            return
        
        self.outer.hide()
        time.sleep(0.3)        
        image = ImageGrab.grab(bbox=(0, 0, self.screen_width, self.screen_height))
        self.outer.show()
            
        return image
        
    def take_area_screenshot(self):
        self.begin = QPointF()
        self.end = QPointF()
        self.snipping = True
        
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        self._image = self.take_full_screenshot()
        img = ImageQt(self._image)
        self._pixmap = QPixmap.fromImage(img)
        
        self.showFullScreen()
        
    def paintEvent(self, event: QPaintEvent) -> None:
        if self.snipping:
            # color of the inner rect
            color = (128, 128, 255, 25)
            lw = 3
            opacity = 1
        else:
            self.begin = QPointF()
            self.end = QPointF()
            color = (0, 0, 0, 0)
            lw = 0
            opacity = 0        
        
        self.setWindowOpacity(opacity)
        
        white_layer = QPixmap(self.screen_width, self.screen_height)
        white_layer.fill(QColor(255, 255, 255, 50))
        
        painter = QPainter(self)  
        painter.drawPixmap(self.rect(), self._pixmap)
        painter.drawPixmap(self.rect(), white_layer)
        painter.setPen(QPen(QColor('white'), lw))
        painter.setBrush(QColor(*color))
        rect = QRectF(self.begin, self.end)
        painter.drawRect(rect)
        
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            
        event.accept()
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.begin = event.globalPosition()
        self.end = self.begin
        self.update()
        
    def mouseMoveEvent(self, event: QMouseEvent) -> None: 
        self.end = event.globalPosition()
        self.update()
        
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.snipping = False
        QApplication.restoreOverrideCursor()
        x, y = (min(self.begin.x(), self.end.x()), max(self.begin.x(), self.end.x())), (min(self.begin.y(), self.end.y()), max(self.begin.y(), self.end.y()))
        
        self.repaint()
        QApplication.processEvents()
        image = self._image.crop((x[0], y[0], x[1], y[1]))
        
        if self.update_pixmap:
            self.update_pixmap(image)
        
        self.close()
        
class ScreenshotMenu(QWidget):    
    def __init__(self, main_window = None) -> None:
        super(ScreenshotMenu, self).__init__()
        
        self.main_window = main_window
        
        self.screenshot = QLabel(self)
        self.screenshot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.screenshot.setAlignment(Qt.AlignCenter)
        self.image = None
        
        self.geometry = self.screen().geometry()
        self.screenshot.setMinimumSize(self.geometry.width() / 8, self.geometry.height() / 8)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.screenshot)
        
        buttons = QHBoxLayout()
        self.new = QPushButton("New", self)
        self.new.clicked.connect(self.new_screenshot)
        
        self.area = QPushButton("Area", self)
        self.area.clicked.connect(self.area_screenshot)
        
        self.save = QPushButton("Save", self)
        self.save.clicked.connect(self.save_screenshot)
        
        buttons.addWidget(self.new)
        buttons.addWidget(self.area)
        buttons.addWidget(self.save)
        
        main_layout.addLayout(buttons)
        
        self.screenshot_tool = ScreenshotTool(outer=self.main_window, update_pixmap=self.update_screenshot)
        
    def new_screenshot(self):
        image = self.screenshot_tool.take_full_screenshot()
        self.update_screenshot(image)
    
    def area_screenshot(self):
        self.screenshot_tool.take_area_screenshot()
    
    def save_screenshot(self):        
        file_format = "png"
        
        initial_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation)
        if not initial_path:
            initial_path = QDir.currentPath()
            
        initial_path += f"/untitled.{file_format}"
        
        file_dialog = QFileDialog(self, "Save As", initial_path)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setDirectory(initial_path)
        
        mime_types = [bf.data().decode('utf8') for bf in QImageWriter.supportedMimeTypes()]
        file_dialog.setMimeTypeFilters(mime_types)
        file_dialog.selectMimeTypeFilter("image/" + file_format)
        file_dialog.setDefaultSuffix(file_format)
        if file_dialog.exec() != QDialog.Accepted:
            return
        
        file_name = file_dialog.selectedFiles()[0]
        
        if not self.image:
            return
        
        img = cv2.cvtColor(np.array(self.image), cv2.COLOR_BGR2RGB)
        if not cv2.imwrite(filename=file_name, img=img):
            path = QDir.toNativeSeparators(file_name)
            QMessageBox.warning(
                self,
                "Save Error",
                f"The image could not be saved to {path}."
            )
    
    def update_screenshot(self, img):
        self.image = img
        
        image = ImageQt(img)
        pixmap = QPixmap.fromImage(image)
        self.screenshot.setPixmap(
            pixmap.scaled(
                self.screenshot.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )