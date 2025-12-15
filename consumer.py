### CONSUMER - STEP 2 (gpu-inference consumer)

import json, base64, cv2, time
import numpy as np
from kafka import KafkaConsumer, KafkaProducer

from main import auto_handle

BOOTSTRAP = "localhost:9092"
IN_TOPIC = "cams.frames"
OUT_TOPIC = "cams.results"

# init
consumer = KafkaConsumer(
    IN_TOPIC,
    bootstrap_servers = BOOTSTRAP,
    value_deserializer = lambda v : json.loads(v.decode("utf-8")),
    auto_offset_reset = "latest",
    enable_auto_commit = True,
    group_id = "gpu-inference-consumer",
)

producer = KafkaProducer(
    bootstrap_servers = BOOTSTRAP,
    key_serializer = lambda k : k.encode('utf-8'),
    value_serializer = lambda v: json.dumps(v).encode('utf-8'),
)

#--------------------------------------------- handling function ----------------------------------------

def decode_img_b64(b64 : str):
    raw = base64.b64decode(b64)
    arr = np.frombuffer(raw, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

#-------------------------------------------------- run -------------------------------------------------

for msg in consumer:
    payload = msg.value
    ts = payload.get("ts", int(time.time() * 1000))
    frame_idx = payload.get("frame_idx", -1)
    
    cam_ids = payload.get("cam_ids")
    imgs = [decode_img_b64(img) for img in payload["imgs"] if img is not None]
    
    events = auto_handle(cam_ids, imgs) or []
    
    for event in events:
        event["ts"] = ts
        event["frame_idx"] = frame_idx
        cam_id = event.get("cam_id", "unknown")
        
        producer.send(OUT_TOPIC, key=cam_id, value = event)
        
    producer.flush()

