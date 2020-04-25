import json
import os
import re
import socket
import sys
from xmlrpc import server

import cv2
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES

from ImgEngine_pub import *


def video2img(video_path, img_dir, rename=''):
    vc = cv2.VideoCapture(video_path)  # 读取视频文件
    img_dir = img_dir.rstrip('/')
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)
    if rename == '':
        video_name = os.path.basename(video_path)
        video_name = os.path.splitext(video_name)[0]
    else:
        video_name = rename
    frames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
    time_f = 10
    time_f = time_f if frames > time_f else frames
    step = int(frames / time_f)

    img_paths = []
    for i in range(time_f):  # 循环读取视频帧
        c = vc.get(cv2.CAP_PROP_POS_FRAMES)
        _, frame = vc.read()
        img_path = f'{img_dir}/{video_name}_{int(c)}.jpg'
        cv2.imwrite(img_path, frame)  # 存储为图像
        img_paths.append(img_path)
        vc.set(cv2.CAP_PROP_POS_FRAMES, c + step)
    vc.release()
    return img_paths


class ImageEngine:
    imgs_root = '../Resources/imgs'

    @staticmethod
    def read_data(html_path):
        html_path = html_path.data
        html = open(html_path, 'r', encoding='utf-8')
        html = html.read()
        html = html.replace('<br>', '\n')
        html = BeautifulSoup(html, 'lxml')
        # html = bs(html)
        path_root = '../telegramData/'
        messages = html.find_all(id=re.compile('message'))
        title = ''
        for message in messages:
            text_ele = message.find(name='div', attrs={'class': 'text'})
            if text_ele:
                title = text_ele.get_text().strip()
            video_ele = message.find(name='a', attrs={'class': re.compile('animated_wrap')})
            if video_ele:
                video_path = path_root + video_ele['href'].strip()
                es = Elasticsearch()
                ses = SignatureES(es)
                print(video_path)
                # print(title)
                for img in video2img(video_path, ImageEngine.imgs_root):
                    ses.add_image(img, metadata={'message': title})

    @staticmethod
    def search_img(data):
        data = data.data
        data = base64.b64decode(data)
        es = Elasticsearch()
        ses = SignatureES(es)
        results = ses.search_image(
            data,
            bytestream=True
        )
        for result in results:
            result['img'] = bytes.decode(img2data(Image.open(result['path'])))
            del result['path']
        results = json.dumps(results)
        return results

    @staticmethod
    def add_data(data, metadata=None):
        data = data.data
        data = base64.b64decode(data)
        if metadata:
            metadata = metadata.data
        es = Elasticsearch()
        ses = SignatureES(es)
        img = data2img(data)
        path = f'{ImageEngine.imgs_root}/{abs(hash(data))}.jpg'
        img.save(path)
        ses.add_image(path, metadata=metadata)
        return ''


if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    with server.SimpleXMLRPCServer((local_ip, 9088)) as rpc_server:
        rpc_server.register_instance(ImageEngine())
        print('server start at 9088')
        try:
            rpc_server.serve_forever()
        except KeyboardInterrupt:  # ctrl + C to exit
            print('\nKeyboard interrupt received, exiting.')
            sys.exit(0)
