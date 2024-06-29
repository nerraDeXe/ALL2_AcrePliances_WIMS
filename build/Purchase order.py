import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date


class SalesVendorApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect('AcrePliances.db')
        self.cursor = self.connector.cursor()

        self.connector.execute(
            'CREATE TABLE IF NOT EXISTS Orders ('
            'ORDER_ID INTEGER PRIMARY KEY, '
            'PRODUCT_NAME VARCHAR(20), '
            'PRODUCT_ID TEXT, '
            'CATEGORY TEXT, '
            'QUANTITY INTEGER, '
            'VENDOR_ID INTEGER, '
            'FOREIGN KEY(VENDOR_ID) REFERENCES Vendors(VENDOR_ID))'
        )

        self.connector.commit()

        self.acre_connector = sqlite3.connect('AcrePliances.db')
        self.acre_cursor = self.acre_connector.cursor()
        self.acre_cursor.execute(
            'CREATE TABLE IF NOT EXISTS Inventory ('
            'PRODUCT_REAL_ID INTEGER PRIMARY KEY, '
            'date DATE, '
            'PRODUCT_NAME TEXT, '
            'PRODUCT_ID TEXT, '
            'STOCKS INTEGER, '
            'CATEGORY VARCHAR(30), '
            'PURCHASE_PRICE FLOAT, '
            'SELLING_PRICE FLOAT, '
            'LOCATION VARCHAR(30), '
            'INTERNAL_REFERENCE VARCHAR(30))'
        )
        self.acre_connector.commit()

        self.root = root
        self.username = username
        self.root.title('Sales and Vendor Management')
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')

        self.create_widgets()
        self.load_order_data()
        self.load_vendor_data()

    def create_widgets(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="PURCHASE ORDER MANAGEMENT", font=("Helvetica", 16),
                                   text_color='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        welcome_label = ctk.CTkLabel(top_frame, text=f"Welcome, {self.username}", font=("Helvetica", 12),
                                     text_color='white')
        welcome_label.pack(side=tk.LEFT, padx=20, pady=20)

        left_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=20)

        self.add_purchase_order_button = ctk.CTkButton(left_frame, text="ADD PURCHASE ORDER", fg_color='#FFFFFF',
                                                       text_color='#000000',
                                                       command=self.create_purchase_order_window())
        self.add_purchase_order_button.pack(pady=10)

        self.edit_purchase_order_button = ctk.CTkButton(left_frame, text="EDIT PURCHASE ORDER", fg_color='#FFFFFF',
                                                        text_color='#000000', command=self.edit_order_window)
        self.edit_purchase_order_button.pack(pady=10)

        self.delete_purchase_order_button = ctk.CTkButton(left_frame, text="DELETE PURCHASE ORDER", fg_color='#FFFFFF',
                                                          text_color='#000000', command=self.delete_order)
        self.delete_purchase_order_button.pack(pady=10)

        self.complete_order_button = ctk.CTkButton(left_frame, text="COMPLETE ORDER", fg_color='#FFFFFF',
                                                   text_color='#000000', command=self.complete_order_window)
        self.complete_order_button.pack(pady=10)

        self.back_button = ctk.CTkButton(left_frame, text="Back", command=self.close_subpanel)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = ctk.CTkFrame(self.root, fg_color='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=20)

        self.order_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.order_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.vendor_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.vendor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        order_details_label = ctk.CTkLabel(self.order_frame, text="Purchase Order Details:", font=("Helvetica", 20, 'bold'),
                                           text_color='black')
        order_details_label.pack(anchor=tk.W, pady=10)

        self.order_tree = ttk.Treeview(self.order_frame, columns=(
            "ID", "Product Name", "Product ID", "Category", "Quantity", "Vendor ID"), show='headings')
        self.order_tree.heading("ID", text="ID")
        self.order_tree.heading("Product Name", text="Product Name")
        self.order_tree.heading("Product ID", text="Product ID")
        self.order_tree.heading("Category", text="Category")
        self.order_tree.heading("Quantity", text="Quantity")
        self.order_tree.heading("Vendor ID", text="Vendor ID")
        self.order_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        vendor_details_label = ctk.CTkLabel(self.vendor_frame, text="Vendor Details:", font=("Helvetica", 20, 'bold'),
                                            text_color='black')
        vendor_details_label.pack(anchor=tk.W, pady=10)

        self.vendor_tree = ttk.Treeview(self.vendor_frame, columns=("ID", "Name", "Email", "Phone", "Company"),
                                        show='headings')
        self.vendor_tree.heading("ID", text="ID")
        self.vendor_tree.heading("Name", text="Name")
        self.vendor_tree.heading("Email", text="Email")
        self.vendor_tree.heading("Phone", text="Phone")
        self.vendor_tree.heading("Company", text="Company")
        self.vendor_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def close_subpanel(self):
        subprocess.Popen(["python", "admin_panel.py"])  # Assuming this line opens another script or window
        self.root.destroy()  # Close the main window and all associated frames

    def load_order_data(self):
        self.order_tree.delete(*self.order_tree.get_children())

        self.cursor.execute('SELECT * FROM Orders')
        rows = self.cursor.fetchall()

        for row in rows:
            self.order_tree.insert('', 'end', values=row)

    def create_purchase_order_window(self):
        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Add Sales Order')
        self.extra_window.geometry('600x600')
        title_label = ctk.CTkLabel(self.extra_window, text="ADD NEW SALES ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)

        # Product Name
        name_frame = ctk.CTkFrame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = ctk.CTkLabel(name_frame, text="Product Name:")
        name_label.pack(side=tk.LEFT)
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Category
        category_frame = ctk.CTkFrame(self.extra_window)
        category_frame.pack(pady=5, padx=10, fill=tk.X)
        category_label = ctk.CTkLabel(category_frame, text="Category:")
        category_label.pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(category_frame, textvariable=self.category_var,
                                          values=["Electronics", "Appliances", "Personal Care", "Homeware",
                                                  "Furniture"])
        self.category_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Quantity
        quantity_frame = ctk.CTkFrame(self.extra_window)
        quantity_frame.pack(pady=5, padx=10, fill=tk.X)
        quantity_label = ctk.CTkLabel(quantity_frame, text="Quantity:")
        quantity_label.pack(side=tk.LEFT)
        self.quantity_entry = ctk.CTkEntry(quantity_frame)
        self.quantity_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Vendor ID
        vendor_id_frame = ctk.CTkFrame(self.extra_window)
        vendor_id_frame.pack(pady=5, padx=10, fill=tk.X)
        vendor_id_label = ctk.CTkLabel(vendor_id_frame, text="Vendor ID:")
        vendor_id_label.pack(side=tk.LEFT)
        self.vendor_id_var = tk.StringVar()
        self.vendor_id_menu = ttk.Combobox(vendor_id_frame, textvariable=self.vendor_id_var)
        self.vendor_id_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.load_vendor_ids()

        add_button = ctk.CTkButton(self.extra_window, text="Add Order", command=self.add_order)
        add_button.pack(pady=10)

        clear_button = ctk.CTkButton(self.extra_window, text="Clear", command=self.clear_order_entries)
        clear_button.pack(pady=10)

    def load_vendor_ids(self):
        self.cursor.execute('SELECT VENDOR_ID FROM Vendors')
        vendor_ids = [row[0] for row in self.cursor.fetchall()]
        self.vendor_id_menu['values'] = vendor_ids

    def add_order(self):
        product_name = self.name_entry.get()
        category = self.category_var.get()
        quantity = self.quantity_entry.get()
        vendor_id = self.vendor_id_var.get()

        if product_name and category and quantity and vendor_id:
            product_id = self.generate_product_id(category)
            self.cursor.execute(
                'INSERT INTO Orders (PRODUCT_NAME, PRODUCT_ID, CATEGORY, QUANTITY, VENDOR_ID) VALUES (?, ?, ?, ?, ?)',
                (product_name, product_id, category, quantity, vendor_id)
            )
            self.connector.commit()
            self.load_order_data()
            messagebox.showinfo('Success', 'Order added successfully!')
            self.extra_window.destroy()
        else:
            messagebox.showwarning('Error', 'Please fill in all fields.')

    def generate_product_id(self, category):
        self.cursor.execute('SELECT COUNT(*) FROM Orders WHERE CATEGORY=?', (category,))
        count = self.cursor.fetchone()[0]
        product_id = f"{category[0].upper()}{count + 1:03d}"
        return product_id

    def edit_order_window(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select an order to edit.')
            return

        order_id = self.order_tree.item(selected_item)['values'][0]
        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Edit Sales Order')
        self.extra_window.geometry('600x600')

        title_label = ctk.CTkLabel(self.extra_window, text="EDIT SALES ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)

        self.cursor.execute('SELECT * FROM Orders WHERE ORDER_ID=?', (order_id,))
        order = self.cursor.fetchone()

        self.edit_order_id = order[0]

        # Product Name
        name_frame = ctk.CTkFrame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = ctk.CTkLabel(name_frame, text="Product Name:")
        name_label.pack(side=tk.LEFT)
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.insert(0, order[1])
        self.name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Category
        category_frame = ctk.CTkFrame(self.extra_window)
        category_frame.pack(pady=5, padx=10, fill=tk.X)
        category_label = ctk.CTkLabel(category_frame, text="Category:")
        category_label.pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(category_frame, textvariable=self.category_var,
                                          values=["Electronics", "Appliances", "Personal Care", "Homeware",
                                                  "Furniture"])
        self.category_menu.set(order[3])
        self.category_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Quantity
        quantity_frame = ctk.CTkFrame(self.extra_window)
        quantity_frame.pack(pady=5, padx=10, fill=tk.X)
        quantity_label = ctk.CTkLabel(quantity_frame, text="Quantity:")
        quantity_label.pack(side=tk.LEFT)
        self.quantity_entry = ctk.CTkEntry(quantity_frame)
        self.quantity_entry.insert(0, order[4])
        self.quantity_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Vendor ID
        vendor_id_frame = ctk.CTkFrame(self.extra_window)
        vendor_id_frame.pack(pady=5, padx=10, fill=tk.X)
        vendor_id_label = ctk.CTkLabel(vendor_id_frame, text="Vendor ID:")
        vendor_id_label.pack(side=tk.LEFT)
        self.vendor_id_var = tk.StringVar()
        self.vendor_id_menu = ttk.Combobox(vendor_id_frame, textvariable=self.vendor_id_var)
        self.vendor_id_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.load_vendor_ids()
        self.vendor_id_menu.set(order[5])

        save_button = ctk.CTkButton(self.extra_window, text="Save Changes", command=self.save_order_changes)
        save_button.pack(pady=10)

    def save_order_changes(self):
        product_name = self.name_entry.get()
        category = self.category_var.get()
        quantity = self.quantity_entry.get()
        vendor_id = self.vendor_id_var.get()

        if product_name and category and quantity and vendor_id:
            self.cursor.execute(
                'UPDATE Orders SET PRODUCT_NAME=?, CATEGORY=?, QUANTITY=?, VENDOR_ID=? WHERE ORDER_ID=?',
                (product_name, category, quantity, vendor_id, self.edit_order_id)
            )
            self.connector.commit()
            self.load_order_data()
            messagebox.showinfo('Success', 'Order updated successfully!')
            self.extra_window.destroy()
        else:
            messagebox.showwarning('Error', 'Please fill in all fields.')

    def delete_order(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select an order to delete.')
            return

        confirm = messagebox.askyesno('Confirm Delete', 'Are you sure you want to delete the selected order?')
        if not confirm:
            return

        order_id = self.order_tree.item(selected_item)['values'][0]
        self.cursor.execute('DELETE FROM Orders WHERE ORDER_ID=?', (order_id,))
        self.connector.commit()
        self.load_order_data()
        messagebox.showinfo('Success', 'Order deleted successfully!')

    def load_vendor_data(self):
        self.vendor_tree.delete(*self.vendor_tree.get_children())

        self.cursor.execute('SELECT * FROM Vendors')
        rows = self.cursor.fetchall()

        for row in rows:
            self.vendor_tree.insert('', 'end', values=row)

    def clear_order_entries(self):
        self.name_entry.delete(0, tk.END)
        self.category_menu.set('')
        self.quantity_entry.delete(0, tk.END)
        self.vendor_id_menu.set('')

    def complete_order_window(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select an order to complete.')
            return

        order_id = self.order_tree.item(selected_item)['values'][0]
        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Complete Order')
        self.extra_window.geometry('600x600')

        title_label = ctk.CTkLabel(self.extra_window, text="COMPLETE ORDER", font=("Helvetica", 14))
        title_label.pack(pady=20)

        self.cursor.execute('SELECT * FROM Orders WHERE ORDER_ID=?', (order_id,))
        order = self.cursor.fetchone()

        self.complete_order_id = order[0]

        # Date
        date_frame = ctk.CTkFrame(self.extra_window)
        date_frame.pack(pady=5, padx=10, fill=tk.X)
        date_label = ctk.CTkLabel(date_frame, text="Date:")
        date_label.pack(side=tk.LEFT)
        self.date_entry = ctk.CTkEntry(date_frame)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Purchase Price
        purchase_price_frame = ctk.CTkFrame(self.extra_window)
        purchase_price_frame.pack(pady=5, padx=10, fill=tk.X)
        purchase_price_label = ctk.CTkLabel(purchase_price_frame, text="Purchase Price:")
        purchase_price_label.pack(side=tk.LEFT)
        self.purchase_price_entry = ctk.CTkEntry(purchase_price_frame)
        self.purchase_price_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Selling Price
        selling_price_frame = ctk.CTkFrame(self.extra_window)
        selling_price_frame.pack(pady=5, padx=10, fill=tk.X)
        selling_price_label = ctk.CTkLabel(selling_price_frame, text="Selling Price:")
        selling_price_label.pack(side=tk.LEFT)
        self.selling_price_entry = ctk.CTkEntry(selling_price_frame)
        self.selling_price_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        complete_button = ctk.CTkButton(self.extra_window, text="Complete Order", command=self.complete_order)
        complete_button.pack(pady=10)

    def complete_order(self):
        order_id = self.complete_order_id
        date = self.date_entry.get()
        purchase_price = self.purchase_price_entry.get()
        selling_price = self.selling_price_entry.get()

        try:
            purchase_price = float(purchase_price)
            selling_price = float(selling_price)
        except ValueError:
            messagebox.showwarning('Error', 'Please enter valid prices.')
            return

        self.cursor.execute('SELECT * FROM Orders WHERE ORDER_ID=?', (order_id,))
        order = self.cursor.fetchone()

        product_name = order[1]
        product_id = order[2]
        category = order[3]
        quantity = order[4]

        location = 'Receiving Area'
        location_prefix = 'REC'
        internal_reference = f"WH-{location_prefix}-{product_id}"

        self.acre_cursor.execute(
            'INSERT INTO Inventory (date, PRODUCT_NAME, PRODUCT_ID, STOCKS, CATEGORY, PURCHASE_PRICE, SELLING_PRICE, '
            'LOCATION, INTERNAL_REFERENCE)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (date, product_name, product_id, quantity, category, purchase_price, selling_price, location,
             internal_reference)
        )
        self.acre_connector.commit()

        self.cursor.execute('DELETE FROM Orders WHERE ORDER_ID=?', (order_id,))
        self.connector.commit()
        self.load_order_data()
        messagebox.showinfo('Success', 'Order completed and transferred successfully!')
        self.extra_window.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = SalesVendorApp(root, "Admin")
    root.mainloop()
