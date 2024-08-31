import sys

from PySide6.QtWidgets import QApplication, QTabWidget

from widgets.screenshot import ScreenshotMenu
from widgets.qrcode import QRCodeReaderMenu

class MainWidget(QTabWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        
        self.screenshot = ScreenshotMenu(self)
        self.addTab(self.screenshot, "Screenshot")
        
        self.qrcode_reader = QRCodeReaderMenu(self)
        self.addTab(self.qrcode_reader, "QRCode Reader")
        
        self.setWindowTitle("Screenshot Tool")
        self.resize(500, 400)

def main() -> None:
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
        
    app.exec()

if __name__ == "__main__":
    main()