import msgpack
import os
import threading

# تعریف کلاس Item برای نگهداری اطلاعات کالا
class Item:
    def __init__(self, item_id, name, buy_price, sell_price, quantity):
        self.id = item_id                # شناسه کالا
        self.name = name                 # نام کالا
        self.buy_price = buy_price       # قیمت خرید
        self.sell_price = sell_price     # قیمت فروش
        self.quantity = quantity         # تعداد موجودی

    def to_dict(self):
        # تبدیل شیء به دیکشنری برای سریال‌سازی
        return {
            'id': self.id,
            'name': self.name,
            'buy_price': self.buy_price,
            'sell_price': self.sell_price,
            'quantity': self.quantity
        }

# تعریف کلاس Sale برای نگهداری اطلاعات فروش
class Sale:
    def __init__(self, sale_id, item_id, quantity, client, date):
        self.id = sale_id                # شناسه فروش
        self.item_id = item_id           # شناسه کالا
        self.quantity = quantity         # تعداد فروش رفته
        self.client = client             # نام مشتری
        self.date = date                 # تاریخ فروش

    def to_dict(self):
        # تبدیل شیء به دیکشنری برای سریال‌سازی
        return {
            'id': self.id,
            'item_id': self.item_id,
            'quantity': self.quantity,
            'client': self.client,
            'date': self.date
        }

# تعریف کلاس DataManager برای مدیریت داده‌ها
class DataManager:
    def __init__(self, items_filename='items.dat', sales_filename='sales.dat'):
        self.items_filename = items_filename    # نام فایل ذخیره‌سازی کالاها
        self.sales_filename = sales_filename    # نام فایل ذخیره‌سازی فروش‌ها
        self.items = {}         # دیکشنری کالاها: {item_id: Item}
        self.items_by_name = {} # دیکشنری کالاها بر اساس نام: {name: Item}
        self.sales = {}         # دیکشنری فروش‌ها: {sale_id: Sale}
        self.lock = threading.Lock()  # لاک برای مدیریت همزمانی
        self.load_data()        # بارگذاری داده‌ها از فایل‌ها

    # متد بارگذاری داده‌ها از فایل‌ها
    def load_data(self):
        # بارگذاری داده‌های کالاها
        if os.path.exists(self.items_filename):
            with open(self.items_filename, 'rb') as f:
                items_data = msgpack.unpackb(f.read(), raw=False)
                for item_dict in items_data:
                    item = Item(**item_dict)
                    self.items[item.id] = item
                    self.items_by_name[item.name] = item

        # بارگذاری داده‌های فروش‌ها
        if os.path.exists(self.sales_filename):
            with open(self.sales_filename, 'rb') as f:
                sales_data = msgpack.unpackb(f.read(), raw=False)
                for sale_dict in sales_data:
                    sale = Sale(**sale_dict)
                    self.sales[sale.id] = sale

    # متد ذخیره‌سازی کالاها در فایل
    def save_items(self):
        with self.lock:
            with open(self.items_filename, 'wb') as f:
                data = [item.to_dict() for item in self.items.values()]
                f.write(msgpack.packb(data, use_bin_type=True))

    # متد ذخیره‌سازی فروش‌ها در فایل
    def save_sales(self):
        with self.lock:
            with open(self.sales_filename, 'wb') as f:
                data = [sale.to_dict() for sale in self.sales.values()]
                f.write(msgpack.packb(data, use_bin_type=True))

    # ------------------- عملیات CRUD برای کالاها -------------------

    # ایجاد کالا (Create)
    def create_item(self, item_id, name, buy_price, sell_price, quantity):
        with self.lock:
            if item_id in self.items:
                return False  # آیتم با این ID وجود دارد
            item = Item(item_id, name, buy_price, sell_price, quantity)
            self.items[item_id] = item
            self.items_by_name[name] = item
            self.save_items()
            return True

    # خواندن کالا بر اساس ID (Read)
    def read_item_by_id(self, item_id):
        return self.items.get(item_id)

    # خواندن کالا بر اساس نام
    def read_item_by_name(self, name):
        return self.items_by_name.get(name)

    # به‌روزرسانی کالا (Update)
    def update_item(self, item_id, **kwargs):
        with self.lock:
            item = self.items.get(item_id)
            if item:
                for key, value in kwargs.items():
                    setattr(item, key, value)
                # به‌روزرسانی دیکشنری items_by_name در صورت تغییر نام
                if 'name' in kwargs:
                    self.items_by_name.pop(item.name, None)
                    self.items_by_name[kwargs['name']] = item
                self.save_items()
                return True
            return False

    # حذف کالا (Delete)
    def delete_item(self, item_id):
        with self.lock:
            item = self.items.pop(item_id, None)
            if item:
                self.items_by_name.pop(item.name, None)
                self.save_items()
                return True
            return False

    # ------------------- عملیات CRUD برای فروش‌ها -------------------

    # ایجاد فروش (Create)
    def create_sale(self, sale_id, item_id, quantity, client, date):
        with self.lock:
            if sale_id in self.sales:
                return False  # فروش با این ID وجود دارد
            if item_id not in self.items:
                return False  # کالای مورد نظر وجود ندارد
            sale = Sale(sale_id, item_id, quantity, client, date)
            self.sales[sale_id] = sale
            # کاهش تعداد موجودی کالا
            self.items[item_id].quantity -= quantity
            self.save_sales()
            self.save_items()
            return True

    # خواندن فروش (Read)
    def read_sale(self, sale_id):
        return self.sales.get(sale_id)

    # به‌روزرسانی فروش (Update)
    def update_sale(self, sale_id, **kwargs):
        with self.lock:
            sale = self.sales.get(sale_id)
            if sale:
                for key, value in kwargs.items():
                    setattr(sale, key, value)
                self.save_sales()
                return True
            return False

    # حذف فروش (Delete)
    def delete_sale(self, sale_id):
        with self.lock:
            sale = self.sales.pop(sale_id, None)
            if sale:
                # افزایش تعداد موجودی کالا به میزان حذف شده
                self.items[sale.item_id].quantity += sale.quantity
                self.save_sales()
                self.save_items()
                return True
            return False

    # ------------------- متدهای کمکی -------------------

    # جستجوی کالاها بر اساس بخشی از نام
    def search_items_by_name(self, name_part):
        return [item for item in self.items.values() if name_part.lower() in item.name.lower()]

    # دریافت تمام کالاها
    def get_all_items(self):
        return list(self.items.values())

    # دریافت تمام فروش‌ها
    def get_all_sales(self):
        return list(self.sales.values())

# ------------------- مثال از استفاده از DataManager -------------------

if __name__ == '__main__':
    # ایجاد یک شیء از DataManager
    manager = DataManager()

    # ---------- عملیات بر روی کالاها ----------
    # ایجاد چند کالا
    manager.create_item(1, 'لپ‌تاپ', 1000, 1200, 50)
    manager.create_item(2, 'تبلت', 500, 650, 30)
    manager.create_item(3, 'گوشی', 300, 400, 100)

    # خواندن کالا بر اساس ID
    item = manager.read_item_by_id(1)
    print(f"کالا با ID 1: {item.name}, قیمت فروش: {item.sell_price}, تعداد: {item.quantity}")

    # به‌روزرسانی کالا
    manager.update_item(1, sell_price=1100, quantity=45)
    item = manager.read_item_by_id(1)
    print(f"پس از به‌روزرسانی - کالا با ID 1: {item.name}, قیمت فروش: {item.sell_price}, تعداد: {item.quantity}")

    # حذف کالا
    manager.delete_item(3)
    print("کالای با ID 3 حذف شد.")

    # جستجوی کالاها بر اساس نام
    search_results = manager.search_items_by_name('لپ')
    print("نتایج جستجو برای 'لپ':")
    for item in search_results:
        print(f"- {item.name}")

    # ---------- عملیات بر روی فروش‌ها ----------
    # ایجاد فروش
    manager.create_sale(1, 1, 5, 'علی', '1402-08-20')
    manager.create_sale(2, 2, 2, 'مریم', '1402-08-21')

    # خواندن فروش
    sale = manager.read_sale(1)
    print(f"فروش با ID 1: کالای {sale.item_id}, تعداد: {sale.quantity}, مشتری: {sale.client}")

    # به‌روزرسانی فروش
    manager.update_sale(1, quantity=4)
    sale = manager.read_sale(1)
    print(f"پس از به‌روزرسانی - فروش با ID 1: کالای {sale.item_id}, تعداد: {sale.quantity}, مشتری: {sale.client}")

    # حذف فروش
    manager.delete_sale(2)
    print("فروش با ID 2 حذف شد.")

    # ---------- نمایش تمام کالاها ----------
    print("لیست تمام کالاها:")
    for item in manager.get_all_items():
        print(f"- {item.name}, تعداد: {item.quantity}")

    # ---------- نمایش تمام فروش‌ها ----------
    print("لیست تمام فروش‌ها:")
    for sale in manager.get_all_sales():
        print(f"- فروش ID {sale.id}, کالای {sale.item_id}, مشتری: {sale.client}")
