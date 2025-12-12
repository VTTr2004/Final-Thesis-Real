import numpy as np
from scipy.optimize import linear_sum_assignment

class Tracker:
    ATTRIBUTE = {
        'id': [0],
        'x, y, a, h': [0, 0, 0, 0],
        "x', y', a', h'": [0, 0, 0, 0],
        'last': [0],
        'label': [0]
    }
    NEW_CHAR = []
    for val in ATTRIBUTE.values():
        NEW_CHAR += val
    NEW_CHAR = np.array(NEW_CHAR)

    @staticmethod
    def new_char(box, last_id):
        temp = np.copy(Tracker.NEW_CHAR)
        temp[0] = last_id + 1
        temp[1:5] = box
        return temp, last_id + 1

    def get_value_future(self, box):
        return box[1:5] + box[5:9]
    
    def get_min_couple(self, char_old, char_new):
        size_old = len(char_old)
        size_new = len(char_new)
        size_max = max(size_old, size_new)
        matrix_distance = np.linalg.norm(np.array(char_old)[:, None, :] -\
                                          np.array(char_new)[None, :, :],\
                                          axis=2)
        matrix_padded = np.full((size_max, size_max), fill_value = 1e9)
        matrix_padded[:size_old, :size_new] = matrix_distance
        old_ind, new_ind = linear_sum_assignment(matrix_padded)
        xs = []
        ys = []
        for i, j in zip(old_ind, new_ind):
            if i < size_old and j < size_new:
                threshold = 0.3 * char_old[i][3]
                if matrix_distance[i, j] < threshold:
                    xs.append(i)
                    ys.append(j)
        return xs, ys
    
    def tracking(self, chars, char_new, last_id):
        if len(chars) != 0:
            if len(char_new) == 0:
                # Nếu không có vật thể mới
                chars[:, -2] += 1
            else:
                # Ghép cặp 2 vật thể
                chars = np.array(chars)
                char_old = np.array([self.get_value_future(char) for char in chars])
                char_new = np.array(char_new)
                old_id, new_id = self.get_min_couple(char_old, char_new)
                print('============================')
                print(old_id, new_id)
                # Cập nhật dữ liệu mới
                print(chars[old_id])
                chars[old_id, 5:9] = char_new[new_id] - chars[old_id, 1:5]
                chars[old_id, 1:5] = char_new[new_id]
                print(chars[old_id])
                print('============================')
                # Xử lý vật thể tracking 
                chars[[i for i in range(len(chars)) if i not in old_id], -2] += 1
                chars[old_id, -2] = 0
                # Xử lý vật thể mới
                char_new = char_new[[i for i in range(len(char_new)) if i not in new_id]]
                if len(char_new) != 0:
                    temp_list = []
                    for char in char_new:
                        char, last_id = self.new_char(np.array(char), last_id)
                        temp_list.append(char)
                    chars = np.vstack((chars, np.array(temp_list)))
        else:
            chars = []
            for char in char_new:
                c, last_id = self.new_char(np.array(char), last_id)
                chars.append(c)
            chars = np.array(chars)
        
        # Loại bỏ vật thể quá thời gian quan sát
        chars = chars[chars[:, -2] < 15]
        return chars, last_id
