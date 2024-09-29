from PySide6.QtCore import Qt, QStandardPaths, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QGroupBox, QLineEdit
from PIL.ImageQt import ImageQt
from PIL import Image

from utils import save_image

class QRCodeCreatorMenu(QWidget):
    def __init__(self, main = None):
        super(QRCodeCreatorMenu, self).__init__()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_done)
        
        self.input = QTextEdit(self)
        self.input.setMaximumHeight(30)
        self.input.setVisible(True)
        self.input.setPlaceholderText("Add url or text content")
        self.input.textChanged.connect(self.update_qr_code)
        
        input_text_layout = QHBoxLayout()
        input_text_layout.addWidget(self.input)
        
        self.input_image = None
        
        self.input_image_button = QPushButton("Upload File")
        self.input_image_button.clicked.connect(self.get_file)
        
        self.input_image_text = QLineEdit()
        self.input_image_text.setReadOnly(True)
        self.input_image_text.textChanged.connect(self.update_qr_code)
        
        self.input_image_delete = QPushButton("X")
        self.input_image_delete.setMaximumWidth(30)
        self.input_image_delete.clicked.connect(self.delete_file)
        
        input_image_layout = QHBoxLayout()
        input_image_layout.addWidget(self.input_image_button)
        input_image_layout.addWidget(self.input_image_text)
        input_image_layout.addWidget(self.input_image_delete)
        
        buttons = QHBoxLayout()
        self.create = QPushButton("Download", self)
        self.create.setMaximumWidth(80)
        self.create.clicked.connect(self.download_qr_code)
        
        buttons.addWidget(self.create)
        
        self.output = QLabel(self)
        self.output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output.setAlignment(Qt.AlignCenter)
        
        self.output_image = None
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.output)
        
        groupbox = QGroupBox("Preview")
        groupbox.setLayout(vbox)
        
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(input_text_layout)
        main_layout.addLayout(input_image_layout)
        main_layout.addWidget(groupbox)
        main_layout.addLayout(buttons)
        
    def get_file(self):
        inital_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        fname = QFileDialog.getOpenFileName(self, 'Open File', inital_path, "Image files (*.jpg *.jpeg *.png)")
        
        path = fname[0]
        
        if path is None or path == '':
            return
        
        img = Image.open(f"{path}")
        
        image = ImageQt(img)
        self.input_image = QPixmap.fromImage(image)
        self.input_image_text.setText(path)
        
    def delete_file(self):
        self.input_image = None
        self.input_image_text.setText("")
        
    def update_qr_code(self):
        self.timer.start(1500)
        
    def timer_done(self):
        self.timer.stop()
        
        if self.input.toPlainText() == "" or self.input.toPlainText() == None:
            return
        
        print("Create QR Code here")
        if self.input_image:
            self.output_image = self.input_image.toImage()
            
            self.output.setPixmap(
                self.input_image.scaled(
                    self.output.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        
    def download_qr_code(self):
        msgs = {
            "information_title": "Save QRCode",
            "information_text": "There is no generated QRCode to save.",
            "warning_title": "Save Error",
            "warning_text": "The QRCode could not be saved.",
            "save_title": "Save QRCode",
            "save_text": "The QRCode has been saved.",
            "open_button_text": "Open QRCode"
        }
        
        save_image(self, self.output_image, msgs)
        