from typing import Callable, List

from PySide6.QtCore import Qt, QStandardPaths, QDir, QRect
from PySide6.QtWidgets import QWidget, QApplication, QLabel, QSizePolicy, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QDialog, QMessageBox, QComboBox
from PySide6.QtGui import QPixmap, QImageWriter, QScreen, QImage, QDesktopServices
from PIL.ImageQt import ImageQt
from PIL.Image import Image

from screenshot.tool import ScreenshotTool
from utils import save_image

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
        save_image(self, self.image)
    
    # def save_screenshot(self) -> None:
    #     if not self.image:
    #         QMessageBox.information(
    #             self,
    #             "Save Image",
    #             "There is no image to save."
    #         )
    #         return
                
    #     file_format: str = "png"
        
    #     initial_path: str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    #     if not initial_path:
    #         initial_path = QDir.currentPath()
            
    #     initial_file_name: str = f"{initial_path}/untitled.{file_format}"
        
    #     file_dialog: QFileDialog = QFileDialog(self, "Save As", initial_file_name)
    #     file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    #     file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
    #     file_dialog.setDirectory(initial_path)
        
    #     mime_types: List[str] = [bf.data().decode('utf8') for bf in QImageWriter.supportedMimeTypes()]
    #     file_dialog.setMimeTypeFilters(mime_types)
    #     file_dialog.selectMimeTypeFilter("image/" + file_format)
    #     file_dialog.setDefaultSuffix(file_format)
    #     if file_dialog.exec() != QDialog.Accepted:
    #         return
        
    #     file_name: str = file_dialog.selectedFiles()[0]
        
    #     saved: bool = self.image.save(file_name, quality=10)
    #     path: str = QDir.toNativeSeparators(file_name)
        
    #     if not saved:
    #         QMessageBox.warning(
    #             self,
    #             "Save Error",
    #             f"The image could not be saved to {path}."
    #         )
            
    #         return
            
    #     message_box: QMessageBox = QMessageBox()
    #     message_box.setIcon(QMessageBox.Icon.Information)
    #     message_box.setWindowTitle("Save Image")
    #     message_box.setText(f"The image has been saved.")
    #     message_box.show()
    #     button1: QPushButton = message_box.addButton("Open Image", QMessageBox.ButtonRole.ActionRole)
    #     button1.clicked.connect(lambda: QDesktopServices.openUrl(initial_file_name))
    #     button2: QPushButton = message_box.addButton("Open Explorer", QMessageBox.ButtonRole.ActionRole)
    #     button2.clicked.connect(lambda: QDesktopServices.openUrl(initial_path))
    #     message_box.exec_()

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
