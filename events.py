import json
from kafka import KafkaConsumer

from config import RECEIVER_TOPIC, BOOTSTRAP

consumer = KafkaConsumer(
    RECEIVER_TOPIC,
    bootstrap_servers = BOOTSTRAP,
    value_deserializer = lambda v : json.loads(v.decode("utf-8")),
    auto_offset_reset = "latest",
    enable_auto_commit = True,
    group_id = "gpu-inference-consumer",
)

for msg in consumer:
    print(msg.value)