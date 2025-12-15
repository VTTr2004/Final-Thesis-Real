import json
from kafka import KafkaConsumer

BOOTSTRAP = "localhost:9092"
TOPIC = "cams.result"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers = BOOTSTRAP,
    value_deserializer = lambda v : json.loads(v.decode("utf-8")),
    auto_offset_reset = "earliest",
    enable_auto_commit = True,
    group_id = "gpu-inference-consumer",
)

for msg in consumer:
    print(msg.value)