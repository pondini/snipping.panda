from typing import List, Dict

from PySide6.QtCore import QStandardPaths, QDir
from PySide6.QtWidgets import QPushButton, QFileDialog, QDialog, QMessageBox, QWidget
from PySide6.QtGui import QImageWriter, QDesktopServices, QImage

def save_image(parent: QWidget, image: QImage, msgs: Dict[str, str]) -> None:
    if not isinstance(msgs, dict):
        msgs = dict()
        
    if not image:
        QMessageBox.information(
            parent,
            msgs.get("information_title", "Save Image"),
            msgs.get("information_text", "There is no image to save.")
        )
        return
            
    file_format: str = "png"
    
    initial_path: str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    if not initial_path:
        initial_path = QDir.currentPath()
        
    initial_file_name: str = f"{initial_path}/untitled.{file_format}"
    
    file_dialog: QFileDialog = QFileDialog(parent, "Save As", initial_file_name)
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
    
    saved: bool = image.save(file_name, quality=10)
    path: str = QDir.toNativeSeparators(file_name)
    
    if not saved:
        QMessageBox.warning(
            parent,
            msgs.get("warning_title", "Save Error"),
            msgs.get("warning_text", "The image could not be saved.")
        )
        
        return
        
    message_box: QMessageBox = QMessageBox()
    message_box.setIcon(QMessageBox.Icon.Information)
    message_box.setWindowTitle(msgs.get("save_title", "Save Image"))
    message_box.setText(msgs.get("save_text", "The image has been saved."))
    message_box.show()
    button1: QPushButton = message_box.addButton(msgs.get("open_button_text", "Open Image"), QMessageBox.ButtonRole.ActionRole)
    button1.clicked.connect(lambda: QDesktopServices.openUrl(initial_file_name))
    button2: QPushButton = message_box.addButton("Open Explorer", QMessageBox.ButtonRole.ActionRole)
    button2.clicked.connect(lambda: QDesktopServices.openUrl(initial_path))
    message_box.exec_()