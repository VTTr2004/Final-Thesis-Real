from ultralytics import YOLO
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

class Detecter:
    def __init__(self, config):
        try:
            self.model = YOLO(config.get('model_path', ''))
            print('[INFO] 🟢 Model detection initialized successfully')
        except:
            print('[WARNING] ❗ Cant initalized model YOLO-DETECT')

    def transform(self, results):
        result_final = []
        for result in results:
            temp = []
            for xywh in result.boxes.xywh.cpu().numpy():
                x, y, w, h = xywh
                temp.append(list(map(float, [x, y, w/h, h])))
            result_final.append(temp)
        return result_final

    def predict(self, imgs):
        results = self.model.predict(imgs, verbose=False, device = device)
        return self.transform(results)