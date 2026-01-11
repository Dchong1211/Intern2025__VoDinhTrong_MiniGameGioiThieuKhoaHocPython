import random

class LevelObjective:
    def __init__(self):
        # Cấu trúc: {"Apple": {"required": 5, "collected": 0, "max_in_map": 10}, ...}
        self.objectives = {}

    # ================= GENERATE =================
    def generate(self, fruit_counts_in_map):
        self.objectives = {}
        for name, total_available in fruit_counts_in_map.items():
            if total_available > 0:
                # Random yêu cầu từ 1 đến tổng số có trong map
                req = random.randint(1, total_available)
                self.objectives[name] = {
                    "required": req,
                    "collected": 0,
                    "max_in_map": total_available
                }

    # ================= ADD (QUAN TRỌNG: SỬA TÊN HÀM) =================
    def add(self, name, amount=1): 
        """
        Hàm này được ItemManager gọi khi người chơi ăn trái cây.
        Tên hàm bắt buộc phải là 'add' để khớp với code cũ.
        """
        if name not in self.objectives:
            return

        data = self.objectives[name]
        
        # Tăng số lượng collected, không vượt quá required
        if data["collected"] < data["required"]:
            data["collected"] = min(data["collected"] + amount, data["required"])

    # ================= CHECK =================
    def is_completed(self):
        """Kiểm tra xem đã thu thập đủ hết chưa"""
        if not self.objectives:
            return True # Không có nhiệm vụ -> Coi như xong
            
        for data in self.objectives.values():
            if data["collected"] < data["required"]:
                return False
        return True

    # ================= HELPERS =================
    def get_data(self):
        return self.objectives

    def reset(self):
        for data in self.objectives.values():
            data["collected"] = 0