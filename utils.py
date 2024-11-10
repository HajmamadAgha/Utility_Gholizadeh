import tkinter as tk
from tkinter import messagebox
import ttkbootsrtap as ttk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DatabaseManager:
    def __init__(self, db_name):
        self.conn   =   sqlite3.connect(db_name)
        self.cursor =   self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        try:
            items_query='''
                CREATE TABLE IF NOT EXISTS items(
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT    NOT NULL UNIQUE,
                    buy_prc     REAL    NOT NULL,
                    sel_prc     REAL    NOT NULL,
                    quantity    INTEGER NOT NULL
                )
            '''

            sales_query='''
                CREATE TABLE IF NOT EXISTS sales(
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id     INTEGER NOT NULL,
                    quantity    INTEGER NOT NULL,
                    client      TEXT    NOT NULL,
                    date        TEXT    NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES items(id)
                )
            '''
            
            self.cursor.execute(items_query)
            self.cursor.execute(sales_query)
            self.conn.commit()
        except Exception as e:
            print(f"Error while creating tables:\n{e}")

    def search_items_db(self, value):
        query   =   "SELECT quantity, sel_prc, buy_prc, name, id FROM items WHERE name LIKE ?"
        self.cursor.execute(query, ('%' + value + '%',))
        data    =   self.cursor.fetchall()
        return data

    def insert_item_db(self, values):
        try:
            query   =   "INSERT INTO items (name, buy_prc, sel_prc, quantity) VALUES (?,?,?,?)"
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            messagebox.showerror("خطا", "کالایی با این نام قبلاً ثبت شده است.")
            return False
        except Exception as e:
            print(f"Error while inserting item:\n{e}")
            return False

    def update_item_db(self, item_id, values):
        try:
            query = "UPDATE items SET name=?, buy_prc=?, sel_prc=?, quantity=? WHERE id=?"
            self.cursor.execute(query, (*values, item_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error while updating item:\n{e}")
            return False

    def delete_item_db(self, item_id):
        try:
            query = "DELETE FROM items WHERE id=?"
            self.cursor.execute(query, (item_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error while deleting item:\n{e}")
            return False

    def insert_sale_db(self, values):
        try:
            query   =   "INSERT INTO sales (item_id, quantity, client, date) VALUES(?,?,?,?)"
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error while inserting sale:\n{e}")
            return False

    def retrieve_item_list_db(self):
        query   =   "SELECT name, id FROM items"
        self.cursor.execute(query)
        data    =   self.cursor.fetchall()
        return data

    def get_sales_data(self):
        query = '''
            SELECT items.name, SUM(sales.quantity)
            FROM items
            JOIN sales ON items.id = sales.item_id
            GROUP BY items.name
            ORDER BY SUM(sales.quantity) DESC
        '''
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data

    def get_inventory_data(self):
        query = '''
            SELECT name, quantity FROM items
        '''
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data

    def close_connection(self):
        self.conn.close()

class UIF(ttk.Window):
    def __init__(self, db):
        super().__init__()
        self.title("Amir Laptop Store")
        self.db =   db
        self.sys_width  =   self.winfo_screenwidth()
        self.sys_height =   self.winfo_screenheight()
        self.geometry(f"{self.sys_width}x{self.sys_height}")
        self.state("zoomed")
        self.configure(bg= "lightgray")

        # بهبود گرافیک با استفاده از تم
        style = ttk.Style(self)
        style.theme_use('clam')

        self.setup_layout()

    def setup_layout(self):
        self.grid_columnconfigure(0, weight= 20)
        self.grid_columnconfigure(1, weight= 10)
        self.grid_columnconfigure(2, weight= 10)

        self.grid_rowconfigure(0, weight= 5)
        self.grid_rowconfigure(1, weight= 70)
        self.grid_rowconfigure(2, weight= 25)

        self.search_frm   =   ttk.Frame(self, padding=10)
        self.search_frm.grid(row= 0, column= 0, sticky= "nsew", pady=10, padx=10)
        
        self.chrt_frm   =   ttk.Frame(self, padding=10)
        self.chrt_frm.grid(row= 1, column= 0, sticky= "nsew", pady=10, padx=10)
        
        # حذف فریم ویرایش از اینجا

        self.note_frm   =   ttk.Frame(self, padding=10)
        self.note_frm.grid(row= 0, column= 1, sticky= "nsew", pady=10, padx=10, rowspan=2, columnspan=2)
        
        self.plot_frm   =   ttk.Frame(self, padding=10)
        self.plot_frm.grid(row= 2, column= 1, sticky= "nsew", pady=10, padx=10)
        
        self.report_frm   =   ttk.Frame(self, padding=10)
        self.report_frm.grid(row= 2, column= 2, sticky= "nsew", pady=10, padx=10)

        self.create_search_frm_content()
        self.create_chrt_frm_content()
        # self.create_modif_frm_content()  # حذف این متد
        self.create_note_frm_content()
        self.create_plot_frm_content()
        self.create_report_frm_content()
        
    def create_search_frm_content(self):
        self.search_frm.grid_columnconfigure(0, weight=1)
        self.search_frm.grid_columnconfigure(1, weight=2)
        self.search_frm.grid_columnconfigure(2, weight=1)
        self.search_frm.grid_rowconfigure(0, weight=1)

        tk.Label(self.search_frm, text= "جستجوی کالا:", font=('Arial', 12)).grid(row=0, column=0, sticky="w", pady=10, padx=5)
        self.search_entry   =   ttk.Entry(self.search_frm, justify= "left", font=('Arial', 12))
        self.search_entry.grid(row=0, column=1, sticky="ew", pady=10, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_item)

        self.show_all_items_btn     =   ttk.Button(self.search_frm, text= "نمایش تمام کالاها", command= self.show_all_items)
        self.show_all_items_btn.grid(row= 0, column=2, sticky= "e", padx= 5, pady=10)

    def create_chrt_frm_content(self):
        self.item_tree  =   ttk.Treeview(self.chrt_frm, selectmode='browse')
        self.item_tree["columns"]   =   ["Quantity", "Sell_Price", "Buy_Price", "Name", "Remove"]
        self.item_tree.pack(fill= "both", expand= True)
        self.note_frm_width =   self.chrt_frm.winfo_width()

        self.item_tree.column("#0", width= 0, stretch= tk.NO)
        self.item_tree.column("Name", anchor= tk.W, width=200)
        self.item_tree.column("Buy_Price", anchor= tk.CENTER, width=100)
        self.item_tree.column("Sell_Price", anchor= tk.CENTER, width=100)
        self.item_tree.column("Quantity", anchor= tk.CENTER, width=80)
        self.item_tree.column("Remove", anchor=tk.CENTER, width=80)

        self.item_tree.heading("#0", anchor= tk.CENTER, text=   "")
        self.item_tree.heading("Name", anchor= tk.W, text= "نام کالا")
        self.item_tree.heading("Buy_Price", anchor= tk.CENTER, text= "قیمت خرید")
        self.item_tree.heading("Sell_Price", anchor= tk.CENTER, text= "قیمت فروش")
        self.item_tree.heading("Quantity", anchor= tk.CENTER, text= "تعداد")
        self.item_tree.heading("Remove", anchor=tk.CENTER, text="حذف")

        # اتصال رویداد انتخاب آیتم
        self.item_tree.bind("<ButtonRelease-1>", self.on_item_select)
        self.item_tree.bind("<Double-1>", self.on_treeview_double_click)

    def validate_input(self, input_if_allowed):
        # اینجا می‌توانید اعتبارسنجی‌های لازم را اعمال کنید
        return True

    def search_item(self, event):
        value   =   self.search_entry.get()
        data    =   self.db.search_items_db(value)
        self.insert_to_tree(self.item_tree, data)

    def show_all_items(self):
        records =   self.db.search_items_db("")
        self.insert_to_tree(self.item_tree,records)

    def clear_tree(self, tree):
        rows    =   tree.get_children()
        for row in rows:
            tree.delete(row)

    def insert_to_tree(self, tree, data):
        self.clear_tree(tree)
        for record in data:
            iid = record[4]
            tree.insert("", "end", iid=iid, values= (record[0], record[1], record[2], record[3], "حذف"))

    def on_item_select(self, event):
        selected_item = self.item_tree.identify_row(event.y)
        if selected_item:
            self.selected_item_id = selected_item
        else:
            self.selected_item_id = None

    def on_treeview_double_click(self, event):
        region = self.item_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.item_tree.identify_column(event.x)
            if column == '#5':  # ستون حذف
                self.delete_item()
            else:
                self.open_edit_tab()

    def delete_item(self):
        if self.selected_item_id:
            confirm = messagebox.askyesno("تأیید حذف", "آیا از حذف این کالا مطمئن هستید؟")
            if confirm:
                success = self.db.delete_item_db(self.selected_item_id)
                if success:
                    messagebox.showinfo("موفقیت", "کالا با موفقیت حذف شد.")
                    self.show_all_items()
                    self.selected_item_id = None
                else:
                    messagebox.showerror("خطا", "خطا در حذف کالا.")
        else:
            messagebox.showwarning("هشدار", "لطفاً یک کالا را انتخاب کنید.")

    def open_edit_tab(self):
        if self.selected_item_id:
            self.notebook.select(self.edit_tab)
            item_data = self.db.search_items_db_by_id(self.selected_item_id)
            if item_data:
                record = item_data[0]
                # مقداردهی فیلدهای ویرایش
                self.edit_item_name_entry.delete(0, tk.END)
                self.edit_item_name_entry.insert(0, record[3])
                self.edit_item_buy_prc_entry.delete(0, tk.END)
                self.edit_item_buy_prc_entry.insert(0, record[2])
                self.edit_item_sell_prc_entry.delete(0, tk.END)
                self.edit_item_sell_prc_entry.insert(0, record[1])
                self.edit_item_quantity_entry.delete(0, tk.END)
                self.edit_item_quantity_entry.insert(0, record[0])
                self.selected_item_id = record[4]
        else:
            messagebox.showwarning("هشدار", "لطفاً یک کالا را انتخاب کنید.")

    def create_note_frm_content(self):
        self.notebook   =   ttk.Notebook(self.note_frm)
        self.note_frm.grid_rowconfigure(0, weight=1)
        self.note_frm.grid_columnconfigure(0, weight=1)
        self.notebook.grid(row=0,column=0, sticky="nsew")

        self.create_item_tab()
        self.create_sale_tab()
        self.create_edit_tab()  # اضافه کردن تب ویرایش

    def create_item_tab(self):
        self.item_tab   =   ttk.Frame(self.notebook)
        self.notebook.add(self.item_tab, text= "ثبت کالا")
        for i in range(5):
            self.item_tab.grid_columnconfigure(i, weight= 1)
        for j in range(8):
            self.item_tab.grid_rowconfigure(j, weight= 1)
        
        tk.Label(self.item_tab, text= "نام آیتم:", font=('Arial', 12)).grid(row=0, column=0, sticky="e", pady= 10, padx= 10)
        tk.Label(self.item_tab, text= "قیمت خرید:", font=('Arial', 12)).grid(row=1, column=0, sticky="e", pady= 10, padx= 10)
        tk.Label(self.item_tab, text= "قیمت فروش:", font=('Arial', 12)).grid(row=2, column=0, sticky="e", pady= 10, padx= 10)
        tk.Label(self.item_tab, text= "تعداد:", font=('Arial', 12)).grid(row=3, column=0, sticky="e", pady= 10, padx= 10)

        self.item_name_entry    =   ttk.Entry(self.item_tab, justify="left", width=30, font=('Arial', 12))
        self.item_buy_prc_entry =   ttk.Entry(self.item_tab, justify="left", width=30, font=('Arial', 12))
        self.item_sell_prc_entry=   ttk.Entry(self.item_tab, justify="left", width=30, font=('Arial', 12))
        self.item_quantity_entry=   ttk.Entry(self.item_tab, justify="left", width=30, font=('Arial', 12))

        self.item_name_entry.grid(row=0, column=1, sticky="w", pady=10, padx=10)
        self.item_buy_prc_entry.grid(row=1, column=1, sticky="w", pady=10, padx=10)
        self.item_sell_prc_entry.grid(row=2, column=1, sticky="w", pady=10, padx=10)
        self.item_quantity_entry.grid(row=3, column=1, sticky="w", pady=10, padx=10)

        self.item_register_btn  =   ttk.Button(self.item_tab, text= "ثبت کالا", command= self.register_item)
        self.item_register_btn.grid(row=4, column= 1, sticky="e", padx= 10, pady=20)

    def register_item(self):
        input_name      =   self.item_name_entry.get()
        input_buy_prc   =   self.item_buy_prc_entry.get()
        input_sel_prc   =   self.item_sell_prc_entry.get()
        input_quantity  =   self.item_quantity_entry.get()
        if input_name and input_buy_prc and input_sel_prc and input_quantity:
            try:
                buy_prc = float(input_buy_prc)
                sel_prc = float(input_sel_prc)
                quantity = int(input_quantity)
                input_item  =   (input_name, buy_prc, sel_prc, quantity)
                success = self.db.insert_item_db(input_item)
                if success:
                    messagebox.showinfo("موفقیت", "کالا با موفقیت ثبت شد.")
                    self.clear_item_tab_fields()
                    self.show_all_items()
                else:
                    messagebox.showerror("خطا", "خطا در ثبت کالا.")
            except ValueError:
                messagebox.showerror("خطا", "لطفاً مقادیر معتبر وارد کنید.")
        else:
            messagebox.showwarning("هشدار","لطفاً تمام فیلدها را پر کنید.")

    def clear_item_tab_fields(self):
        self.item_name_entry.delete(0,"end")
        self.item_buy_prc_entry.delete(0,"end")
        self.item_sell_prc_entry.delete(0,"end")
        self.item_quantity_entry.delete(0,"end")

    def create_sale_tab(self):
        self.sale_tab   =   ttk.Frame(self.notebook)
        self.notebook.add(self.sale_tab, text= "ثبت فروش")
        for i in range(5):
            self.sale_tab.grid_columnconfigure(i, weight=1)
        for j in range(12):
            self.sale_tab.grid_rowconfigure(j, weight=1)
        
        tk.Label(self.sale_tab, text= "آیتم:", font=('Arial', 12)).grid(row= 0, column=0, sticky="e", pady=10, padx=10)
        self.item_name_combo    =   ttk.Combobox(self.sale_tab, justify="left", values= [], state= "readonly", font=('Arial', 12))
        self.item_name_combo.grid(row= 0, column=1, sticky="w", pady= 10, padx= 10)
        self.item_name_combo.bind("<Button-1>", self.update_item_combo)

        tk.Label(self.sale_tab, text= "تعداد:", font=('Arial', 12)).grid(row= 1, column=0, sticky="e", padx= 10, pady= 10)
        self.sale_quantity_spin =   ttk.Spinbox(self.sale_tab, from_=1, to=1e4, font=('Arial', 12))
        self.sale_quantity_spin.grid(row=1, column= 1, sticky="w", pady=10, padx=10)

        tk.Label(self.sale_tab, text="مشتری:", font=('Arial', 12)).grid(row= 2, column=0, sticky="e", padx=10, pady=10)
        self.sale_client_ent    =   ttk.Entry(self.sale_tab, justify="left", font=('Arial', 12))
        self.sale_client_ent.grid(row= 2, column= 1, sticky= "w", pady=10, padx=10)

        tk.Label(self.sale_tab, text="تاریخ:", font=('Arial', 12)).grid(row= 3, column=0, sticky="e", pady=10, padx=10)
        self.sale_date_entry    =   ttk.Entry(self.sale_tab, font=('Arial', 12))
        self.sale_date_entry.grid(row= 3, column=1, sticky="w", padx=10, pady=10)
        self.sale_date_entry.insert(0, "1403-08-20")

        self.sale_register_btn  =   ttk.Button(self.sale_tab, text= "ثبت فروش", command= self.sale_register)
        self.sale_register_btn.grid(row= 4, column=1, sticky="e", padx=10, pady=20)

    def sale_register(self):
        item_name   =   self.item_name_combo.get()
        if item_name in self.item_name_data:
            item_id     =   self.item_name_data[item_name]
            sale_qnty   =   self.sale_quantity_spin.get()
            sale_client =   self.sale_client_ent.get()
            sale_date   =   self.sale_date_entry.get()
            if item_name and sale_qnty and sale_client and sale_date:
                try:
                    sale_qnty = int(sale_qnty)
                    values   =   (item_id, sale_qnty, sale_client, sale_date)
                    success = self.db.insert_sale_db(values)
                    if success:
                        messagebox.showinfo("موفقیت", "فروش با موفقیت ثبت شد.")
                        self.clear_sale_fields()
                    else:
                        messagebox.showerror("خطا", "خطا در ثبت فروش.")
                except ValueError:
                    messagebox.showerror("خطا", "لطفاً مقادیر معتبر وارد کنید.")
            else:
                messagebox.showwarning("هشدار", "لطفاً تمام فیلدها را پر کنید.")
        else:
            messagebox.showwarning("هشدار", "لطفاً یک آیتم معتبر انتخاب کنید.")

    def clear_sale_fields(self):
        self.item_name_combo.set('')
        self.sale_quantity_spin.delete(0, tk.END)
        self.sale_quantity_spin.insert(0, '1')
        self.sale_client_ent.delete(0, tk.END)
        self.sale_date_entry.delete(0, tk.END)
        self.sale_date_entry.insert(0, "1403-08-20")

    def update_item_combo(self, event):
        items = self.db.retrieve_item_list_db()
        self.item_name_data = dict(items)
        self.item_name_combo['values'] = list(self.item_name_data.keys())

    def create_edit_tab(self):
        self.edit_tab   =   ttk.Frame(self.notebook)
        self.notebook.add(self.edit_tab, text= "ویرایش")
        for i in range(5):
            self.edit_tab.grid_columnconfigure(i, weight=1)
        for j in range(12):
            self.edit_tab.grid_rowconfigure(j, weight=1)

        tk.Label(self.edit_tab, text= "انتخاب کالا:", font=('Arial', 12)).grid(row=0, column=0, sticky="e", pady=10, padx=10)
        self.edit_item_combo    =   ttk.Combobox(self.edit_tab, justify="left", values= [], state= "readonly", font=('Arial', 12))
        self.edit_item_combo.grid(row=0, column=1, sticky="w", pady=10, padx=10)
        self.edit_item_combo.bind("<<ComboboxSelected>>", self.load_item_data)
        self.edit_item_combo.bind("<Button-1>", self.update_edit_combo)

        tk.Label(self.edit_tab, text= "نام آیتم:", font=('Arial', 12)).grid(row=1, column=0, sticky="e", pady=10, padx=10)
        tk.Label(self.edit_tab, text= "قیمت خرید:", font=('Arial', 12)).grid(row=2, column=0, sticky="e", pady=10, padx=10)
        tk.Label(self.edit_tab, text= "قیمت فروش:", font=('Arial', 12)).grid(row=3, column=0, sticky="e", pady=10, padx=10)
        tk.Label(self.edit_tab, text= "تعداد:", font=('Arial', 12)).grid(row=4, column=0, sticky="e", pady=10, padx=10)

        self.edit_item_name_entry    =   ttk.Entry(self.edit_tab, justify="left", width=30, font=('Arial', 12))
        self.edit_item_buy_prc_entry =   ttk.Entry(self.edit_tab, justify="left", width=30, font=('Arial', 12))
        self.edit_item_sell_prc_entry=   ttk.Entry(self.edit_tab, justify="left", width=30, font=('Arial', 12))
        self.edit_item_quantity_entry=   ttk.Entry(self.edit_tab, justify="left", width=30, font=('Arial', 12))

        self.edit_item_name_entry.grid(row=1, column=1, sticky="w", pady=10, padx=10)
        self.edit_item_buy_prc_entry.grid(row=2, column=1, sticky="w", pady=10, padx=10)
        self.edit_item_sell_prc_entry.grid(row=3, column=1, sticky="w", pady=10, padx=10)
        self.edit_item_quantity_entry.grid(row=4, column=1, sticky="w", pady=10, padx=10)

        self.update_item_btn = ttk.Button(self.edit_tab, text="بروزرسانی کالا", command=self.update_item)
        self.update_item_btn.grid(row=5, column=1, sticky="e", pady=10, padx=10)

        self.delete_item_btn = ttk.Button(self.edit_tab, text="حذف کالا", command=self.delete_item_from_edit)
        self.delete_item_btn.grid(row=5, column=0, sticky="w", pady=10, padx=10)

        self.selected_item_id = None

    def update_edit_combo(self, event):
        items = self.db.retrieve_item_list_db()
        self.edit_item_name_data = dict(items)
        self.edit_item_combo['values'] = list(self.edit_item_name_data.keys())

    def load_item_data(self, event):
        item_name = self.edit_item_combo.get()
        if item_name in self.edit_item_name_data:
            item_id = self.edit_item_name_data[item_name]
            item_data = self.db.search_items_db_by_id(item_id)
            if item_data:
                record = item_data[0]
                self.edit_item_name_entry.delete(0, tk.END)
                self.edit_item_name_entry.insert(0, record[3])
                self.edit_item_buy_prc_entry.delete(0, tk.END)
                self.edit_item_buy_prc_entry.insert(0, record[2])
                self.edit_item_sell_prc_entry.delete(0, tk.END)
                self.edit_item_sell_prc_entry.insert(0, record[1])
                self.edit_item_quantity_entry.delete(0, tk.END)
                self.edit_item_quantity_entry.insert(0, record[0])
                self.selected_item_id = record[4]
        else:
            messagebox.showwarning("هشدار", "کالا یافت نشد.")

    def update_item(self):
        if self.selected_item_id:
            name = self.edit_item_name_entry.get()
            buy_prc = self.edit_item_buy_prc_entry.get()
            sel_prc = self.edit_item_sell_prc_entry.get()
            quantity = self.edit_item_quantity_entry.get()
            if name and buy_prc and sel_prc and quantity:
                try:
                    buy_prc = float(buy_prc)
                    sel_prc = float(sel_prc)
                    quantity = int(quantity)
                    values = (name, buy_prc, sel_prc, quantity)
                    success = self.db.update_item_db(self.selected_item_id, values)
                    if success:
                        messagebox.showinfo("موفقیت", "کالا با موفقیت بروزرسانی شد.")
                        self.show_all_items()
                    else:
                        messagebox.showerror("خطا", "خطا در بروزرسانی کالا.")
                except ValueError:
                    messagebox.showerror("خطا", "لطفاً مقادیر معتبر وارد کنید.")
            else:
                messagebox.showwarning("هشدار", "لطفاً تمام فیلدها را پر کنید.")
        else:
            messagebox.showwarning("هشدار", "لطفاً یک کالا را انتخاب کنید.")

    def delete_item_from_edit(self):
        if self.selected_item_id:
            confirm = messagebox.askyesno("تأیید حذف", "آیا از حذف این کالا مطمئن هستید؟")
            if confirm:
                success = self.db.delete_item_db(self.selected_item_id)
                if success:
                    messagebox.showinfo("موفقیت", "کالا با موفقیت حذف شد.")
                    self.show_all_items()
                    # پاک کردن ورودی‌های ویرایش
                    self.edit_item_combo.set('')
                    self.edit_item_name_entry.delete(0, tk.END)
                    self.edit_item_buy_prc_entry.delete(0, tk.END)
                    self.edit_item_sell_prc_entry.delete(0, tk.END)
                    self.edit_item_quantity_entry.delete(0, tk.END)
                    self.selected_item_id = None
                else:
                    messagebox.showerror("خطا", "خطا در حذف کالا.")
        else:
            messagebox.showwarning("هشدار", "لطفاً یک کالا را انتخاب کنید.")

    def create_plot_frm_content(self):
        self.plot_frm.grid_rowconfigure(0, weight=1)
        self.plot_frm.grid_columnconfigure(0, weight=1)
        data = self.db.get_sales_data()
        if data:
            items = [x[0] for x in data]
            quantities = [x[1] for x in data]
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.bar(items, quantities)
            ax.set_xlabel('کالاها')
            ax.set_ylabel('مقدار فروش')
            ax.set_title('نمودار فروش')
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frm)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        else:
            tk.Label(self.plot_frm, text="داده‌ای برای نمایش وجود ندارد.").grid(row=0, column=0)

    def create_report_frm_content(self):
        self.report_frm.grid_rowconfigure(0, weight=1)
        self.report_frm.grid_columnconfigure(0, weight=1)
        data = self.db.get_inventory_data()
        if data:
            items = [x[0] for x in data]
            quantities = [x[1] for x in data]
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.pie(quantities, labels=items, autopct='%1.1f%%')
            ax.set_title('موجودی کالاها')
            canvas = FigureCanvasTkAgg(fig, master=self.report_frm)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        else:
            tk.Label(self.report_frm, text="داده‌ای برای نمایش وجود ندارد.").grid(row=0, column=0)

if __name__ == "__main__":
    db  =   DatabaseManager("LaptopStore.db")
    app =   UIF(db)
    app.show_all_items()  # نمایش تمام کالاها در ابتدای برنامه
    app.mainloop()
    db.close_connection()
