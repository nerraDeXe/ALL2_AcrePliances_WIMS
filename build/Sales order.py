import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import pytz


class SalesApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect('AcrePliances.db')
        self.cursor = self.connector.cursor()

        self.connector.commit()

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

        self.delete_sales_order_button = ctk.CTkButton(left_frame, text="DELETE SALES ORDER", fg_color='#FFFFFF',
                                                       text_color='#000000', command=self.delete_order)
        self.delete_sales_order_button.pack(pady=10)

        self.complete_order_button = ctk.CTkButton(left_frame, text="COMPLETE ORDER", fg_color='#FFFFFF',
                                                   text_color='#000000', command=self.complete_sales_order)
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
        self.sales_order_tree.heading("Store Branch", text="Store Branch")
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
        self.extra_window.geometry('400x500')

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

    def add_sales_order(self):
        location_branch = self.location_branch_var.get()

        if location_branch:
            self.cursor.execute(
                'INSERT INTO Sales_Orders (PRODUCT_NAME, PRODUCT_ID, CATEGORY, QUANTITY, DATE, STORE_BRANCH) VALUES ('
                '?, ?, ?, ?, ?, ?)',
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

    def load_inventory_data(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())

        self.cursor.execute("SELECT * FROM Inventory WHERE LOCATION='Storage Area'")
        rows = self.cursor.fetchall()

        for row in rows:
            self.inventory_tree.insert('', 'end', values=row)

    def complete_sales_order(self):
        selected_item = self.sales_order_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select a sales order to complete.')
            return

        order_id = self.sales_order_tree.item(selected_item)['values'][0]

        confirm = messagebox.askyesno('Confirm Complete', 'Are you sure you want to complete the selected sales order?')
        if not confirm:
            return

        self.cursor.execute('DELETE FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))
        self.connector.commit()
        self.load_sales_order_data()
        self.load_inventory_data()
        messagebox.showinfo('Success', 'Sales order completed successfully!')

    def add_notification(self, description):
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION, TIMESTAMP) VALUES (?, ?)',
                            (description, timestamp))
        self.connector.commit()
        self.load_notifications()

    def show_notifications_window(self):
        self.notification_window = ctk.CTkToplevel(self.root)
        self.notification_window.title('Notifications')
        self.notification_window.geometry('500x400')
        self.notification_window.resizable(0, 0)

        notification_label = ctk.CTkLabel(self.notification_window, text="Notifications", font=("Helvetica", 14))
        notification_label.pack(pady=20)

        self.NOTIFICATION_LIST = tk.Listbox(self.notification_window)
        self.NOTIFICATION_LIST.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.load_notifications()

        delete_button = ctk.CTkButton(self.notification_window, text="Delete Selected",
                                      command=self.delete_selected_notification)
        delete_button.pack(pady=10)

    def delete_selected_notification(self):
        selected_indices = self.NOTIFICATION_LIST.curselection()

        if not selected_indices:
            messagebox.showwarning('No notification selected!', 'Please select a notification to delete.')
            return

        confirm_delete = messagebox.askyesno('Confirm Delete',
                                             'Are you sure you want to delete the selected notification(s)?')
        if not confirm_delete:
            return

        for index in selected_indices:
            try:
                notification_id = self.notification_ids[index]
                self.cursor.execute('DELETE FROM Notifications WHERE NOTIFICATION_ID=?', (notification_id,))
                self.connector.commit()
            except sqlite3.Error as e:
                messagebox.showerror('Error', f'Error deleting notification: {str(e)}')
                return

        self.load_notifications()

    def load_notifications(self):
        try:
            self.NOTIFICATION_LIST.delete(0, tk.END)
            self.notification_ids = {}
            self.cursor.execute("SELECT * FROM Notifications")
            notifications = self.cursor.fetchall()

            for idx, notification in enumerate(notifications):
                timestamp = datetime.strptime(notification[2], '%Y-%m-%d %H:%M:%S')
                utc_timezone = pytz.utc
                local_timezone = pytz.timezone('Asia/Singapore')
                utc_timestamp = utc_timezone.localize(timestamp)
                local_timestamp = utc_timestamp.astimezone(local_timezone)
                formatted_timestamp = local_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                message_with_timestamp = f"{formatted_timestamp} - {notification[1]}"
                self.NOTIFICATION_LIST.insert(tk.END, message_with_timestamp)
                self.notification_ids[idx] = notification[0]
        except sqlite3.Error as e:
            messagebox.showerror('Error', f'Error loading notifications: {str(e)}')


if __name__ == "__main__":
    root = ctk.CTk()
    app = SalesApp(root, "Admin")
    root.mainloop()
