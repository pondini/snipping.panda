import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication, QTabWidget
from PySide6.QtGui import QIcon, QPixmap

from screenshot.menu import ScreenshotMenu
from qrcode import QRCodeReaderMenu, QRCodeCreatorMenu

class MainWidget(QTabWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        
        self.screenshot = ScreenshotMenu(self)
        self.addTab(self.screenshot, "Screenshot")
        
        self.qrcode_reader = QRCodeReaderMenu(self)
        self.addTab(self.qrcode_reader, "QRCode Reader")
        
        self.qrcode_creator = QRCodeCreatorMenu(self)
        self.addTab(self.qrcode_creator, "QRCode Creator")
        
        self.setWindowTitle("SnippingPanda")
        self.resize(500, 400)

def main() -> None:
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    
    if getattr(sys, 'frozen', False):
        path = os.path.join(sys._MEIPASS, "files/icon.ico")
    else:
        path = f"{Path(__file__).resolve().parent.parent}/static/icon.ico"

    app.setWindowIcon(QIcon(QPixmap(path)))
    main_widget.setWindowIcon(QIcon(QPixmap(path)))
        
    app.exec()

if __name__ == "__main__":
    main()