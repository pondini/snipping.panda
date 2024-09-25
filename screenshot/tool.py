import time
from typing import Callable, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QCursor, QPixmap, QScreen
from PIL import ImageGrab
from PIL.ImageQt import fromqpixmap
from PIL.Image import Image

from screenshot.handler import ScreenHandler
from utils import no_callback

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
        
