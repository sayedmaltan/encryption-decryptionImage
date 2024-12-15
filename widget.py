from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QGroupBox,
    QFileDialog,
    QMessageBox,
    QComboBox,
)
from PySide6.QtGui import QPixmap
import os
import cv2

from aes import encrypt_image, decrypt_image


class Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AES Image Encryption/Decryption")

        # Variables
        self.imageEncrypted = None
        self.decryptedImage = None
        self.imagefile = None
        self.encrypted_image_file = None  # Store encrypted image path

        ##* KEY
        key_label = QLabel("Key")
        self.key_line = QLineEdit()
        self.key_line.setPlaceholderText("Enter your key here")

        key_layout = QHBoxLayout()
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_line)

        ## * Choose File
        self.file_dialog = QFileDialog(self)
        self.file_dialog.setFileMode(QFileDialog.AnyFile)

        upload_button = QPushButton("Choose Image")
        upload_button.clicked.connect(self.choose_image)

        # Image display
        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 300)  # Fixed size for the image display
        self.image_label.setStyleSheet("border: 1px solid black;")

        ## * Method
        mode = QGroupBox("Choose Method")

        encrypt = QPushButton("Encrypt")
        decrypt = QPushButton("Decrypt")

        encrypt.clicked.connect(self.enc_image)
        decrypt.clicked.connect(self.dec_image)

        self.mode_list = QComboBox()
        self.mode_list.addItems(["ECB", "CTR", "CFB", "CBC"])

        method_layout = QHBoxLayout()
        method_layout.addWidget(encrypt)
        method_layout.addWidget(decrypt)

        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.mode_list)
        mode_layout.addLayout(method_layout)
        mode.setLayout(mode_layout)

        clear = QPushButton("Clear")
        clear.clicked.connect(self.cls)

        ## * Layout
        layout = QVBoxLayout()
        layout.addLayout(key_layout)
        layout.addWidget(self.image_label)
        layout.addWidget(upload_button)
        layout.addWidget(mode)
        layout.addWidget(clear)
        self.setLayout(layout)

    ## * Choose Image
    def choose_image(self):
        self.image_label.clear()
        self.imagefile = self.file_dialog.getOpenFileName(
            parent=self, caption="Select Image", dir=os.getcwd()
        )
        if self.imagefile[0]:  # If a file was selected
            pixmap = QPixmap(self.imagefile[0])
            scaled_pixmap = pixmap.scaled(300, 300)
            self.image_label.setPixmap(scaled_pixmap)

    ## * Encrypt Image
    def enc_image(self):
        if not self.key_line.text():
            QMessageBox.critical(self, "No Key", "Please Enter a key", QMessageBox.Ok)
        else:
            if self.imagefile:
                image = cv2.imread(self.imagefile[0])
                try:
                    # Encrypt the image
                    self.imageEncrypted = encrypt_image(
                        image, self.key_line.text(), self.mode_list.currentText()
                    )
                    self.encrypted_image_file = "ImageEncrypted.png"
                    pixmap = QPixmap(self.encrypted_image_file).scaled(300, 300)
                    self.image_label.setPixmap(pixmap)
                    self.imagefile = None  # Clear original image file
                except:
                    QMessageBox.critical(
                        self,
                        "Invalid Data",
                        "The key is wrong or the cipher mode is different",
                        QMessageBox.Ok,
                    )
            else:
                QMessageBox.critical(
                    self, "No Image", "Please choose an image", QMessageBox.Ok
                )

    ## * Decrypt Image
    def dec_image(self):
        if not self.key_line.text():
            QMessageBox.critical(self, "No Key", "Please Enter a key", QMessageBox.Ok)
        else:
            if self.encrypted_image_file:  # Check for encrypted image
                self.imageEncrypted = cv2.imread(self.encrypted_image_file)
                try:
                    # Decrypt the image
                    self.decryptedImage = decrypt_image(
                        self.imageEncrypted,
                        self.key_line.text(),
                        self.mode_list.currentText(),
                    )
                    decrypted_image_path = "decryptedImage.png"
                    pixmap = QPixmap(decrypted_image_path).scaled(300, 300)
                    self.image_label.setPixmap(pixmap)
                except:
                    QMessageBox.critical(
                        self,
                        "Invalid Data",
                        "The key is wrong or the cipher mode is different",
                        QMessageBox.Ok,
                    )
            else:
                QMessageBox.critical(
                    self, "No Image", "Please encrypt an image first", QMessageBox.Ok
                )

    ## * Clear
    def cls(self):
        self.image_label.clear()
        self.key_line.clear()
        self.imageEncrypted = None
        self.decryptedImage = None
        self.imagefile = None
        self.encrypted_image_file = None


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    window = Widget()
    window.show()
    app.exec()
