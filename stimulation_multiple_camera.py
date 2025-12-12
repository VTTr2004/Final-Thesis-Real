import config
import cv2

def get_amount_frame(video_path, amount=100):
    cap = cv2.VideoCapture(video_path)
    frames = []

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(total_frames)
    if amount > total_frames:
        amount = total_frames

    for i in range(amount):
        ret, frame = cap.read()  # đọc frame liên tiếp
        if not ret:
            break
        frames.append(frame)
    
    cap.release()
    return frames

def get_data(config):
    result = dict()
    for val in config['camera']:
        imgs = get_amount_frame(val['video_path'], config['amount_frame'])
        result[val['cam_id']] = imgs

    return result

from main import auto_handle

data = get_data(config.CAMS_TEST)

for idx in range(config.CAMS_TEST['amount_frame']):
    cam_ids = list(data.keys())
    imgs = [val[idx] for val in data.values()]

    auto_handle(cam_ids, imgs)