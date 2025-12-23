import sqlite3, os, datetime, cv2

class Database:
    def __init__(self, config):
        # Thông số mặc định
        path = config.get('database_path', 'camera.db')
        self.mask_path_common = config.get('mask_path_common', '')
        self.false_path = config.get('false_path', '')

        is_new_db = not os.path.exists(path)
        # Nếu thư mục path chưa tồn tại → tạo
        folder = os.path.dirname(path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

        # Kết nối SQLite
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

        # Nếu DB mới → tạo bảng
        if is_new_db:
            print("➡️ Tạo database mới, tạo bảng mặc định...")
            self.create_table_default()
            self.conn.commit()
        else:
            print("➡️ Đọc database thành công")

    def create_table_default(self):
        # Tạo bảng lưu mask của cam
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS camera_mask (
                id TEXT PRIMARY KEY,
                mask_path TEXT,
                last_update TEXT,
                updated_by TEXT
            );
            """
        )

        # Chèn dữ liệu mẫu cho camera_mask
        self.cursor.execute("""
            INSERT INTO camera_mask (id, last_update, updated_by)
            VALUES ('cam_2', '', 'AD');
        """)

        # Tạo bảng lưu mask của cam
        self.cursor.execute(
            """
                CREATE TABLE IF NOT EXISTS camera_objs (
                id TEXT PRIMARY KEY,
                objs TEXT,
                last_id INT,
                last_update TEXT
            );
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS camera_objs_false (
                cam_id TEXT,
                char_id TEXT,
                time_detect TEXT,
                PRIMARY KEY (cam_id, char_id)
            );
            """
        )

    #-----------------------------------
    # CÁC HÀM TƯƠNG TÁC
    #-----------------------------------
    def get_cam_mask(self, cam_id):
        self.cursor.execute("SELECT 1 FROM camera_mask WHERE id = ? LIMIT 1;", (cam_id,))
        result = self.cursor.fetchone()
        if result is not None:
            return f"{self.mask_path_common}/{cam_id}.png"
        return ''
    
    def get_cam_objs(self, cam_ids):
        placeholders = ",".join(["?"] * len(cam_ids))
        query = f"SELECT id, objs, last_id FROM camera_objs WHERE id IN ({placeholders});"
        self.cursor.execute(query, cam_ids)
        cam_dict = dict()
        for cam_id, objs, last_id in self.cursor.fetchall():
            if objs:
                cam_dict[cam_id] = {
                    'chars': [list(map(int, char.split(','))) for char in objs.split(' ')],
                    'last_id': last_id
                }
            else:
                cam_dict[cam_id] = {
                    'chars': [],
                    'last_id': 0
                }
            
        return cam_dict
    
    def save_cam_objs(self, cam_id, objs, last_id):
        temp = [','.join(list(map(str,char))) for char in objs]
        temp = ' '.join(temp)
        now = datetime.datetime.now().isoformat()

        self.cursor.execute(
            """
            INSERT INTO camera_objs (id, objs, last_id, last_update)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                objs = excluded.objs,
                last_id = excluded.last_id,
                last_update = excluded.last_update;
            """,
            (cam_id, temp, last_id, now)
        )
        self.conn.commit()

    def save_char_false(self, cam_id, char, img):
        """
        Lưu thông tin char vào DB nếu chưa có.
        """
        time_now = datetime.datetime.now().isoformat()
        char_id = char[0]

        # Kiểm tra xem char_id đã có trong camera_objs_false chưa
        self.cursor.execute(
            "SELECT 1 FROM camera_objs_false WHERE cam_id = ? AND char_id = ?",
            (cam_id, char_id)
        )
        exists = self.cursor.fetchone()

        if not exists:
            # Lưu vào DB nếu chưa có
            self.cursor.execute(
                """
                INSERT INTO camera_objs_false (cam_id, char_id, time_detect)
                VALUES (?, ?, ?)
                """,
                (cam_id, char_id, time_now)
            )
            self.conn.commit()

            # Lưu ảnh ra file, ví dụ theo char_id và timestamp
            filename = f"{self.false_path}/{cam_id}_{char_id}_{int(datetime.datetime.now().timestamp())}.jpg"
            cv2.imwrite(filename, img)

def draw(char, img):
    char_id = char[0]
    box = char[1:5]  # [x, y, w/h, h]
    
    x, y, wh_ratio, h = box
    w = wh_ratio * h  # tính lại width từ w/h

    # Chuyển sang integer để vẽ
    x1, y1, x2, y2 = int(x), int(y), int(x + w), int(y + h)
    
    # Vẽ rectangle và text
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, f"ID:{char_id}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    return img