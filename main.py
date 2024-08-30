import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout, QPushButton

class Screenshot(QWidget):
    def __init__(self):
        super(Screenshot, self).__init__()        
        self.screenshot = QLabel(self)
        self.screenshot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.screenshot.setAlignment(Qt.AlignCenter)
        
        geometry = self.screen().geometry()
        self.screenshot.setMinimumSize(geometry.width() / 8, geometry.height() / 8)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.screenshot)
        
        buttons = QHBoxLayout(self)
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
        
    def new_screenshot(self):
        pass
    
    def area_screenshot(self):
        pass
    
    def save_screenshot(self):
        pass

def main():
    app = QApplication(sys.argv)
    screenshot = Screenshot()
    screenshot.show()
    
    app.exec()

if __name__ == "__main__":
    main()