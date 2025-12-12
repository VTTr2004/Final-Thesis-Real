import torch, cv2
import numpy as np

class Visualer:
    def __init__(self, config):
        self.size = config.get('size', 64)
        self.channel = config.get('channel', 1)
        self.max_step = config.get('max_step', 2)

    def transform_mask(self, path):
        mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if mask.ndim == 3:
            mask = mask[:, :, 0]

        mask = torch.from_numpy(mask).float()
        mask = mask.unsqueeze(0)
        return mask
    
    def draw_obj(self, img, img_shape, char, new_img=False, char_predict=False):
        if new_img:
            img_temp = img
        else:
            img_temp = img.clone()

        val = 100
        if char_predict:
            val = 200

        x, y = char[1:3]
        x = int(x/img_shape[0])*self.size
        y = int((y+char[5]/2)/img_shape[1])*self.size
        dx, dy = char[5:7]
        x2 = x + int(np.clip(dx, -self.max_step, self.max_step))
        y2 = y + int(np.clip(dy, -self.max_step, self.max_step))

        img_temp[0, y:y+2, x:x+2] = val
        img_temp[0, y2:y2+2, x2:x2+2] = val + 50

        return img_temp
    
    @staticmethod
    def check_obj(char):
        if char[5] == 0 and char[6] == 0 and char[7] == 0 and char[8] == 0:
            return False
        return True

    def get_visual(self, value):
        mask_pro = self.transform_mask(value['mask_path'])
        # Vẽ tất cả vật thể
        chars = []
        for char in value['data']:
            if Visualer.check_obj(char):
                mask_pro = self.draw_obj(mask_pro, value['image_shape'], char)
                chars.append(char)
        # Vẽ tưng obj
        result = []
        for char in chars:
            img = self.draw_obj(mask_pro, value['image_shape'], char, new_img=True, char_predict=True)
            result.append((char[0], img))

        return result