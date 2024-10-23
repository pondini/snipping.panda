from .callbacks import no_callback
from .image import save_image
from .generator import QRCodeGenerator

GENERATORS = {generator.__name__.removesuffix('Generator').lower(): generator for generator in QRCodeGenerator.__subclasses__()}