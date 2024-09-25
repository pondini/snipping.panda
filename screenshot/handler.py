from typing import Callable, Tuple, List

from PySide6.QtCore import Qt, QPointF, QRectF, QRect, QPoint
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QKeyEvent, QMouseEvent, QPaintEvent, QPainter, QColor, QPen, QPixmap, QScreen, QImage

from utils import no_callback

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
