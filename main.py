import sys

from PySide6.QtCore import Qt, QPointF, QRectF, QStandardPaths, QDir
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QDialog, QMessageBox, QTabWidget
from PySide6.QtGui import QCursor, QKeyEvent, QMouseEvent, QPaintEvent, QPainter, QColor, QPen, QPixmap, QImageWriter
from PIL import ImageGrab
from PIL.ImageQt import ImageQt
import cv2
import numpy as np

class Snipping(QWidget):
    def __init__(self, main: "ScreenshotMenu" = None) -> None:
        super(Snipping, self).__init__()
        self.main = main
        
        screen_size = self.screen().size()
        screen_width, screen_height = screen_size.width(), screen_size.height()
        
        self.setGeometry(0, 0, screen_width, screen_height)
        self.snipping = False
        self.begin = QPointF()
        self.end = QPointF()
        
    def take_screenshot(self):
        self.showFullScreen()
        self.snipping = True
        self.setWindowOpacity(0.3)
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        self.show()
        
    def paintEvent(self, event: QPaintEvent) -> None:
        if self.snipping:
            color = (128, 128, 255, 100)
            lw = 3
            opacity = 0.3
        else:
            self.begin = QPointF()
            self.end = QPointF()
            color = (0, 0, 0, 0)
            lw = 0
            opacity = 0
            
            
        self.setWindowOpacity(opacity)
        painter = QPainter(self)
        painter.setPen(QPen(QColor('black'), lw))
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
        img = ImageGrab.grab(bbox = (0, 0, 100, 50))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
        cv2.imwrite("lol.png", img)
        self.snipping = False
        QApplication.restoreOverrideCursor()
        x, y = (min(self.begin.x(), self.end.x()), max(self.begin.x(), self.end.x())), (min(self.begin.y(), self.end.y()), max(self.begin.y(), self.end.y()))
        
        self.repaint()
        QApplication.processEvents()
        image = ImageGrab.grab(bbox=(x[0], y[0], x[1], y[1]))
        # QApplication.processEvents()
        # img = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
        
        self.main.update_screenshot(image)
        
        self.close()
        
class ScreenshotMenu(QWidget):    
    def __init__(self, main_window = None) -> None:
        super(ScreenshotMenu, self).__init__()
        
        self.main_window = main_window
        
        self.screenshot = QLabel(self)
        self.screenshot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.screenshot.setAlignment(Qt.AlignCenter)
        
        geometry = self.screen().geometry()
        self.screenshot.setMinimumSize(geometry.width() / 8, geometry.height() / 8)
        
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
        
        self.snipping_tool = Snipping(self)
        
    def new_screenshot(self):
        pass
    
    def area_screenshot(self):
        self.snipping_tool.take_screenshot()
    
    def save_screenshot(self):
        pixmap = self.screenshot.pixmap()
        
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
        if not pixmap.save(file_name):
            path = QDir.toNativeSeparators(file_name)
            QMessageBox.warning(
                self,
                "Save Error",
                f"The image could not be saved to {path}."
            )
    
    def update_screenshot(self, img):
        image = ImageQt(img)
        pixmap = QPixmap.fromImage(image)
        self.screenshot.setPixmap(
            pixmap.scaled(
                self.screenshot.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

class MainWidget(QTabWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        
        self.screenshot = ScreenshotMenu(self)
        self.addTab(self.screenshot, "Screenshot")
        
        self.setWindowTitle("Screenshot Tool")
        self.resize(500, 400)

def main() -> None:
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
        
    app.exec()

if __name__ == "__main__":
    main()