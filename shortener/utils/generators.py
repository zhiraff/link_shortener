from secrets import choice
import string
import qrcode
from io import BytesIO

def generate_short_link(use_numeric: bool=True, length: int=6) -> str:

    if use_numeric:
        ALPHABET: str = string.ascii_letters + string.digits
    else:
        ALPHABET: str = string.ascii_letters
    
    if length < 6:
        raise ValueError()
    res = ''
    for _ in range(length):
        res += choice(ALPHABET)
    
    return res


def generate_qr_svg(data: str="https://ya.ru") -> bytes:
    # data = request.GET.get('data', 'Hello, World!')
    
    # Создаем фабрику для SVG
    # factory = qrcode.image.svg.SvgImage
    
    # Генерируем QR-код как SVG
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        # image_factory=factory,
        box_size=20,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохраняем SVG в строку
    stream = BytesIO()
    img.save(stream, format='PNG')
    # svg_string = stream.getvalue().decode()
    
    return stream