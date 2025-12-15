import numpy as np
from ultralytics import YOLO
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

class Segmentater:
    def __init__(self, config):
        try:
            self.model = YOLO(config.get('model_path', ''))
            print('[INFO] 🟢 Model segmentation initialized successfully')
        except:
            print('[WARNING] ❗ Cannot initialize YOLO-SEGMENT model')

    def transform(self, results):
        merged_masks = []

        for res in results:
            if res.masks is None:
                merged_masks.append(None)
                continue
            # Gộp mask lại
            masks = res.masks.data.cpu().numpy()
            merged = np.max(masks, axis=0).astype(np.uint8)
            merged_masks.append(merged)

        return merged_masks

    def get_mask(self, imgs):
        results = self.model.predict(imgs, verbose=False, device = device)
        return self.transform(results)
