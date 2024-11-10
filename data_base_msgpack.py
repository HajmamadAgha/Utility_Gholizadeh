import msgpack
import os

class ItemManagerMsgPack:
    def __init__(self, filename='items.dat'):
        self.filename = filename
        self.items = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                data = msgpack.unpackb(f.read(), raw=False)
                self.items = data
        else:
            self.items = {}

    def save(self):
        with open(self.filename, 'wb') as f:
            data = self.items
            f.write(msgpack.packb(data, use_bin_type=True))

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
manager_msgpack = ItemManagerMsgPack()
manager_msgpack.create_item('1', 'Laptop', 1000, 1200, 10)
item = manager_msgpack.read_item('1')
print(item)
manager_msgpack.update_item('1', quantity=15)
manager_msgpack.delete_item('1')
