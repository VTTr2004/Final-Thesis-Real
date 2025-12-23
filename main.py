import os, cv2
os.system('cls')

import config

# Khởi tạo database
from database import Database
database = Database(config.CONFIG_STORE)

# Khởi tạo mô hình trích xuất và theo dõi vật thể
from handlers.detecter import Detecter
from handlers.tracker import Tracker
detecter = Detecter(config.CONFIG_DETECTION)
tracker = Tracker()
# Kiểm tra thử model
if config.TEST_DETECT:
    img = cv2.imread(config.IMG_TEST, cv2.IMREAD_COLOR_RGB)
    print(detecter.predict([img])[0])
else:
    pass

# Khởi tạo công cự trực quan
from handlers.visualler import Visualer
visualer = Visualer(config.CONFIG_VISUAL)

# Khởi tạo mô hình phân loại lỗi
from handlers.classifier import Classifier
classifier = Classifier(config.CONFIG_CLASSIFICATION)

#-----------------------------
# HÀM CHÍNH
#-----------------------------

def auto_handle(cam_ids, imgs):
    target = []
    data = dict()
    cam_img = dict()
    # Lọc những cam-id được phép tiếp tục
    for cam_id, img in zip(cam_ids, imgs):
        path = database.get_cam_mask(cam_id)
        cam_img[cam_id] = img
        if path != '':
            data[cam_id] = {
                'mask_path': path,
                'data': img,
                'image_shape': img.shape
            }

    # 📷 Log số camera nhận được
    print(f"📷 Nhận được {len(cam_ids)} camera, lọc còn {len(data)} camera có mask hợp lệ.")
            
    # Trích xuất vật thể
    img_predict = [val['data'] for val in data.values()]
    objs_new_list = detecter.predict(img_predict)
    for idx, k in enumerate(data.keys()):
        data[k]['data'] = objs_new_list[idx]
    
    # Lấy dữ liệu vật thể cũ
    cams = list(data.keys())
    cam_data_old = database.get_cam_objs(cams)
    # Theo dõi và lưu lại vật thể
    for cam_id in data.keys():
        char_new = data[cam_id]['data']
        char_old = []
        last_id = 0
        if cam_id in cam_data_old.keys():
            char_old = cam_data_old[cam_id].get('chars', [])
            last_id = cam_data_old[cam_id].get('last_id', 0)
        chars, last_id = tracker.tracking(char_old, char_new, last_id)
        database.save_cam_objs(cam_id, chars, last_id)
        data[cam_id]['data'] = chars

    # Chuyển đổi thành ảnh trực quan
    infor_img = []
    input_img = []
    for cam_id in data.keys():
        temp = visualer.get_visual(data[cam_id])
        for infor in temp:
            infor_img.append((cam_id, infor))
            input_img.append(infor[1])
    
    # 🖼️ Log số ảnh được classify
    print(f"🖼️ Có {len(input_img)} ảnh được dùng để classify.")

    # Phân loại lỗi và lưu trữ
    # result_classi = classifier.classify(input_img)
    # for infor, result in zip(infor_img, result_classi):
    #     if result == 1:
    #         target.append[(*infor, result)]
    #         database.save_char_false(*infor)
    
    result_classi = classifier.classify(input_img)
    pred_count = 0
    for (cam_id, char), (pred, prob) in zip(infor_img, result_classi):
        
        if pred == 1:
            pred_count += 1
            target.append({
                "cam_id": cam_id,
                "char_id": char[0],
                "pred": int(pred),
                "prob": int(prob)
            })
            database.save_char_false(cam_id, char, cam_img[cam_id])

    # ✅ Log số lượng pred == 1
    print(f"✅ Có {pred_count} vật thể được phân loại là lỗi.")
            
    return target