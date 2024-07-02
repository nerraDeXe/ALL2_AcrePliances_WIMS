import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
from PIL import Image, ImageTk
import pytz


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

    def create_widgets(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="PURCHASE ORDER MANAGEMENT", font=("Helvetica", 16),
                                   text_color='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        welcome_label = ctk.CTkLabel(top_frame, text=f"Welcome, {self.username}", font=("Helvetica", 12),
                                     text_color='white')
        welcome_label.pack(side=tk.LEFT, padx=20, pady=20)

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
        self.extra_window.geometry('600x600')
        title_label = ctk.CTkLabel(self.extra_window, text="ADD NEW PURCHASE ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)
        self.extra_window.attributes('-topmost', True)

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
        self.vendor_id_menu = ttk.Combobox(vendor_id_frame, textvariable=self.vendor_id_var,
                                           values=self.get_vendor_ids())
        self.vendor_id_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Add Button
        add_button = ctk.CTkButton(self.extra_window, text="Add Order", command=self.add_purchase_order)
        add_button.pack(pady=20)

    def add_purchase_order(self):
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
        self.selected_order_id = order[0]  # Store the selected order ID

        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Edit Purchase Order')
        self.extra_window.geometry('600x600')
        title_label = ctk.CTkLabel(self.extra_window, text="EDIT PURCHASE ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)
        self.extra_window.attributes('-topmost', True)

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
        self.category_var = tk.StringVar(value=order[2])
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
        self.quantity_entry.insert(0, order[3])
        self.quantity_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Vendor ID
        vendor_id_frame = ctk.CTkFrame(self.extra_window)
        vendor_id_frame.pack(pady=5, padx=10, fill=tk.X)
        vendor_id_label = ctk.CTkLabel(vendor_id_frame, text="Vendor ID:")
        vendor_id_label.pack(side=tk.LEFT)
        self.vendor_id_var = tk.StringVar(value=order[4])
        self.vendor_id_menu = ttk.Combobox(vendor_id_frame, textvariable=self.vendor_id_var,
                                           values=self.get_vendor_ids())
        self.vendor_id_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Save Button
        save_button = ctk.CTkButton(self.extra_window, text="Save Changes", command=self.edit_order)
        save_button.pack(pady=20)

    def edit_order(self):
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
        self.add_notification(f"EDITED PRODUCT NAME: {product_name} FROM PURCHASE ORDER")

        messagebox.showinfo("Success", "Purchase Order updated successfully!")

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
            self.add_notification(f"DELETED ORDER ID: {purchase_order_id} FROM PURCHASE ORDER")

    def complete_order_window(self):
        selected_item = self.order_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an order to complete.")
            return

        order = self.order_tree.item(selected_item, 'values')
        self.complete_window = ctk.CTkToplevel(self.root)
        self.complete_window.title('Complete Order')
        self.complete_window.geometry('600x600')
        title_label = ctk.CTkLabel(self.complete_window, text="COMPLETE ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)
        self.complete_window.attributes('-topmost', True)

        # Add form fields for Inventory
        # Product Name
        name_frame = ctk.CTkFrame(self.complete_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = ctk.CTkLabel(name_frame, text="Product Name:")
        name_label.pack(side=tk.LEFT)
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.insert(0, order[1])
        self.name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Category
        category_frame = ctk.CTkFrame(self.complete_window)
        category_frame.pack(pady=5, padx=10, fill=tk.X)
        category_label = ctk.CTkLabel(category_frame, text="Category:")
        category_label.pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value=order[2])  # Correct index for category
        self.category_menu = ttk.Combobox(category_frame, textvariable=self.category_var,
                                          values=["Electronics", "Appliances", "Personal Care", "Homeware",
                                                  "Furniture"])
        self.category_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Ordered Quantity
        quantity_frame = ctk.CTkFrame(self.complete_window)
        quantity_frame.pack(pady=5, padx=10, fill=tk.X)
        quantity_label = ctk.CTkLabel(quantity_frame, text="Quantity:")
        quantity_label.pack(side=tk.LEFT)
        self.quantity_entry = ctk.CTkEntry(quantity_frame)
        self.quantity_entry.insert(0, order[3])  # Correct index for quantity
        self.quantity_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Purchase Price
        purchase_price_frame = ctk.CTkFrame(self.complete_window)
        purchase_price_frame.pack(pady=5, padx=10, fill=tk.X)
        purchase_price_label = ctk.CTkLabel(purchase_price_frame, text="Purchase Price:")
        purchase_price_label.pack(side=tk.LEFT)
        self.purchase_price_entry = ctk.CTkEntry(purchase_price_frame)
        self.purchase_price_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Selling Price
        selling_price_frame = ctk.CTkFrame(self.complete_window)
        selling_price_frame.pack(pady=5, padx=10, fill=tk.X)
        selling_price_label = ctk.CTkLabel(selling_price_frame, text="Selling Price:")
        selling_price_label.pack(side=tk.LEFT)
        self.selling_price_entry = ctk.CTkEntry(selling_price_frame)
        self.selling_price_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Complete Button
        complete_button = ctk.CTkButton(self.complete_window, text="Complete Order",
                                        command=lambda: self.complete_order(order))
        complete_button.pack(pady=20)

    def complete_order(self, order):
        name = self.name_entry.get()
        category = self.category_var.get()
        quantity = self.quantity_entry.get()
        purchase_price = self.purchase_price_entry.get()
        selling_price = self.selling_price_entry.get()
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

    def generate_product_id(self, category):
        self.cursor.execute('SELECT COUNT(*) FROM Orders WHERE CATEGORY=?', (category,))
        count = self.cursor.fetchone()[0]
        product_id = f"{category[0].upper()}{count + 1:03d}"
        return product_id

    ############################################ NOTIFICATION FUNCTIONS#################################################
    def add_notification(self, description):
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION) VALUES (?)', (description,))
        self.connector.commit()

    def show_notifications_window(self):
        notification_window = ctk.CTkToplevel(self.root)
        notification_window.title('Notifications')
        notification_window.geometry('500x400')
        notification_window.resizable(0, 0)

        # Set the notification window to be on top of the main root window
        notification_window.attributes('-topmost', 'true')

        notification_label = ctk.CTkLabel(notification_window, text="Notifications", font=("Helvetica", 14))
        notification_label.pack(pady=20)

        self.NOTIFICATION_LIST = tk.Listbox(notification_window)
        self.NOTIFICATION_LIST.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.load_notifications()

        delete_button = ctk.CTkButton(notification_window, text="Delete Selected",
                                      command=self.delete_selected_notification)
        delete_button.pack(pady=10)

    def delete_selected_notification(self):
        # Get selected indices from the notification list
        selected_indices = self.NOTIFICATION_LIST.curselection()

        # Loop through selected indices and delete the corresponding notifications
        for index in selected_indices:
            try:
                # Fetch the notification ID using the index
                notification_id = self.notification_ids[index]
                # Execute the SQL delete command
                self.cursor.execute('DELETE FROM Notifications WHERE NOTIFICATION_ID=?', (notification_id,))
                self.connector.commit()
            except sqlite3.Error as e:
                # Show error message if there is an issue with deletion
                messagebox.showerror('Error', f'Error deleting notification: {str(e)}')
                return

        # Check if any notification is selected
        if not selected_indices:
            messagebox.showwarning('No notification selected!', 'Please select a notification to delete.')
            return

        # Ask for confirmation before deleting the selected notification(s)
        confirm_delete = messagebox.askyesno('Confirm Delete',
                                             'Are you sure you want to delete the selected notification(s)?')
        if not confirm_delete:
            return

        # Reload notifications after deletion
        self.load_notifications()

    def load_notifications(self):
        try:
            self.NOTIFICATION_LIST.delete(0, tk.END)  # Clear the list first
            self.notification_ids = {}  # Dictionary to store index to ID mapping
            self.cursor.execute("SELECT * FROM Notifications")
            notifications = self.cursor.fetchall()

            for idx, notification in enumerate(notifications):
                timestamp = datetime.strptime(notification[2],
                                              '%Y-%m-%d %H:%M:%S')  # Assuming the timestamp is in the third column
                utc_timezone = pytz.utc
                local_timezone = pytz.timezone('Asia/Singapore')  # GMT+8 timezone
                utc_timestamp = utc_timezone.localize(timestamp)
                local_timestamp = utc_timestamp.astimezone(local_timezone)
                formatted_timestamp = local_timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format the timestamp as desired
                message_with_timestamp = f"{formatted_timestamp} - {notification[1]}"
                self.NOTIFICATION_LIST.insert(tk.END, message_with_timestamp)
                self.notification_ids[idx] = notification[0]  # Store the ID with the index as the key
        except sqlite3.Error as e:
            messagebox.showerror('Error', f'Error loading notifications: {str(e)}')


if __name__ == '__main__':
    root = ctk.CTk()
    app = PurchaseApp(root, username="Admin")  # Pass the username here
    root.mainloop()
