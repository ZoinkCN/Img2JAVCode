import json
import re
import socket
import sys
import time
from xmlrpc.server import SimpleXMLRPCRequestHandler, SimpleXMLRPCServer

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES

from ImgEngine_pub import *


class XMLRPCTracebackHandler(SimpleXMLRPCRequestHandler):
    def _dispatch(self, method, params):
        try:
            return self.server.funcs[method](*params)
        except:
            import traceback
            traceback.print_exc()
            raise


imgs_root = '../Resources/imgs'


def add_to_lib(media_path, message):
    es = Elasticsearch()
    ses = SignatureES(es)
    if not os.path.isdir(imgs_root):
        os.mkdir(imgs_root)
    if not os.path.exists(media_path):
        print(f'"{media_path}" Not exists')
        return
    media_fullname = os.path.basename(media_path)
    media_name, _ = os.path.splitext(media_fullname)
    imgs = media2imgs(media_path)
    title_print = message.replace('\n', ' ')
    info = f'{media_fullname} ---- {title_print}'
    print(info)
    i = 1
    for img in imgs:
        results = ses.search_image(base64.b64decode(img2data(img)), bytestream=True)
        if results and results[0]['dist'] < 0.1:
            continue
        img_name = f'\t{abs(hash(message))}_{i}.jpg'
        print(img_name)
        path = f'{imgs_root}/{img_name}'
        i += 1
        img.save(path)
        ses.add_image(path, metadata={'message': message})
    print('')
    try:
        os.remove(media_path)
    except:
        pass
    return info


def read_data(html_path, tags: list = None):
    try:
        file = open('test.txt', 'w', encoding='utf-8')
        file.close()
        html = open(html_path, 'r', encoding='utf-8')
        html = html.read()
        html = html.replace('<br>', '\n')
        html = BeautifulSoup(html, 'lxml')
        # html = bs(html)
        path_root = '../telegramData/'
        messages = html.find_all(id=re.compile('message'))
        title = ''
        msg_time = time.strptime('01.01.1970 00:00', '%d.%m.%Y %H:%M')
        medias = []
        with open('filter.json', 'r') as file:
            title_filter = file.read()
        title_filter = json.loads(title_filter)
        for message in messages:
            print(f'[{messages.index(message) + 1}/{len(messages)}]')
            time_ele = message.find('div', attrs={'class': 'pull_right'})
            if time_ele:
                time_str = time_ele['title']
                temp = time.strptime(time_str[:-3], '%d.%m.%Y %H:%M')
                if msg_time != temp:
                    msg_time = temp
                    title = ''
                    medias.clear()
            text_ele = message.find('div', attrs={'class': 'text'})
            if text_ele:
                title = text_ele.get_text().strip()
            if not re.search(f'({str.join("|", title_filter["whitelist"])})', title) \
                    and re.search(f'({str.join("|", title_filter["blacklist"])})', title):
                skip = True
            elif tags and not re.search(f'({str.join("|", tags)})', title):
                skip = True
                print('no tag,skip')
            else:
                skip = False
            if title != '':
                for media in medias:
                    add_to_lib(media, title)
                medias.clear()
            media_ele = message.find('a')
            if media_ele:
                media_path = path_root + media_ele['href'].strip()
                if title == '':
                    medias.append(media_path)
                    continue
                if not skip:
                    add_to_lib(media_path, title)
    except KeyboardInterrupt:
        print('\nReading stoped!')
        return


def search_img(file_data, file_format):
    if file_format == '.jpg':
        data = base64.b64decode(file_data.data)
    else:
        return 'Invalid data format'
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


def add_data(file, file_format, message):
    if file_format == '.jpg':
        temp = data2img(file)
        file_name = f'{abs(hash(file.data))}{file_format}'
        file_path = f'temp/{file_name}'
        temp.save(file_path)
    elif file_format in ['.gif', '.mp4']:
        file_path = file
    else:
        return 'Invalid data format'
    return add_to_lib(file_path, message)


if __name__ == '__main__':
    port = int(sys.argv[1])
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    with SimpleXMLRPCServer((local_ip, port), requestHandler=XMLRPCTracebackHandler, allow_none=True) as rpc_server:
        rpc_server.register_function(read_data)
        rpc_server.register_function(add_data)
        rpc_server.register_function(search_img)
        print(f'server start at {port}')
        try:
            rpc_server.serve_forever()
        except KeyboardInterrupt:  # ctrl + C to exit
            print('\nKeyboard interrupt received, exiting.')
            sys.exit(0)
