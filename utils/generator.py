from abc import ABC

from PIL.ImageQt import ImageQt
from PIL import Image
import segno

class QRCodeGenerator(ABC):
    def generate_qr_code(self):
        pass
    
class SegnoGenerator(QRCodeGenerator):
    def __init__(self, input, input_image, input_image_text):
        self.input = input
        self.input_image = input_image
        self.input_image_text = input_image_text
    
    def generate_qr_code(self) -> ImageQt:
        qrcode = segno.make_qr(self.input.toPlainText())
        if self.input_image:
            import io
            out = io.BytesIO()
            text = self.input_image_text.text()

            kind = text.split('.')[-1]
            if kind == 'jpg':
                kind = 'png'
            
            qrcode.to_artistic(background=text, target=out, kind=kind)
            pil_image = Image.open(out)
        
        else:
            pil_image = qrcode.to_pil()
        
        pil_image = pil_image.resize((800, 800))
        pil_image = pil_image.convert('RGB')
        
        image = ImageQt(pil_image)
        
        return image