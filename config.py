import os

# Các thông số chung mặc định
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))

IMG_TEST = f"{CURRENT_FOLDER}/storage/image/img_test.jpg"
CAMS_TEST = {
    'camera':[
        {'cam_id':'cam_1',
        'video_path':f"{CURRENT_FOLDER}/storage/video/cam_1.mp4"},
        {'cam_id':'cam_2',
        'video_path':f"{CURRENT_FOLDER}/storage/video/cam_2.mp4"}
        ],
    'amount_frame': 30
    }

# Các thông số liên quan đến mô hình
TEST_DETECT = False

CONFIG_DETECTION = {
    'model_path': f"{CURRENT_FOLDER}/resource/model/detect.pt"
}

CONFIG_VISUAL = {
    'size' : 64,
    'channel' : 1,
    'step_max': 2,
}

CONFIG_SEGMENTATION = {
    'model_path': f"{CURRENT_FOLDER}/resource/model/segment.pt"
}

# # Khởi tạo mô hình phân đoạn đường đi
# from handlers.segmentater import Segmentater
# segmentater = Segmentater(config.CONFIG_SEGMENTATION)

CONFIG_CLASSIFICATION = {
    'back_bone': 'vgg16',
    'input_shape': (1, 64, 64),
    'pretrained': True,
    'model_path': f"{CURRENT_FOLDER}/resource/model/classi_vgg16.pth"
}

# Các thông số liên quan đến lưu trữ
CONFIG_STORE = {
    'database_path': f"{CURRENT_FOLDER}/storage/databse.db",
    'mask_path_common': f"{CURRENT_FOLDER}/storage/mask",
    'false_path': f"{CURRENT_FOLDER}/storage/img_false"
}

BOOTSTRAP = "localhost:9092"
SENDER_TOPIC = "cams.frames"
RECEIVER_TOPIC = "cams.results"