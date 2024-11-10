import json
import os

class Item:
    def __init__(self, item_id, name, buy_price, sell_price, quantity):
        self.id = item_id
        self.name = name
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.quantity = quantity

class ItemRepository:
    def __init__(self, filename='items.json'):
        self.filename = filename
        self.items = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                items_data = json.load(f)
                self.items = {item_id: Item(**data) for item_id, data in items_data.items()}
        else:
            self.items = {}

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            items_data = {item_id: item.__dict__ for item_id, item in self.items.items()}
            json.dump(items_data, f, indent=4, ensure_ascii=False)

    def add_item(self, item):
        self.items[item.id] = item
        self.save()

    def get_item(self, item_id):
        return self.items.get(item_id)

    def update_item(self, item_id, **kwargs):
        item = self.items.get(item_id)
        if item:
            for key, value in kwargs.items():
                setattr(item, key, value)
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
repo = ItemRepository()
item = Item('1', 'Laptop', 1000, 1200, 10)
repo.add_item(item)
retrieved_item = repo.get_item('1')
print(retrieved_item.__dict__)
repo.update_item('1', quantity=15)
repo.delete_item('1')
