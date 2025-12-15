### Producer - Sender

import cv2, json, base64, time
from kafka import KafkaProducer
import config

BOOTSTRAP = "localhost:9092"
TOPIC = "cams.frames"

# init producer
producer = KafkaProducer(
    bootstrap_servers = BOOTSTRAP,
    value_serializer = lambda v: json.dumps(v).encode('utf-8')
)

#---------------------------------------------- handling function --------------------------------------
def get_amount_frames(video_path : str, amount : int = 100) -> list:
    """  
    Get frames-data from video with fix/flexible amount
    """
    
    cap = cv2.VideoCapture(video_path)
    frames = []
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[INFO]: total frames: {total_frames}")
    
    if amount > total_frames:
        amount = total_frames
        
    for _ in range(amount):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        
    cap.release()
    return frames

def get_data(config) -> dict:
    """  
    Get formated-data 
    """
    result = {}
    for val in config.get("camera"):
        imgs = get_amount_frames(val.get("video_path"), config.get("amount_frame"))
        result[val["cam_id"]] = imgs
        
    return result

def encode_img_b64(img, quality = 80):
    """  
    Encode image into base64 for send to kafka-topic
    """
    
    ok, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return None
    
    return base64.b64encode(buf.tobytes()).decode('utf-8')

#----------------------------------------------- run --------------------------------------------------
data = get_data(config.CAMS_TEST)

# deploy to kafka-producer (SENDER)
num_frames = min(len(v) for v in data.values())
print(f"[SEND-INFO]: number of frames to send: {num_frames}")

for idx in range(num_frames):
    cam_ids = list(data.keys())
    imgs = [val[idx] for val in data.values()]
    
    payload = {
        "ts": int(time.time() * 1000),
        "cam_ids": cam_ids,
        "imgs": [encode_img_b64(img) for img in imgs]
    }
    
    producer.send(TOPIC, payload)
    producer.flush()
    
    time.sleep(0.03)
    
print("[SEND-INFO]: sending data done !")