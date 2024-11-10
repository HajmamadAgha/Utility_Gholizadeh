import json
import os

class ItemManagerJSON:
    def __init__(self, filename='items.json'):
        self.filename = filename
        self.items = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.items = json.load(f)
        else:
            self.items = {}

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, indent=4, ensure_ascii=False)

    def create_item(self, item_id, name, buy_price, sell_price, quantity):
        item = {
            'id': item_id,
            'name': name,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'quantity': quantity
        }
        self.items[item_id] = item
        self.save()

    def read_item(self, item_id):
        return self.items.get(item_id)

    def update_item(self, item_id, **kwargs):
        item = self.items.get(item_id)
        if item:
            item.update(kwargs)
            self.items[item_id] = item
            self.save()
            return True
        return False

    def delete_item(self, item_id):
        if item_id in self.items:
            del self.items[item_id]
            self.save()
            return True
        return False

# مثال استفاده:
manager_json = ItemManagerJSON()
manager_json.create_item('1', 'Laptop', 1000, 1200, 10)
item = manager_json.read_item('1')
print(item)
manager_json.update_item('1', quantity=15)
manager_json.delete_item('1')
