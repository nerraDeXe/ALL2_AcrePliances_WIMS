import platform
import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date,timezone
from PIL import Image, ImageTk
import pytz
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os


class PurchaseApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect('AcrePliances.db')
        self.cursor = self.connector.cursor()

        self.connector.execute(
            'CREATE TABLE IF NOT EXISTS Purchase_Orders ('
            'PURCHASE_ORDER_ID INTEGER PRIMARY KEY AUTOINCREMENT, '
            'PRODUCT_NAME VARCHAR(20), '
            'CATEGORY TEXT, '
            'QUANTITY INTEGER, '
            'VENDOR_ID INTEGER, '
            'DATETIME DATETIME, '
            'FOREIGN KEY(VENDOR_ID) REFERENCES Vendors(VENDOR_ID))'
        )

        self.connector.commit()

        self.acre_connector = sqlite3.connect('AcrePliances.db')
        self.acre_cursor = self.acre_connector.cursor()

        self.acre_connector.commit()

        self.root = root
        self.username = username
        self.root.title('Purchase Order Management')
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')
        self.root.resizable(0, 0)

        self.create_widgets()
        self.load_order_data()
        self.load_vendors_data()
        self.is_filter_active = False
        self.is_filter_active1 = False
        self.detached_items = []
        self.detached_items1 = []

    def create_widgets(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="PURCHASE ORDER MANAGEMENT", font=("Helvetica", 16),
                                   text_color='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        # Add notification button
        self.notification_image = ImageTk.PhotoImage(Image.open("nored.png"))

        # Create the image button
        self.notification_button = tk.Button(top_frame, image=self.notification_image, bg='white',
                                             activebackground='darkred', command=self.show_notifications_window)
        self.notification_button.pack(side=tk.RIGHT, padx=20, pady=20)

        left_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=20)

        self.add_purchase_order_button = ctk.CTkButton(left_frame, text="ADD PURCHASE ORDER", fg_color='#FFFFFF',
                                                       text_color='#000000',
                                                       command=self.create_purchase_order_window)
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

        self.open_purchase_order_folder_button = ctk.CTkButton(left_frame, text="OPEN COMPLETED ORDER REPORTS", fg_color='#FFFFFF',
                                                   text_color='#000000', command=self.open_purchase_order_folder)
        self.open_purchase_order_folder_button.pack(pady=10)


        self.back_button = ctk.CTkButton(left_frame, text="Back", command=self.close_subpanel)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = ctk.CTkFrame(self.root, fg_color='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=20)

        self.order_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.order_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.vendor_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.vendor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        order_details_label = ctk.CTkLabel(self.order_frame, text="Purchase Order Details:",
                                           font=("Helvetica", 20, 'bold'),
                                           text_color='black')
        order_details_label.pack(anchor=tk.W, pady=10)

        self.order_tree = ttk.Treeview(self.order_frame, columns=(
            "ID", "Product Name", "Category", "Quantity", "Vendor ID", "Date"), show='headings')
        self.order_tree.heading("ID", text="ID")
        self.order_tree.heading("Product Name", text="Product Name")
        self.order_tree.heading("Category", text="Category")
        self.order_tree.heading("Quantity", text="Quantity")
        self.order_tree.heading("Vendor ID", text="Vendor ID")
        self.order_tree.heading("Date", text="Date")

        self.order_tree.column("ID", width=100, stretch=tk.NO)
        self.order_tree.column("Product Name", width=300, stretch=tk.NO)
        self.order_tree.column("Category", width=150, stretch=tk.NO)
        self.order_tree.column("Quantity", width=100, stretch=tk.NO)
        self.order_tree.column("Vendor ID", width=100, stretch=tk.NO)
        self.order_tree.column("Date", width=298, stretch=tk.NO)

        self.order_tree.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        self.header_menu = tk.Menu(self.root, tearoff=0)
        self.header_menu.add_command(label="Filter", command=self.filter_by_column)

        self.order_tree.bind("<Button-3>", self.show_header_menu)

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

        self.header_menu1 = tk.Menu(self.root, tearoff=0)
        self.header_menu1.add_command(label="Filter", command=self.filter_by_column1)

        self.vendor_tree.bind("<Button-3>", self.show_header_menu1)

    def show_header_menu(self, event):
        if not self.is_filter_active:  # Check if filtering is active
            # Find the column heading that was clicked
            region = self.order_tree.identify("region", event.x, event.y)
            if region == "heading":
                col = self.order_tree.identify_column(event.x)
                self.selected_column = self.order_tree.heading(col)["text"]
                self.update_header_menu(col)
                self.header_menu.post(event.x_root, event.y_root)
        else:
            # Only show the "Show All" option
            self.header_menu.delete(0, tk.END)
            self.header_menu.add_command(label="Show All", command=self.show_all)
            self.header_menu.post(event.x_root, event.y_root)

    def show_header_menu1(self, event):
        if not self.is_filter_active1:  # Check if filtering is active
            # Find the column heading that was clicked
            region = self.vendor_tree.identify("region", event.x, event.y)
            if region == "heading":
                col = self.vendor_tree.identify_column(event.x)
                self.selected_column1 = self.vendor_tree.heading(col)["text"]
                self.update_header_menu1(col)
                self.header_menu1.post(event.x_root, event.y_root)
        else:
            # Only show the "Show All" option
            self.header_menu1.delete(0, tk.END)
            self.header_menu1.add_command(label="Show All", command=self.show_all1)
            self.header_menu1.post(event.x_root, event.y_root)

    def update_header_menu(self, col):
        # Clear previous menu items
        self.header_menu.delete(0, tk.END)

        if not self.is_filter_active:
            # Add submenu for unique items
            unique_items_menu = tk.Menu(self.header_menu, tearoff=0)
            unique_items = self.get_unique_items(col)

            for item in unique_items:
                unique_items_menu.add_command(label=item, command=lambda value=item: self.filter_by_column(value))

            self.header_menu.add_cascade(label="Filter by", menu=unique_items_menu)

        # Add "Show All" option
        self.header_menu.add_command(label="Show All", command=self.show_all)

    def update_header_menu1(self, col):
        # Clear previous menu items
        self.header_menu1.delete(0, tk.END)

        if not self.is_filter_active1:
            # Add submenu for unique items
            unique_items_menu1 = tk.Menu(self.header_menu1, tearoff=0)
            unique_items1 = self.get_unique_items1(col)

            for item in unique_items1:
                unique_items_menu1.add_command(label=item, command=lambda value=item: self.filter_by_column1(value))

            self.header_menu1.add_cascade(label="Filter by", menu=unique_items_menu1)

        # Add "Show All" option
        self.header_menu1.add_command(label="Show All", command=self.show_all)

    def get_unique_items(self, col):
        # Get unique items in the specified column
        col_index = int(col.replace('#', '')) - 1
        items = set()

        for child in self.order_tree.get_children():
            item = self.order_tree.item(child, 'values')[col_index]
            items.add(item)

        return sorted(items)

    def get_unique_items1(self, col):
        # Get unique items in the specified column
        col_index = int(col.replace('#', '')) - 1
        items1 = set()

        for child in self.vendor_tree.get_children():
            item1 = self.vendor_tree.item(child, 'values')[col_index]
            items1.add(item1)

        return sorted(items1)

    def filter_by_column(self, filter_value):
        col_index = self.get_column_index(self.order_tree, self.selected_column)
        if col_index is None:
            return

        self.detached_items = []  # Clear the detached items list

        for item in self.order_tree.get_children():
            values = self.order_tree.item(item, 'values')
            if values[col_index] != filter_value:
                self.detached_items.append(item)
                self.order_tree.detach(item)

        self.is_filter_active = True  # Set filtering active

    def filter_by_column1(self, filter_value1):
        col_index = self.get_column_index1(self.vendor_tree, self.selected_column1)
        if col_index is None:
            return

        self.detached_items1 = []  # Clear the detached items list

        for item in self.vendor_tree.get_children():
            values = self.vendor_tree.item(item, 'values')
            if values[col_index] != filter_value1:
                self.detached_items1.append(item)
                self.vendor_tree.detach(item)

        self.is_filter_active1 = True  # Set filtering active

    def get_column_index(self, tree, column_name):
        columns = [tree.heading(col)["text"] for col in tree["columns"]]
        try:
            return columns.index(column_name)
        except ValueError:
            print(f"Error: Column '{column_name}' not found in {columns}")
            return None

    def get_column_index1(self, tree, column_name1):
        columns1 = [tree.heading(col)["text"] for col in tree["columns"]]
        try:
            return columns1.index(column_name1)
        except ValueError:
            print(f"Error: Column '{column_name1}' not found in {columns1}")
            return None

    def show_all(self):
        for item in self.detached_items:
            self.order_tree.reattach(item, '', 'end')
        self.detached_items = []  # Clear the detached items list
        self.is_filter_active = False  # Set filtering inactive

    def show_all1(self):
        for item in self.detached_items1:
            self.vendor_tree.reattach(item, '', 'end')
        self.detached_items1 = []  # Clear the detached items list
        self.is_filter_active1 = False  # Set filtering inactive

    def close_subpanel(self):
        self.root.destroy()

    def load_order_data(self):
        self.order_tree.delete(*self.order_tree.get_children())

        self.cursor.execute('SELECT * FROM Purchase_Orders')
        rows = self.cursor.fetchall()

        for row in rows:
            self.order_tree.insert('', 'end', values=row)

    def create_purchase_order_window(self):
        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Add Purchase Order')
        # self.extra_window.geometry('600x350')
        self.extra_window.resizable(False, False)
        self.extra_window.attributes('-topmost', True)

        ctk.CTkLabel(self.extra_window, text="Add Purchase Order", font=('Helvetica', 16, 'bold'),
                     text_color='red').grid(row=0, columnspan=2, padx=10, pady=5)

        labels = ["Product Name:", "Category:", "Quantity:", "Vendor ID:"]
        for i, text in enumerate(labels):
            ctk.CTkLabel(self.extra_window, text=text, font=('Gill Sans MT', 13)).grid(row=i + 1, column=0, padx=10,
                                                                                       pady=10)

        self.name_entry = ctk.CTkEntry(self.extra_window, font=('Gill Sans MT', 13), width=200)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)

        self.category_var = tk.StringVar()
        self.category_menu = ctk.CTkComboBox(self.extra_window, variable=self.category_var,
                                             values=["Electronics", "Appliances", "Personal Care", "Homeware",
                                                     "Furniture"])
        self.category_menu.grid(row=2, column=1, padx=10, pady=10)

        self.quantity_entry = ctk.CTkEntry(self.extra_window, font=('Gill Sans MT', 13), width=200)
        self.quantity_entry.grid(row=3, column=1, padx=10, pady=10)

        self.vendor_id_var = tk.StringVar()
        self.vendor_id_menu = ttk.Combobox(self.extra_window, textvariable=self.vendor_id_var,
                                           values=self.get_vendor_ids())
        self.vendor_id_menu.grid(row=4, column=1, padx=10, pady=10)

        ctk.CTkButton(self.extra_window, text='Add Order', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                      command=self.add_purchase_order).grid(row=5, column=0, padx=10, pady=10)
        ctk.CTkButton(self.extra_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                      command=self.extra_window.destroy).grid(row=5, column=1, padx=10, pady=10)

    def add_purchase_order(self):
        try:
            product_name = self.name_entry.get()
            category = self.category_var.get()
            quantity = int(self.quantity_entry.get())
            vendor_id = int(self.vendor_id_var.get())
            dt = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

            if not all([product_name, category, quantity, vendor_id]):
                messagebox.showerror("Error", "Please fill all fields")
                return

            self.cursor.execute(
                'INSERT INTO Purchase_Orders (PRODUCT_NAME, CATEGORY, QUANTITY, VENDOR_ID, DATETIME) VALUES (?, ?, ?, ?, ?)',
                (product_name, category, quantity, vendor_id, dt)
            )
            self.connector.commit()
            self.extra_window.destroy()
            self.load_order_data()
            self.add_notification(f"ADDED PRODUCT NAME: {product_name} TO PURCHASE ORDER")

            messagebox.showinfo("Success", "Purchase Order added successfully!")

        except Exception as e:
            messagebox.showerror("Error", "Inappropriate values.")


    def get_vendor_ids(self):
        self.cursor.execute('SELECT VENDOR_ID FROM Vendors')
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def load_vendors_data(self):
        self.vendor_tree.delete(*self.vendor_tree.get_children())

        self.cursor.execute('SELECT * FROM Vendors')
        rows = self.cursor.fetchall()

        for row in rows:
            self.vendor_tree.insert('', 'end', values=row)

    def edit_order_window(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to edit.")
            return

        order = self.order_tree.item(selected_item, 'values')
        self.selected_order_id = order[0]

        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Edit Purchase Order')
        # self.extra_window.geometry('600x350')
        self.extra_window.resizable(False, False)
        self.extra_window.attributes('-topmost', True)

        ctk.CTkLabel(self.extra_window, text="Edit Purchase Order", font=('Helvetica', 16, 'bold'),
                     text_color='red').grid(row=0, columnspan=2, padx=10, pady=5)

        labels = ["Product Name:", "Category:", "Quantity:", "Vendor ID:"]
        for i, text in enumerate(labels):
            ctk.CTkLabel(self.extra_window, text=text, font=('Gill Sans MT', 13)).grid(row=i + 1, column=0, padx=10,
                                                                                       pady=10)

        self.name_entry = ctk.CTkEntry(self.extra_window, font=('Gill Sans MT', 13), width=200)
        self.name_entry.insert(0, order[1])
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)

        self.category_var = tk.StringVar(value=order[2])
        self.category_menu = ctk.CTkComboBox(self.extra_window, variable=self.category_var,
                                             values=["Electronics", "Appliances", "Personal Care", "Homeware",
                                                     "Furniture"])
        self.category_menu.grid(row=2, column=1, padx=10, pady=10)

        self.quantity_entry = ctk.CTkEntry(self.extra_window, font=('Gill Sans MT', 13), width=200)
        self.quantity_entry.insert(0, order[3])
        self.quantity_entry.grid(row=3, column=1, padx=10, pady=10)

        self.vendor_id_var = tk.StringVar(value=order[4])
        self.vendor_id_menu = ttk.Combobox(self.extra_window, textvariable=self.vendor_id_var,
                                           values=self.get_vendor_ids())
        self.vendor_id_menu.grid(row=4, column=1, padx=10, pady=10)

        ctk.CTkButton(self.extra_window, text='Save Changes', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                      command=self.edit_order).grid(row=5, column=0, padx=10, pady=10)
        ctk.CTkButton(self.extra_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                      command=self.extra_window.destroy).grid(row=5, column=1, padx=10, pady=10)

    def edit_order(self):
        try:
            product_name = self.name_entry.get()
            category = self.category_var.get()
            quantity = int(self.quantity_entry.get())
            vendor_id = int(self.vendor_id_var.get())
            dt = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

            if not all([product_name, category, quantity, vendor_id]):
                messagebox.showerror("Error", "Please fill all fields")
                return

            self.cursor.execute(
                'UPDATE Purchase_Orders SET PRODUCT_NAME = ?, CATEGORY = ?, QUANTITY = ?, VENDOR_ID = ?, DATETIME = ? '
                'WHERE PURCHASE_ORDER_ID = ?',
                (product_name, category, quantity, vendor_id, dt, self.selected_order_id)
            )
            self.connector.commit()
            self.extra_window.destroy()
            self.load_order_data()

            messagebox.showinfo("Success", "Purchase Order updated successfully!")

        except Exception as e:
            messagebox.showerror("Error", "Inappropriate values.")


    def delete_order(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to delete.")
            return

        purchase_order_id = self.order_tree.item(selected_item)['values'][0]

        # Ask for confirmation
        confirm = messagebox.askokcancel("Confirm Deletion",
                                         f"Are you sure you want to delete order ID {purchase_order_id}?")

        if confirm:
            self.cursor.execute('DELETE FROM Purchase_Orders WHERE PURCHASE_ORDER_ID = ?', (purchase_order_id,))
            self.connector.commit()

            self.load_order_data()

    def complete_order_window(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to complete.")
            return

        order = self.order_tree.item(selected_item, 'values')
        self.complete_window = ctk.CTkToplevel(self.root)
        self.complete_window.title('Complete Order')
        # self.complete_window.geometry('600x350')
        self.complete_window.resizable(False, False)
        self.complete_window.attributes('-topmost', True)

        ctk.CTkLabel(self.complete_window, text="Complete Order", font=('Helvetica', 16, 'bold'),
                     text_color='red').grid(row=0, columnspan=2, padx=10, pady=5)

        labels = ["Product Name:", "Category:", "Quantity:", "Purchase Price:", "Selling Price:"]
        for i, text in enumerate(labels):
            ctk.CTkLabel(self.complete_window, text=text, font=('Gill Sans MT', 13)).grid(row=i + 1, column=0, padx=10,
                                                                                          pady=10)

        self.name_entry = ctk.CTkEntry(self.complete_window, font=('Gill Sans MT', 13), width=200)
        self.name_entry.insert(0, order[1])
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)
        self.name_entry.configure(state="disabled")

        self.category_var = tk.StringVar(value=order[2])
        self.category_menu = ctk.CTkComboBox(self.complete_window, variable=self.category_var,
                                             values=["Electronics", "Appliances", "Personal Care", "Homeware",
                                                     "Furniture"])
        self.category_menu.grid(row=2, column=1, padx=10, pady=10)
        self.category_menu.configure(state="disabled")

        self.quantity_entry = ctk.CTkEntry(self.complete_window, font=('Gill Sans MT', 13), width=200)
        self.quantity_entry.insert(0, order[3])
        self.quantity_entry.grid(row=3, column=1, padx=10, pady=10)
        self.quantity_entry.configure(state="disabled")

        self.purchase_price_entry = ctk.CTkEntry(self.complete_window, font=('Gill Sans MT', 13), width=200)
        self.purchase_price_entry.grid(row=4, column=1, padx=10, pady=10)

        self.selling_price_entry = ctk.CTkEntry(self.complete_window, font=('Gill Sans MT', 13), width=200)
        self.selling_price_entry.grid(row=5, column=1, padx=10, pady=10)

        ctk.CTkButton(self.complete_window, text='Complete Order', font=('Helvetica', 13, 'bold'),
                      fg_color='SpringGreen4', command=lambda: self.complete_order(order)).grid(row=6, column=0,
                                                                                                padx=10, pady=10)
        ctk.CTkButton(self.complete_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                      command=self.complete_window.destroy).grid(row=6, column=1, padx=10, pady=10)

    def complete_order(self, order):
        try:
            name = self.name_entry.get()
            category = self.category_var.get()
            quantity = self.quantity_entry.get()
            purchase_price = float(self.purchase_price_entry.get())
            selling_price = float(self.selling_price_entry.get())
            product_id = self.generate_product_id(category)
            location = 'Staging Area'
            location_prefix = 'STA'
            internal_reference = f"WH-{location_prefix}-{product_id}"
            current_date = date.today().strftime("%Y-%m-%d")

            # Insert data into the Inventory table
            self.acre_cursor.execute('''
                INSERT INTO Inventory (date, PRODUCT_NAME, PRODUCT_ID, CATEGORY, STOCKS, PURCHASE_PRICE, SELLING_PRICE, 
                LOCATION, INTERNAL_REFERENCE)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (current_date, name, product_id, category, quantity, purchase_price, selling_price, location,
                  internal_reference))
            self.acre_connector.commit()

            # Delete the completed order from Purchase_Orders table
            self.cursor.execute('DELETE FROM Purchase_Orders WHERE PURCHASE_ORDER_ID = ?', (order[0],))
            self.connector.commit()

            # Refresh the order data and close the window
            self.load_order_data()
            self.complete_window.destroy()

            # Add a notification about the completed order
            self.add_notification(f"Completed order for {name}")

            # Show a message box to inform the user
            messagebox.showinfo("Order Completed", f"The order for {name} has been successfully completed.")

            # Generate PDF report
            self.generate_pdf_report(order[0], name, category, quantity, purchase_price, selling_price, current_date)

        except Exception as e:
            messagebox.showerror("Error", "Inappropriate values.")


    def generate_pdf_report(self, order_id, name, category, quantity, purchase_price, selling_price, date):
        # Create the 'receipts' directory if it doesn't exist
        if not os.path.exists('Purchase Orders'):
            os.makedirs('Purchase Orders')

        report_name = f"Purchase Orders/Purchase_Order_{order_id}_Receipt.pdf"
        document = SimpleDocTemplate(report_name, pagesize=letter)
        width, height = letter

        elements = []

        # Company Information
        company_info = """
        <b>ACRE Corporation</b><br/>
        123 Jalan Damai<br/>
        George Town, Penang 10100<br/>
        Phone: (04) 456-7890<br/>
        Email: Acre1@acrecorp.com<br/>
        """
        elements.append(Paragraph(company_info, getSampleStyleSheet()["Normal"]))
        elements.append(Spacer(1, 24))

        # Title
        title_style = ParagraphStyle(name='Title', fontSize=18, alignment=1, spaceAfter=14)
        title = Paragraph("Purchase Order Receipt", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Line separator
        elements.append(Paragraph('<hr width="100%" color="black"/>', getSampleStyleSheet()["Normal"]))
        elements.append(Spacer(1, 12))

        # Table Data
        data = [
            ["Order ID", f"{order_id}"],
            ["Product Name", f"{name}"],
            ["Category", f"{category}"],
            ["Quantity", f"{quantity}"],
            ["Purchase Price", f"RM{purchase_price:.2f}"],
            ["Selling Price", f"RM{selling_price:.2f}"],
            ["Date", f"{date}"],
            ["Total Purchase Price", f"RM{purchase_price * float(quantity):.2f}"],
        ]

        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))

        # Line separator
        elements.append(Paragraph('<hr width="100%" color="black"/>', getSampleStyleSheet()["Normal"]))
        elements.append(Spacer(1, 12))

        # Thank You Note
        thank_you_note = """
        <b>Thank you for your order!</b><br/>
        We appreciate your business and hope to serve you again soon. If you have any questions about your order, 
        please contact us at (04) 456-7890 or info@acrecorp.com.
        """
        elements.append(Paragraph(thank_you_note, getSampleStyleSheet()["Normal"]))
        elements.append(Spacer(1, 24))

        # Premade Description
        description = """
        This receipt confirms the purchase of the listed items from ACRE Corporation. The products 
        listed above have been received in good condition and are as described in the purchase order. Any discrepancies 
        should be reported within 7 days of receipt. Thank you for your business.
        """
        elements.append(Paragraph(description, getSampleStyleSheet()["Normal"]))
        elements.append(Spacer(1, 24))

        # Build the document
        document.build(elements)

        messagebox.showinfo("Receipt Generated",
                            f"The receipt for order {order_id} has been generated and saved as {report_name}.")

    def open_purchase_order_folder(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Define the path to the "Purchase Order" folder
        purchase_order_path = os.path.join(script_dir, 'Purchase Orders')

        # Check the operating system and open the folder accordingly
        if platform.system() == 'Windows':
            os.startfile(purchase_order_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', purchase_order_path])
        else:  # Linux
            subprocess.Popen(['xdg-open', purchase_order_path])

    def generate_product_id(self, category):
        # Check if the category already exists in the counter table
        self.cursor.execute('SELECT LAST_PRODUCT_ID FROM Product_Counter WHERE CATEGORY=?', (category,))
        result = self.cursor.fetchone()

        if result:
            # Increment the existing counter
            last_id = result[0]
            new_id = last_id + 1
            self.cursor.execute('UPDATE Product_Counter SET LAST_PRODUCT_ID=? WHERE CATEGORY=?', (new_id, category))
        else:
            # Initialize the counter for the new category
            new_id = 1
            self.cursor.execute('INSERT INTO Product_Counter (CATEGORY, LAST_PRODUCT_ID) VALUES (?, ?)',
                                (category, new_id))

        self.connector.commit()

        # Generate the product ID
        product_id = f"{category[0].upper()}{new_id:03d}"
        return product_id

    ############################################ NOTIFICATION FUNCTIONS#################################################
    def add_notification(self, description):
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION, TIMESTAMP) VALUES (?, ?)',
                            (description, timestamp))
        self.connector.commit()

    def show_notifications_window(self):
        subprocess.Popen(["python", "Notifications.py"])


if __name__ == '__main__':
    root = ctk.CTk()
    app = PurchaseApp(root, username="Admin")  # Pass the username here
    root.mainloop()
