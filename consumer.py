### CONSUMER - STEP 2 (gpu-inference consumer)

import json, base64, cv2, time
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
import logging
from logging.handlers import RotatingFileHandler

from main import auto_handle
from config import SENDER_TOPIC, RECEIVER_TOPIC, BOOTSTRAP

#---------------------------------------------- Setup log -------------------------------------------------
logger = logging.getLogger("Consumer")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "logs/consumer.log",
    maxBytes = 10 * 1024 * 1024,
    backupCount = 5
)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# init
consumer = KafkaConsumer(
    SENDER_TOPIC,
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

def to_py(v):
    if hasattr(v, "item"):
        return v.item()
    return v
#-------------------------------------------------- run -------------------------------------------------

for msg in consumer:
    payload = msg.value
    ts = payload.get("ts", int(time.time() * 1000))
    frame_idx = payload.get("frame_idx", -1)
    
    cam_ids = payload.get("cam_ids")
    imgs = [decode_img_b64(img) for img in payload["imgs"] if img is not None]
    
    #log-receive
    logger.info(f"Receive batch: {len(cam_ids)} cams")
    
    start = time.time()
    try:
        events = auto_handle(cam_ids, imgs) or []
    except Exception as e:
        events = []
        logger.exception("Inference failed")    # log-inference
        continue
    elapsed = time.time() - start
    
    logger.info(
        f"cams={cam_ids} "
        f"| events_len={len(events)} | time={elapsed:.3f}s"
    )
    
    for event in events:
        #log-event
        event = {k: to_py(v) for k, v in event.items()}
        logger.info(f"Event| {event}")
        
        event["ts"] = ts
        event["frame_idx"] = frame_idx
        cam_id = event.get("cam_id", "unknown")
        
        producer.send(RECEIVER_TOPIC, key=cam_id, value = event)
        
    producer.flush()

