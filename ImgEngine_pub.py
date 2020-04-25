import base64
from io import BytesIO

from PIL import Image


def img2data(img):
    output_buffer = BytesIO()
    img.save(output_buffer, format='JPEG')
    data = output_buffer.getvalue()
    data = base64.b64encode(data)
    return data


def data2img(data):
    if type(data) != str:
        data = data.data
    data = base64.b64decode(data)
    image_data = BytesIO(data)
    img = Image.open(image_data)
    return img
