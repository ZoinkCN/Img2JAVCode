import base64
import os
from io import BytesIO

import cv2
from PIL import Image, ImageSequence
from PIL.GifImagePlugin import GifImageFile


def pic2imgs(pic_path):
    pic = Image.open(pic_path)
    if not type(pic) == GifImageFile:
        return [pic.convert('RGB')]
    frames = [f.copy() for f in ImageSequence.Iterator(pic)]
    frames_num = len(frames)
    time_f = 10
    time_f = time_f if frames_num > time_f else frames_num
    step = int(frames_num / time_f)
    imgs = [frames[i].convert('RGB') for i in range(0, frames_num, step)]
    return imgs


def video2imgs(video_path):
    vc = cv2.VideoCapture(video_path)  # 读取视频文件
    frames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
    time_f = 10
    time_f = time_f if frames >= time_f else frames
    step = int(frames / time_f)

    imgs = []
    for _ in range(time_f):  # 循环读取视频帧
        c = vc.get(cv2.CAP_PROP_POS_FRAMES)
        __, frame = vc.read()
        img = Image.fromarray(frame)
        if frame is not None:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            imgs.append(img)
        vc.set(cv2.CAP_PROP_POS_FRAMES, c + step)
    vc.release()
    return imgs


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
