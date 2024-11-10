import sqlite3
import cProfile
import pstats

def test_sql_crud_operations():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    # ایجاد جدول
    cursor.execute('''
        CREATE TABLE items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            buy_price REAL,
            sell_price REAL,
            quantity INTEGER
        )
    ''')
    conn.commit()
    # ایجاد کالاها
    for i in range(1, 1001):
        cursor.execute('INSERT INTO items VALUES (?, ?, ?, ?, ?)', (i, f'Item {i}', i * 10, i * 12, i * 5))
    conn.commit()
    # خواندن کالاها
    for i in range(1, 1001):
        cursor.execute('SELECT * FROM items WHERE id=?', (i,))
        item = cursor.fetchone()
    # به‌روزرسانی کالاها
    for i in range(1, 1001):
        cursor.execute('UPDATE items SET quantity=? WHERE id=?', (1000, i))
    conn.commit()
    # حذف کالاها
    for i in range(1, 1001):
        cursor.execute('DELETE FROM items WHERE id=?', (i,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    profiler = cProfile.Profile()
    profiler.enable()
    test_sql_crud_operations()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(10)
