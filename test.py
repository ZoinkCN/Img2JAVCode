import cv2
import os


# 使用opencv对视频均匀截取图片
def Video2Img(videoPath, imgPath, /, *, rename=''):
    vc = cv2.VideoCapture(videoPath)  # 读取视频文件
    imgPath = imgPath.rstrip('/')
    if rename == '':
        video_name = os.path.basename(videoPath)
        video_name = os.path.splitext(video_name)[0]
    else:
        video_name = rename
    frames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
    time_f = 10
    time_f = time_f if frames > time_f else frames   # 视频帧计数间隔频率
    step = int(frames / time_f)

    for i in range(time_f):  # 循环读取视频帧
        c = vc.get(cv2.CAP_PROP_POS_FRAMES)
        rval, frame = vc.read()
        cv2.imwrite(f'{imgPath}/{video_name}.jpg', frame)  # 存储为图像
        vc.set(cv2.CAP_PROP_POS_FRAMES, c + step)
    vc.release()
