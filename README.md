# Python version

## Yều cầu <= 3.12 (*Khuyến nghị 3.10*)

```bash
py -3.12 -m venv <tên môi trường>
cd <current folder>
venv\Scripts\activate
```
## Needed package torch to using CUDA

```bash
pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```
## Needed others
```bash
pip install -r requirements.txt
```

# Workflow - Terminal command
**Needed**: Activate the virtual enviromant first

## Kafka (Docker)
### 1. Run docker-compose.yml
```bash
docker compose up -d
docker ps (-> check container)
```

### 2. Create topic
```bash
# docker exec -it kafka bash -lc "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic <Topic-Name> --partitions 3 --replication-factor 1"
docker exec -it kafka bash -lc "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic cams.frames --partitions 3 --replication-factor 1"
docker exec -it kafka bash -lc "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic cams.result --partitions 3 --replication-factor 1"
```

### 3. Check topic created
```bash
docker exec -it kafka bash -lc "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list"
```

## Run workflow
```Python```
consumer.py (**Receive**) → events.py (**Events catching**) → sender.py (**Send**)