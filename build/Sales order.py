import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
from PIL import Image, ImageTk
import pytz


class SalesApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect('AcrePliances.db')
        self.cursor = self.connector.cursor()

        self.connector.execute(
            'CREATE TABLE IF NOT EXISTS Sales_Orders ('
            'ORDER_ID INTEGER PRIMARY KEY, '
            'PRODUCT_NAME VARCHAR(20), '
            'PRODUCT_ID TEXT, '
            'CATEGORY TEXT, '
            'QUANTITY INTEGER, '
            'DATE date,'
            'STORE_BRANCH TEXT)'
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

        self.connector.execute(
            'CREATE TABLE IF NOT EXISTS Notifications ('
            'NOTIFICATION_ID INTEGER PRIMARY KEY AUTOINCREMENT, '
            'DESCRIPTION TEXT, '
            'TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP)'
        )

        self.acre_connector.commit()

        self.root = root
        self.username = username
        self.root.title('Sales Order Management')
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')
        self.root.resizable(0, 0)

        self.create_widgets()
        self.load_sales_order_data()
        self.load_inventory_data()

    def create_widgets(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="SALES ORDER MANAGEMENT", font=("Helvetica", 16),
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

        self.add_sales_order_button = ctk.CTkButton(left_frame, text="ADD SALES ORDER", fg_color='#FFFFFF',
                                                       text_color='#000000',
                                                       command=self.create_sales_order_window)
        self.add_sales_order_button.pack(pady=10)

        # self.edit_sales_order_button = ctk.CTkButton(left_frame, text="EDIT SALES ORDER", fg_color='#FFFFFF',
        #                                                 text_color='#000000', command=self.edit_order_window)
        # self.edit_sales_order_button.pack(pady=10)

        self.delete_sales_order_button = ctk.CTkButton(left_frame, text="DELETE SALES ORDER", fg_color='#FFFFFF',
                                                          text_color='#000000', command=self.delete_order)
        self.delete_sales_order_button.pack(pady=10)

        self.complete_order_button = ctk.CTkButton(left_frame, text="COMPLETE ORDER", fg_color='#FFFFFF',
                                                   text_color='#000000', command=self.complete_order)
        self.complete_order_button.pack(pady=10)

        self.back_button = ctk.CTkButton(left_frame, text="Back", command=self.close_subpanel)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = ctk.CTkFrame(self.root, fg_color='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=20)

        self.order_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.order_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.inventory_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.inventory_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        order_details_label = ctk.CTkLabel(self.order_frame, text="Sales Order Details:",
                                           font=("Helvetica", 20, 'bold'),
                                           text_color='black')
        order_details_label.pack(anchor=tk.W, pady=10)

        self.sales_order_tree = ttk.Treeview(self.order_frame, columns=(
            "ID", "Product Name", "Product ID", "Category", "Quantity", "Date", "Store Branch"), show='headings')
        self.sales_order_tree.heading("ID", text="ID")
        self.sales_order_tree.heading("Product Name", text="Product Name")
        self.sales_order_tree.heading("Product ID", text="Product ID")
        self.sales_order_tree.heading("Category", text="Category")
        self.sales_order_tree.heading("Quantity", text="Quantity")
        self.sales_order_tree.heading("Date", text="Date")
        self.sales_order_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        inventory_details_label = ctk.CTkLabel(self.inventory_frame, text="Inventory:", font=("Helvetica", 20, 'bold'),
                                            text_color='black')
        inventory_details_label.pack(anchor=tk.W, pady=10)

        self.inventory_tree = ttk.Treeview(self.inventory_frame, columns=(
            "PRODUCT_REAL_ID", "DATE", "PRODUCT_NAME", "PRODUCT_ID", "STOCKS", "CATEGORY",
            "PURCHASE_PRICE", "SELLING_PRICE", "LOCATION", "INTERNAL_REFERENCE"), show='headings')
        self.inventory_tree.heading("PRODUCT_REAL_ID", text="Product Real ID")
        self.inventory_tree.heading("DATE", text="Date")
        self.inventory_tree.heading("PRODUCT_NAME", text="Product Name")
        self.inventory_tree.heading("PRODUCT_ID", text="Product ID")
        self.inventory_tree.heading("STOCKS", text="Stocks")
        self.inventory_tree.heading("CATEGORY", text="Category")
        self.inventory_tree.heading("PURCHASE_PRICE", text="Purchase Price")
        self.inventory_tree.heading("SELLING_PRICE", text="Selling Price")
        self.inventory_tree.heading("LOCATION", text="Location")
        self.inventory_tree.heading("INTERNAL_REFERENCE", text="Internal Reference")
        self.inventory_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.inventory_tree.column("PRODUCT_REAL_ID", width=0, stretch=tk.NO)

    def close_subpanel(self):
        subprocess.Popen(["python", "admin_panel.py"])  # Assuming this line opens another script or window
        self.root.destroy()  # Close the main window and all associated frames

    def load_sales_order_data(self):
        self.sales_order_tree.delete(*self.sales_order_tree.get_children())

        self.cursor.execute('SELECT * FROM Sales_Orders')
        rows = self.cursor.fetchall()

        for row in rows:
            self.sales_order_tree.insert('', 'end', values=row)

    def create_sales_order_window(self):
        selected_item = self.inventory_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select an inventory item before adding a sales order.')
            return

        inventory_item = self.inventory_tree.item(selected_item)['values']
        self.selected_product_name = inventory_item[2]
        self.selected_product_id = inventory_item[3]
        self.selected_category = inventory_item[5]
        self.selected_quantity = inventory_item[4]
        self.selected_date = inventory_item[1]

        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Add Sales Order')
        self.extra_window.geometry('400x300')

        title_label = ctk.CTkLabel(self.extra_window, text="ADD NEW SALES ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)

        # Location Branch
        location_branch_frame = ctk.CTkFrame(self.extra_window)
        location_branch_frame.pack(pady=5, padx=10, fill=tk.X)
        location_branch_label = ctk.CTkLabel(location_branch_frame, text="Location Branch:")
        location_branch_label.pack(side=tk.LEFT)
        self.location_branch_var = tk.StringVar()
        self.location_branch_entry = ctk.CTkEntry(location_branch_frame, textvariable=self.location_branch_var)
        self.location_branch_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        add_button = ctk.CTkButton(self.extra_window, text="Add Order", command=self.add_sales_order)
        add_button.pack(pady=10)

        clear_button = ctk.CTkButton(self.extra_window, text="Clear", command=self.clear_sales_order_entries)
        clear_button.pack(pady=10)

    #################################### Sales Order into database function #############################################
    def add_sales_order(self):
        location_branch = self.location_branch_var.get()

        if location_branch:
            self.cursor.execute(
                'INSERT INTO Sales_Orders (PRODUCT_NAME, PRODUCT_ID, CATEGORY, QUANTITY, DATE, STORE_BRANCH) VALUES (?, ?, ?, ?, ?, ?)',
                (self.selected_product_name, self.selected_product_id, self.selected_category, self.selected_quantity,
                 self.selected_date,
                 location_branch)
            )
            self.connector.commit()
            self.load_sales_order_data()
            messagebox.showinfo('Success', 'Sales order added successfully!')
            self.extra_window.destroy()
        else:
            messagebox.showwarning('Error', 'Please fill in the location branch.')

    # def load_vendor_data(self):
    #     self.inventory_tree.delete(*self.inventory_tree.get_children())
    #
    #     self.cursor.execute('SELECT * FROM Vendors')
    #     rows = self.cursor.fetchall()
    #
    #     for row in rows:
    #         self.inventory_tree.insert('', 'end', values=row)

    # def edit_order_window(self):
    #     selected_item = self.sales_order_tree.selection()
    #     if not selected_item:
    #         messagebox.showerror("Error", "Please select an order to edit.")
    #         return
    #     order_id = self.sales_order_tree.item(selected_item)['values'][0]
    # 
    #     self.edit_window = ctk.CTkToplevel(self.root)
    #     self.edit_window.title('Edit Sales Order')
    #     self.edit_window.geometry('600x600')
    #     title_label = ctk.CTkLabel(self.edit_window, text="EDIT SALES ORDER", font=("Helvetica", 20, 'bold'))
    #     title_label.pack(pady=20)
    #     self.edit_window.attributes('-topmost', True)
    # 
    #     # Product Name
    #     name_frame = ctk.CTkFrame(self.edit_window)
    #     name_frame.pack(pady=5, padx=10, fill=tk.X)
    #     name_label = ctk.CTkLabel(name_frame, text="Product Name:")
    #     name_label.pack(side=tk.LEFT)
    #     self.edit_name_entry = ctk.CTkEntry(name_frame)
    #     self.edit_name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    # 
    #     # Category
    #     category_frame = ctk.CTkFrame(self.edit_window)
    #     category_frame.pack(pady=5, padx=10, fill=tk.X)
    #     category_label = ctk.CTkLabel(category_frame, text="Category:")
    #     category_label.pack(side=tk.LEFT)
    #     self.edit_category_var = tk.StringVar()
    #     self.edit_category_menu = ttk.Combobox(category_frame, textvariable=self.edit_category_var,
    #                                            values=["Electronics", "Appliances", "Personal Care", "Homeware",
    #                                                    "Furniture"])
    #     self.edit_category_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    # 
    #     # Quantity
    #     quantity_frame = ctk.CTkFrame(self.edit_window)
    #     quantity_frame.pack(pady=5, padx=10, fill=tk.X)
    #     quantity_label = ctk.CTkLabel(quantity_frame, text="Quantity:")
    #     quantity_label.pack(side=tk.LEFT)
    #     self.edit_quantity_entry = ctk.CTkEntry(quantity_frame)
    #     self.edit_quantity_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    # 
    #     # Vendor ID
    #     vendor_id_frame = ctk.CTkFrame(self.edit_window)
    #     vendor_id_frame.pack(pady=5, padx=10, fill=tk.X)
    #     vendor_id_label = ctk.CTkLabel(vendor_id_frame, text="Vendor ID:")
    #     vendor_id_label.pack(side=tk.LEFT)
    #     self.edit_vendor_id_entry = ctk.CTkEntry(vendor_id_frame)
    #     self.edit_vendor_id_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    # 
    #     # Product ID
    #     product_id_frame = ctk.CTkFrame(self.edit_window)
    #     product_id_frame.pack(pady=5, padx=10, fill=tk.X)
    #     product_id_label = ctk.CTkLabel(product_id_frame, text="Product ID:")
    #     product_id_label.pack(side=tk.LEFT)
    #     self.edit_product_id_entry = ctk.CTkEntry(product_id_frame)
    #     self.edit_product_id_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    # 
    #     # Submit button
    #     submit_button = ctk.CTkButton(self.edit_window, text="Update Order",
    #                                   command=lambda: self.update_order(order_id))
    #     submit_button.pack(pady=20)
    # 
    #     self.cursor.execute('SELECT * FROM Orders WHERE ORDER_ID = ?', (order_id,))
    #     order = self.cursor.fetchone()
    # 
    #     self.edit_name_entry.insert(0, order[1])
    #     self.edit_product_id_entry.insert(0, order[2])
    #     self.edit_category_var.set(order[3])
    #     self.edit_quantity_entry.insert(0, order[4])
    #     self.edit_vendor_id_entry.insert(0, order[5])

    # def update_order(self, order_id):
    #     name = self.edit_name_entry.get()
    #     product_id = self.edit_product_id_entry.get()
    #     category = self.edit_category_var.get()
    #     quantity = self.edit_quantity_entry.get()
    #     vendor_id = self.edit_vendor_id_entry.get()
    # 
    #     self.cursor.execute('''
    #     UPDATE Orders SET PRODUCT_NAME = ?, PRODUCT_ID = ?, CATEGORY = ?, QUANTITY = ?, VENDOR_ID = ?
    #     WHERE ORDER_ID = ?
    #     ''', (name, product_id, category, quantity, vendor_id, order_id))
    #     self.connector.commit()
    # 
    #     self.load_sales_order_data()
    #     self.edit_window.destroy()
    #     self.add_notification(f"Updated order ID {order_id} for {name}")

    def delete_order(self):
        selected_item = self.sales_order_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select a sales order to delete.')
            return

        confirm = messagebox.askyesno('Confirm Delete', 'Are you sure you want to delete the selected sales order?')
        if not confirm:
            return

        order_id = self.sales_order_tree.item(selected_item)['values'][0]
        self.cursor.execute('DELETE FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))
        self.connector.commit()
        self.load_sales_order_data()
        messagebox.showinfo('Success', 'Sales order deleted successfully!')

################################## Complete Order functions into database ##############################################
    def complete_order(self, order):
        selected_item = self.sales_order_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select a sales order to complete.')
            return

        order_id = self.sales_order_tree.item(selected_item)['values'][0]
        inv_id = self.inventory_tree.item(selected_item)['values'][0]

        confirm = messagebox.askyesno('Confirm Complete', 'Are you sure you want to complete the selected sales order?')
        if not confirm:
            return

        self.cursor.execute('DELETE FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))
        self.cursor.execute('DELETE FROM Inventory WHERE PRODUCT_REAL_ID=?', (inv_id,))
        self.connector.commit()
        self.load_sales_order_data()
        self.load_inventory_data()
        messagebox.showinfo('Success', 'Sales order completed successfully!')

    ########################## Display inventory data #######################################################################
    def load_inventory_data(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())

        self.cursor.execute("SELECT * FROM Inventory WHERE LOCATION='Shipping Area'")
        rows = self.cursor.fetchall()

        for row in rows:
            self.inventory_tree.insert('', 'end', values=row)

    def clear_order_entries(self):
        self.name_entry.delete(0, tk.END)
        self.category_menu.set('')
        self.quantity_entry.delete(0, tk.END)
        self.store_branch_entry.delete(0, tk.END)

    ######################################## COMPLETE ORDER FUNCTION ###################################################
    # def complete_order_window(self):
    #     selected_item = self.sales_order_tree.selection()
    #     if not selected_item:
    #         messagebox.showwarning('Error', 'Please select an order to complete.')
    #         return
    #
    #     order_id = self.sales_order_tree.item(selected_item)['values'][0]
    #     self.extra_window = ctk.CTkToplevel(self.root)
    #     self.extra_window.title('Complete Order')
    #     self.extra_window.geometry('600x600')
    #
    #     title_label = ctk.CTkLabel(self.extra_window, text="COMPLETE ORDER", font=("Helvetica", 14))
    #     title_label.pack(pady=20)
    #
    #     self.cursor.execute('SELECT * FROM Orders WHERE ORDER_ID=?', (order_id,))
    #     order = self.cursor.fetchone()
    #
    #     self.complete_order_id = order[0]
    #
    #     # Date
    #     date_frame = ctk.CTkFrame(self.extra_window)
    #     date_frame.pack(pady=5, padx=10, fill=tk.X)
    #     date_label = ctk.CTkLabel(date_frame, text="Date:")
    #     date_label.pack(side=tk.LEFT)
    #     self.date_entry = ctk.CTkEntry(date_frame)
    #     self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
    #     self.date_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    #
    #     # Sales Price
    #     sales_price_frame = ctk.CTkFrame(self.extra_window)
    #     sales_price_frame.pack(pady=5, padx=10, fill=tk.X)
    #     sales_price_label = ctk.CTkLabel(sales_price_frame, text="Sales Price:")
    #     sales_price_label.pack(side=tk.LEFT)
    #     self.sales_price_entry = ctk.CTkEntry(sales_price_frame)
    #     self.sales_price_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    #
    #     # Selling Price
    #     selling_price_frame = ctk.CTkFrame(self.extra_window)
    #     selling_price_frame.pack(pady=5, padx=10, fill=tk.X)
    #     selling_price_label = ctk.CTkLabel(selling_price_frame, text="Selling Price:")
    #     selling_price_label.pack(side=tk.LEFT)
    #     self.selling_price_entry = ctk.CTkEntry(selling_price_frame)
    #     self.selling_price_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
    #
    #     complete_button = ctk.CTkButton(self.extra_window, text="Complete Order", command=self.complete_order)
    #     complete_button.pack(pady=10)

    def complete_order(self):
        selected_item = self.sales_order_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select a sales order to complete.')
            return

        order_id = self.sales_order_tree.item(selected_item)['values'][0]
        inv_id = self.inventory_tree.item(selected_item)['values'][0]

        confirm = messagebox.askyesno('Confirm Complete', 'Are you sure you want to complete the selected sales order?')
        if not confirm:
            return

        self.cursor.execute('DELETE FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))
        self.cursor.execute('DELETE FROM Inventory WHERE PRODUCT_REAL_ID=?', (inv_id,))
        self.connector.commit()
        self.load_sales_order_data()
        self.load_inventory_data()
        messagebox.showinfo('Success', 'Sales order completed successfully!')

    ########################NOTIFICAITON FUNCTIONS######################################################################

    def add_notification(self, description):
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION) VALUES (?)', (description,))
        self.connector.commit()
        self.load_notifications()

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


if __name__ == "__main__":
    root = ctk.CTk()
    app = SalesApp(root, "Admin")
    root.mainloop()