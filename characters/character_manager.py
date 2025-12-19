from characters.character_data import CHARACTERS


class CharacterManager:
    def __init__(self, save, item_manager):
        self.save = save
        self.item_manager = item_manager

        self.owned = save.get_owned_characters()
        self.selected = save.get_selected_character()

        # đảm bảo nhân vật mặc định luôn tồn tại
        if "Virtual Guy" not in self.owned:
            self.owned.append("Virtual Guy")

        if self.selected not in self.owned:
            self.selected = "Virtual Guy"

        self.save.save_characters(self.owned, self.selected)

    # ================= QUERY =================
    def is_owned(self, name):
        return name in self.owned

    def get_selected(self):
        return self.selected

    def get_price(self, name):
        return CHARACTERS.get(name, {}).get("price", 0)

    def can_buy(self, name):
        if name not in CHARACTERS:
            return False

        if self.is_owned(name):
            return False

        price = CHARACTERS[name]["price"]
        return self.item_manager.total_fruits() >= price

    # ================= ACTION =================
    def buy(self, name):
        if name not in CHARACTERS:
            return False

        if self.is_owned(name):
            return False

        if not self.can_buy(name):
            return False

        price = CHARACTERS[name]["price"]

        # ===== TRỪ HOA QUẢ (RAM) =====
        self.item_manager.remove_fruits(price)

        # ===== CẬP NHẬT NHÂN VẬT =====
        self.owned.append(name)
        self.selected = name

        # ===== LƯU SAVE (QUAN TRỌNG NHẤT) =====
        self.save.save_fruits(self.item_manager.count)   # 🔥 DÒNG BỊ THIẾU
        self.save.save_characters(self.owned, self.selected)

        return True


    def select(self, name):
        if name not in CHARACTERS:
            return False

        if not self.is_owned(name):
            return False

        self.selected = name
        self.save.save_characters(self.owned, self.selected)
        return True
