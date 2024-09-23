import time
from typing import Callable, Tuple, List

from PySide6.QtCore import Qt, QPointF, QRectF, QStandardPaths, QDir, QRect, QPoint, QSize
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QDialog, QMessageBox, QComboBox
from PySide6.QtGui import QCursor, QKeyEvent, QMouseEvent, QPaintEvent, QPainter, QColor, QPen, QPixmap, QImageWriter, QScreen, QImage, QDesktopServices
from PIL import ImageGrab
from PIL.ImageQt import ImageQt, fromqpixmap
from PIL.Image import Image
import cv2
import numpy as np

def no_callback(**kwargs):
    pass

class ScreenHandler(QWidget):
    def __init__(self, screen: QScreen = None, image_callback: Callable = no_callback, release_event: Callable = no_callback) -> None:
        super(ScreenHandler, self).__init__()
        
        self.setScreen(screen)
        self.setGeometry(screen.geometry())
        
        self._pixmap: QPixmap = None
        self._image: QImage = None
        
        self.top_left: QPoint = self.mapToGlobal(QPoint(0, 0))
        self.bottom_right: QPoint = self.mapToGlobal(QPoint(1920, 1080))
        
        self._x, self._y = self.top_left.toTuple()
        self.screen_width, self.screen_height = self.screen().size().toTuple()
        
        self.begin: QPointF = QPointF()
        self.end: QPointF = QPointF()
        self.snipping: bool = False
        self._image_callback: Callable = image_callback
        self._release: Callable = release_event
        
    def getRect(self) -> Tuple[int, int, int, int]:
        return self._x, self._y, self.screen_width, self.screen_height
    
    def control_border(self, x: Tuple[int, int] | List[int], y: Tuple[int, int] | List[int]) -> Tuple[Tuple[int, int]]:        
        x1, x2 = x
        y1, y2 = y
        
        if x1 < 0:
            x1 = 0
            
        if x2 > self.screen_width:
            x2 = self.screen_width
            
        if y1 < 0:
            y1 = 0
            
        if y2 > self.screen_height:
            y2 = self.screen_height
            
        return (x1, x2), (y1, y2)
    
    def determine_true_corners(self, tl: QPointF, br: QPointF) -> Tuple[Tuple[int, int]]:
        x1, y1 = tl.toTuple()
        x2, y2 = br.toTuple()
        
        x1, x2 = (x1, x2) if x1 < x2 else (x2, x1)
        y1, y2 = (y1, y2) if y1 < y2 else (y2, y1)
        
        (x1, x2), (y1, y2) = self.control_border(x = (x1, x2), y = (y1, y2))
        
        return (x1, y1), (x2, y2)
        
    def paintEvent(self, event: QPaintEvent) -> None:
        if self.snipping:
            # color of the inner rect
            color = (255, 255, 255, 25)
            lw = 3
            opacity = 1
        else:
            self.begin = QPointF()
            self.end = QPointF()
            color = (0, 0, 0, 0)
            lw = 0
            opacity = 0        
        
        self.setWindowOpacity(opacity)
        
        white_layer: QPixmap = QPixmap(self.screen_width, self.screen_height)
        white_layer.fill(QColor(0, 0, 0, 90))
        
        painter: QPainter = QPainter(self)
        painter.drawPixmap(self.rect(), self._pixmap)
        painter.drawPixmap(self.rect(), white_layer)
        painter.setPen(QPen(QColor('white'), lw))
        painter.setBrush(QColor(*color))
        rect: QRectF = QRectF(self.begin, self.end)
        
        painter.drawRect(rect)
        
        p1, p2 = self.determine_true_corners(rect.topLeft(), rect.bottomRight())             
        paint_rect: QRect = QRect(QPoint(*p1), QPoint(*p2))
        
        painter.drawPixmap(paint_rect, self._pixmap.copy(paint_rect))
        
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            QApplication.restoreOverrideCursor()
            self._release()
            
        event.accept()
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.begin: QPointF = event.scenePosition()
        self.end: QPointF = self.begin
        
        self.update()
        
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.begin: QPointF = event.scenePosition()
        
        self.update()
        
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.snipping: bool = False
        QApplication.restoreOverrideCursor()
        
        x, y = [min(self.begin.x(), self.end.x()), max(self.begin.x(), self.end.x())], [min(self.begin.y(), self.end.y()), max(self.begin.y(), self.end.y())]
        
        x, y = self.control_border(x, y)
        
        self.repaint()
        QApplication.processEvents()
        image: QImage = self._image.copy(x[0], y[0], x[1] - x[0], y[1] - y[0])
        
        self._image_callback(image)
        
        self._release()

class ScreenshotTool():
    def __init__(self, outer: QWidget = None, image_callback: Callable = no_callback) -> None:
        self.outer: QWidget = outer
        
        self.screens: List[ScreenHandler] = []
        for screen in QApplication.screens()[:]:            
            screen_handler: ScreenHandler = ScreenHandler(screen = screen, image_callback=image_callback, release_event=self.release_screens)
            
            self.screens.append(screen_handler)
        
    def release_screens(self) -> None:
        for screen in self.screens:
            screen.close()
            
        self.outer.show()
        
    def take_full_screenshot(self, screen: QScreen = None) -> Image:
        self.outer.hide()
        time.sleep(0.3)        
        # image = ImageGrab.grab(bbox=(0, 0, 1920, 1080))
        image: Image = ImageGrab.grab(bbox=None, all_screens=True) if not screen else fromqpixmap(screen.grabWindow())
        self.outer.show()
            
        return image
        
    def take_area_screenshot(self) -> None:        
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        self.outer.hide()
        time.sleep(0.3)
        for screen in self.screens:
            screenshot: QPixmap = screen.screen().grabWindow()
            
            screen._pixmap = screenshot
            screen._image = screenshot.toImage()
            
            screen.snipping = True
            
            screen.showFullScreen()
        
class ScreenshotMenu(QWidget):    
    def __init__(self, main_window: QWidget = None) -> None:
        super(ScreenshotMenu, self).__init__()
        
        self.main_window: QWidget = main_window
        main_layout: QVBoxLayout = QVBoxLayout(self)
        
        self.cb: QComboBox = QComboBox()
        self.cb.setFixedWidth(100)
        self.cb.addItem("All", userData={"exec": self.all_screens_screenshot})
        
        primary: QScreen = QApplication.primaryScreen()
        self.cb.addItem("Primary", userData={"exec": self.specific_screen_screenshot, "screen": primary})
        screens: List[QScreen] = QApplication.screens()
        screens.remove(primary)
        
        for index, screen in enumerate(screens, 2):
            self.cb.addItem(f"Screen {index}", userData={"exec": self.specific_screen_screenshot, "screen": screen})
            
        cb_layout: QHBoxLayout = QHBoxLayout()
        cb_layout.addWidget(self.cb)
        
        self.screenshot: QLabel = QLabel(self)
        self.screenshot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.screenshot.setAlignment(Qt.AlignCenter)
        self.image: QImage = None
        
        self.geometry: QRect = self.screen().geometry()
        self.screenshot.setMinimumSize(self.geometry.width() / 8, self.geometry.height() / 8)
        
        main_layout.addLayout(cb_layout)
        main_layout.addWidget(self.screenshot)
        
        buttons: QHBoxLayout = QHBoxLayout()
        self.new: QPushButton = QPushButton("New", self)
        self.new.clicked.connect(self.new_screenshot)
        
        self.area: QPushButton = QPushButton("Area", self)
        self.area.clicked.connect(self.area_screenshot)
        
        self.save: QPushButton = QPushButton("Save", self)
        self.save.clicked.connect(self.save_screenshot)
        
        buttons.addWidget(self.new)
        buttons.addWidget(self.area)
        buttons.addWidget(self.save)
        
        main_layout.addLayout(buttons)
        
        self.screenshot_tool: ScreenshotTool = ScreenshotTool(outer=self.main_window, image_callback=self.update_screenshot)
        
    def all_screens_screenshot(self) -> None:
        image: Image = self.screenshot_tool.take_full_screenshot()
        self.update_screenshot(image)
    
    def specific_screen_screenshot(self) -> None:
        screen: QScreen = self.cb.currentData().get('screen')
        image: Image = self.screenshot_tool.take_full_screenshot(screen)
        self.update_screenshot(image)
        
    # def new_screenshot(self):
    #     image = self.screenshot_tool.take_full_screenshot()
    #     self.update_screenshot(image)
    
    def new_screenshot(self) -> None:
        _exec: Callable = self.cb.currentData().get("exec")
        _exec()
    
    def area_screenshot(self) -> None:
        self.screenshot_tool.take_area_screenshot()
    
    def save_screenshot(self) -> None:
        if not self.image:
            QMessageBox.information(
                self,
                "Save Image",
                "There is no image to save."
            )
            return
                
        file_format: str = "png"
        
        initial_path: str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        if not initial_path:
            initial_path = QDir.currentPath()
            
        initial_file_name: str = f"{initial_path}/untitled.{file_format}"
        
        file_dialog: QFileDialog = QFileDialog(self, "Save As", initial_file_name)
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        file_dialog.setDirectory(initial_path)
        
        mime_types: List[str] = [bf.data().decode('utf8') for bf in QImageWriter.supportedMimeTypes()]
        file_dialog.setMimeTypeFilters(mime_types)
        file_dialog.selectMimeTypeFilter("image/" + file_format)
        file_dialog.setDefaultSuffix(file_format)
        if file_dialog.exec() != QDialog.Accepted:
            return
        
        file_name: str = file_dialog.selectedFiles()[0]
        
        saved: bool = self.image.save(file_name, quality=10)
        path: str = QDir.toNativeSeparators(file_name)
        
        if not saved:
            QMessageBox.warning(
                self,
                "Save Error",
                f"The image could not be saved to {path}."
            )
            
            return
            
        message_box: QMessageBox = QMessageBox()
        message_box.setIcon(QMessageBox.Icon.Information)
        message_box.setWindowTitle("Save Image")
        message_box.setText(f"The image has been saved.")
        message_box.show()
        button1: QPushButton = message_box.addButton("Open Image", QMessageBox.ButtonRole.ActionRole)
        button1.clicked.connect(lambda: QDesktopServices.openUrl(initial_file_name))
        button2: QPushButton = message_box.addButton("Open Explorer", QMessageBox.ButtonRole.ActionRole)
        button2.clicked.connect(lambda: QDesktopServices.openUrl(initial_path))
        message_box.exec_()

    def update_screenshot(self, img: Image | QImage) -> None:
        if not isinstance(img, QImage):
            img: QImage = ImageQt(img)
        
        self.image: QImage = img
        
        pixmap: QPixmap = QPixmap.fromImage(self.image)
        self.screenshot.setPixmap(
            pixmap.scaled(
                self.screenshot.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
