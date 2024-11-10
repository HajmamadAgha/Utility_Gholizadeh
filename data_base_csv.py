import csv
import os

class ItemManagerCSV:
    def __init__(self, filename='items.csv'):
        self.filename = filename
        self.items = []
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.items = list(reader)
        else:
            self.items = []

    def save(self):
        with open(self.filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'name', 'buy_price', 'sell_price', 'quantity']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.items)

    def create_item(self, item_id, name, buy_price, sell_price, quantity):
        item = {
            'id': item_id,
            'name': name,
            'buy_price': str(buy_price),
            'sell_price': str(sell_price),
            'quantity': str(quantity)
        }
        self.items.append(item)
        self.save()

    def read_item(self, item_id):
        for item in self.items:
            if item['id'] == item_id:
                return item
        return None

    def update_item(self, item_id, **kwargs):
        for item in self.items:
            if item['id'] == item_id:
                item.update({k: str(v) for k, v in kwargs.items()})
                self.save()
                return True
        return False

    def delete_item(self, item_id):
        for i, item in enumerate(self.items):
            if item['id'] == item_id:
                del self.items[i]
                self.save()
                return True
        return False

# مثال استفاده:
manager_csv = ItemManagerCSV()
manager_csv.create_item('1', 'Laptop', 1000, 1200, 10)
item = manager_csv.read_item('1')
print(item)
manager_csv.update_item('1', quantity=15)
manager_csv.delete_item('1')
