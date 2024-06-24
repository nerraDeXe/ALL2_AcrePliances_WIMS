import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class PurchaseOrderApp:
    def __init__(self, root, username):
        self.connector3 = sqlite3.connect('purchase_order.db')
        self.cursor3 = self.connector3.cursor()

        self.connector3.execute(
            'CREATE TABLE IF NOT EXISTS Orders (ORDER_ID INTEGER PRIMARY KEY, PRODUCT_NAME VARCHAR(20), '
            'DESCRIPTION VARCHAR(30), QUANTITY INTEGER, STOCK_IN VARCHAR(10))'
        )
        self.connector3.commit()

        self.root = root
        self.username = username
        self.root.title('Purchase Order Management')
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')

        self.create_widgets()
        self.load_data()  # Load data initially

    def create_widgets(self):
        top_frame = tk.Frame(self.root, bg='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = tk.Label(top_frame, text="PURCHASE ORDER", font=("Helvetica", 16), bg='#BF2C37', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        welcome_label = tk.Label(top_frame, text=f"Welcome, {self.username}", font=("Helvetica", 12), bg='#BF2C37', fg='white')
        welcome_label.pack(side=tk.LEFT, padx=20, pady=20)

        left_frame = tk.Frame(self.root, bg='#BF2C37')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)

        self.button1 = tk.Button(left_frame, text="ADD PURCHASE ORDER", padx=30, pady=10, command=self.create_window)
        self.button1.pack(pady=10)

        self.button2 = tk.Button(left_frame, text="EDIT PURCHASE ORDER", padx=30, pady=10, command=self.edit_window)
        self.button2.pack(pady=10)

        self.button3 = tk.Button(left_frame, text="DELETE PURCHASE ORDER", padx=25, pady=10, command=self.delete_order)
        self.button3.pack(pady=10)

        self.back_button = tk.Button(left_frame, text="Back", command=self.root.quit)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        order_details_label = tk.Label(main_frame, text="Purchase Order Details:", font=("Helvetica", 14), bg='white')
        order_details_label.pack(anchor=tk.W, pady=10)

        self.task_tree = ttk.Treeview(main_frame, columns=("ID", "Product Name", "Description", "Quantity", "Stock In"),
                                      show='headings')
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Product Name", text="Product Name")
        self.task_tree.heading("Description", text="Description")
        self.task_tree.heading("Quantity", text="Quantity")
        self.task_tree.heading("Stock In", text="Stock In")
        self.task_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_data(self):
        self.task_tree.delete(*self.task_tree.get_children())  # Clear existing items

        self.cursor3.execute('SELECT * FROM Orders')
        rows = self.cursor3.fetchall()

        for row in rows:
            self.task_tree.insert('', 'end', values=row)

    def create_window(self):
        self.extra_window = tk.Toplevel(self.root)
        self.extra_window.title('Add Purchase Order')
        self.extra_window.geometry('600x600')

        title_label = tk.Label(self.extra_window, text="ADD NEW PURCHASE ORDER", font=("Helvetica", 14))
        title_label.pack(pady=20)

        # Order Name
        name_frame = tk.Frame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = tk.Label(name_frame, text="Product Name:")
        name_label.pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame)
        self.name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Order Description
        description_frame = tk.Frame(self.extra_window)
        description_frame.pack(pady=5, padx=10, fill=tk.X)
        description_label = tk.Label(description_frame, text="Description:")
        description_label.pack(side=tk.LEFT)
        self.description_entry = tk.Entry(description_frame)
        self.description_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Quantity
        quantity_frame = tk.Frame(self.extra_window)
        quantity_frame.pack(pady=5, padx=10, fill=tk.X)
        quantity_label = tk.Label(quantity_frame, text="Quantity:")
        quantity_label.pack(side=tk.LEFT)
        self.quantity_entry = tk.Entry(quantity_frame)
        self.quantity_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Stock In
        stock_in_frame = tk.Frame(self.extra_window)
        stock_in_frame.pack(pady=5, padx=10, fill=tk.X)
        stock_in_label = tk.Label(stock_in_frame, text="Stock In:")
        stock_in_label.pack(side=tk.LEFT)
        self.stock_in_entry = tk.Entry(stock_in_frame)
        self.stock_in_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        add_button = tk.Button(self.extra_window, text="Add Order", command=self.add_order)
        add_button.pack(pady=10)

        clear_button = tk.Button(self.extra_window, text="Clear", command=self.clear_entries)
        clear_button.pack(pady=10)


    def add_order(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        quantity = self.quantity_entry.get()
        stock_in = self.stock_in_entry.get()

        if name and description and quantity and stock_in:
            self.cursor3.execute(
                'INSERT INTO Orders (PRODUCT_NAME, DESCRIPTION, QUANTITY, STOCK_IN) VALUES (?, ?, ?, ?)',
                (name, description, quantity, stock_in)
            )
            self.connector3.commit()

            self.load_data()  # Reload data into TreeView
            self.clear_entries()
        else:
            messagebox.showwarning("Input Error", "All fields are required")

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.stock_in_entry.delete(0, tk.END)

    def edit_window(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No order selected")
            return

        item = self.task_tree.item(selected_item)
        values = item['values']

        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title('Edit Purchase Order')
        self.edit_window.geometry('600x600')

        title_label = tk.Label(self.edit_window, text="EDIT PURCHASE ORDER", font=("Helvetica", 14))
        title_label.pack(pady=20)

        # Order Name
        name_frame = tk.Frame(self.edit_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = tk.Label(name_frame, text="Product Name:")
        name_label.pack(side=tk.LEFT)
        self.name_edit_entry = tk.Entry(name_frame)
        self.name_edit_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.name_edit_entry.insert(0, values[1])

        # Order Description
        description_frame = tk.Frame(self.edit_window)
        description_frame.pack(pady=5, padx=10, fill=tk.X)
        description_label = tk.Label(description_frame, text="Description:")
        description_label.pack(side=tk.LEFT)
        self.description_edit_entry = tk.Entry(description_frame)
        self.description_edit_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.description_edit_entry.insert(0, values[2])

        # Quantity
        quantity_frame = tk.Frame(self.edit_window)
        quantity_frame.pack(pady=5, padx=10, fill=tk.X)
        quantity_label = tk.Label(quantity_frame, text="Quantity:")
        quantity_label.pack(side=tk.LEFT)
        self.quantity_edit_entry = tk.Entry(quantity_frame)
        self.quantity_edit_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.quantity_edit_entry.insert(0, values[3])

        # Stock In Date
        stock_in_frame = tk.Frame(self.edit_window)
        stock_in_frame.pack(pady=5, padx=10, fill=tk.X)
        stock_in_label = tk.Label(stock_in_frame, text="Stock In:")
        stock_in_label.pack(side=tk.LEFT)
        self.stock_in_edit_entry = tk.Entry(stock_in_frame)
        self.stock_in_edit_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.stock_in_edit_entry.insert(0, values[4])

        save_button = tk.Button(self.edit_window, text="Save Changes", command=lambda: self.save_edit(selected_item))
        save_button.pack(pady=10)

        clear_button = tk.Button(self.edit_window, text="Clear", command=self.clear_edit_entries)
        clear_button.pack(pady=10)


    def save_edit(self, selected_item):
        name = self.name_edit_entry.get()
        description = self.description_edit_entry.get()
        quantity = self.quantity_edit_entry.get()
        stock_in = self.stock_in_edit_entry.get()

        if name and description and quantity and stock_in:
            order_id = self.task_tree.item(selected_item)['values'][0]
            self.cursor3.execute(
                'UPDATE Orders SET PRODUCT_NAME = ?, DESCRIPTION = ?, QUANTITY = ?, STOCK_IN = ? WHERE ORDER_ID = ?',
                (name, description, quantity, stock_in, order_id)
            )
            self.connector3.commit()

            self.task_tree.item(selected_item, values=(order_id, name, description, quantity, stock_in))
            self.edit_window.destroy()
        else:
            messagebox.showwarning("Input Error", "All fields are required")

    def clear_edit_entries(self):
        self.name_edit_entry.delete(0, tk.END)
        self.description_edit_entry.delete(0, tk.END)
        self.quantity_edit_entry.delete(0, tk.END)
        self.stock_in_edit_entry.delete(0, tk.END)

    def delete_order(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No order selected")
            return

        order_id = self.task_tree.item(selected_item)['values'][0]
        self.cursor3.execute('DELETE FROM Orders WHERE ORDER_ID = ?', (order_id,))
        self.connector3.commit()

        self.task_tree.delete(selected_item)  # Remove from TreeView

if __name__ == '__main__':
    username = "Admin"
    root = tk.Tk()
    app = PurchaseOrderApp(root, username)
    root.mainloop()
