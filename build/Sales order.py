import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timezone
from PIL import Image, ImageTk
import pytz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import filedialog
from fpdf import FPDF


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

        title_label = ctk.CTkLabel(top_frame, text="SALES ORDER MANAGEMENT", font=("Helvetica", 16), text_color='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        self.notification_image = ImageTk.PhotoImage(Image.open("nored.png"))
        self.notification_button = tk.Button(top_frame, image=self.notification_image, bg='white',
                                             activebackground='darkred', command=self.show_notifications_window)
        self.notification_button.pack(side=tk.RIGHT, padx=20, pady=20)

        left_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=20)

        self.add_sales_order_button = ctk.CTkButton(left_frame, text="ADD SALES ORDER", fg_color='#FFFFFF',
                                                    text_color='#000000', command=self.create_sales_order_window)
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
                                           font=("Helvetica", 20, 'bold'), text_color='black')
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

        self.sales_order_tree.column("ID", width=50, stretch=tk.NO)
        self.sales_order_tree.column("Product Name", width=280, stretch=tk.NO)
        self.sales_order_tree.column("Product ID", width=100, stretch=tk.NO)
        self.sales_order_tree.column("Category", width=150, stretch=tk.NO)
        self.sales_order_tree.column("Quantity", width=100, stretch=tk.NO)
        self.sales_order_tree.column("Date", width=194, stretch=tk.NO)
        self.sales_order_tree.column("Store Branch", width=200, stretch=tk.NO)

        self.sales_order_tree.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        inventory_details_label = ctk.CTkLabel(self.inventory_frame, text="Inventory:", font=("Helvetica", 20, 'bold'),
                                               text_color='black')
        inventory_details_label.pack(anchor=tk.W, pady=10)

        self.inventory_tree = ttk.Treeview(self.inventory_frame, columns=(
            "PRODUCT_REAL_ID", "DATE", "PRODUCT_NAME", "PRODUCT_ID", "STOCKS", "CATEGORY", "PURCHASE_PRICE",
            "SELLING_PRICE", "LOCATION", "INTERNAL_REFERENCE"), show='headings')
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

        # Adjust column widths
        self.adjust_column_widths()

        # Add a button to generate the shipped stock report
        self.generate_report_button = ctk.CTkButton(left_frame, text="Generate Shipped Stock Report",
                                                    fg_color='#FFFFFF', text_color='#000000',
                                                    command=self.generate_shipped_stock_report)
        self.generate_report_button.pack(pady=10)

    def adjust_column_widths(self):
        # Calculate available width for remaining columns
        total_width = self.inventory_frame.winfo_width()
        visible_columns = [col for col in self.inventory_tree["columns"] if col != "PRODUCT_REAL_ID"]
        column_count = len(visible_columns)

        if column_count > 0 and total_width > 0:
            equal_width = total_width // column_count

            for col in visible_columns:
                self.inventory_tree.column(col, width=equal_width)

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
        self.extra_window.attributes('-topmost', 'true')

        title_label = ctk.CTkLabel(self.extra_window, text="ADD NEW SALES ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)

        quantity_frame = ctk.CTkFrame(self.extra_window)
        quantity_frame.pack(pady=5, padx=10, fill=tk.X)
        quantity_label = ctk.CTkLabel(quantity_frame, text="Quantity:")
        quantity_label.pack(side=tk.LEFT)
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ctk.CTkEntry(quantity_frame, textvariable=self.quantity_var)
        self.quantity_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        location_branch_frame = ctk.CTkFrame(self.extra_window)
        location_branch_frame.pack(pady=5, padx=10, fill=tk.X)
        location_branch_label = ctk.CTkLabel(location_branch_frame, text="Location Branch:")
        location_branch_label.pack(side=tk.LEFT)

        branches = [
            "AcrePliances Penang",
            "AcrePliances Kedah",
            "AcrePliances Perlis",
            "AcrePliances Perak",
            "AcrePliances Kelantan",
            "AcrePliances Terengganu",
            "AcrePliances Pahang",
            "AcrePliances Johor",
            "AcrePliances Melaka",
            "AcrePliances Negeri Sembilan"
        ]
        self.location_branch_var = tk.StringVar()
        self.location_branch_combobox = ttk.Combobox(location_branch_frame, textvariable=self.location_branch_var,
                                                     values=branches)
        self.location_branch_combobox.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        add_button = ctk.CTkButton(self.extra_window, text="Add Order", command=self.add_sales_order)
        add_button.pack(pady=10)

    def add_sales_order(self):
        quantity = int(self.quantity_var.get())
        location_branch = self.location_branch_var.get()

        if quantity > self.selected_quantity:
            messagebox.showwarning('Error', 'Quantity exceeds available stocks.')
            return

        if quantity and location_branch:
            self.cursor.execute(
                'INSERT INTO Sales_Orders (PRODUCT_NAME, PRODUCT_ID, CATEGORY, QUANTITY, DATE, STORE_BRANCH) VALUES ('
                '?, ?, ?, ?, ?, ?)',
                (self.selected_product_name, self.selected_product_id, self.selected_category, quantity,
                 self.selected_date, location_branch)
            )
            self.cursor.execute(
                'UPDATE Inventory SET STOCKS = STOCKS - ? WHERE PRODUCT_ID = ?',
                (quantity, self.selected_product_id)
            )

            # Check the stock level after the update
            self.cursor.execute(
                'SELECT STOCKS FROM Inventory WHERE PRODUCT_ID = ?',
                (self.selected_product_id,)
            )
            updated_stock = self.cursor.fetchone()[0]

            # Remove inventory data if stock is less than or equal to 0
            if updated_stock <= 0:
                self.cursor.execute(
                    'DELETE FROM Inventory WHERE PRODUCT_ID = ?',
                    (self.selected_product_id,)
                )

            self.connector.commit()
            self.load_sales_order_data()
            self.load_inventory_data()
            self.extra_window.destroy()
            messagebox.showinfo('Success', 'Sales order added successfully!')
            self.add_notification(
                f'{self.selected_product_name} has been moved to Shipping Area with {quantity} quantity.')

        else:
            messagebox.showwarning('Error', 'Please fill in all the details.')

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

        order = self.sales_order_tree.item(selected_item)['values']
        order_id = order[0]

        confirm = messagebox.askyesno('Confirm Complete', 'Are you sure you want to complete the selected sales order?')
        if not confirm:
            return

        shipped_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(
            'INSERT INTO Shipped_Stock (PRODUCT_NAME, PRODUCT_ID, CATEGORY, QUANTITY, DATE, STORE_BRANCH, '
            'SHIPPED_TIME) VALUES ('
            '?, ?, ?, ?, ?, ?, ?)',
            (order[1], order[2], order[3], order[4], order[5], order[6], shipped_time)
        )
        self.cursor.execute('DELETE FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))
        self.connector.commit()
        self.load_sales_order_data()
        self.load_inventory_data()
        self.add_notification(f"Order {order_id} completed and shipped.")
        messagebox.showinfo('Success', 'Sales order completed and shipped successfully!')

    def add_notification(self, description):
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION, TIMESTAMP) VALUES (?, ?)',
                            (description, timestamp))
        self.connector.commit()
        self.load_notifications()

    def show_notifications_window(self):
        self.notification_window = ctk.CTkToplevel(self.root)
        self.notification_window.title('Notifications')
        self.notification_window.geometry('600x400')
        self.notification_window.resizable(0, 0)
        self.notification_window.attributes('-topmost', True)

        # Set the background color to red
        self.notification_window.configure(fg_color='#BF2C37')

        notification_label = ctk.CTkLabel(self.notification_window, text="Notifications",
                                          font=("Helvetica", 14, 'bold'))
        notification_label.pack(pady=20)

        self.NOTIFICATION_LIST = tk.Listbox(self.notification_window)
        self.NOTIFICATION_LIST.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.load_notifications()

        delete_button = ctk.CTkButton(self.notification_window, text="Delete Selected",
                                      command=self.delete_selected_notification,
                                      fg_color="black")
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
            if hasattr(self, 'NOTIFICATION_LIST'):
                self.NOTIFICATION_LIST.delete(0, tk.END)
                self.notification_ids = {}
                self.cursor.execute("SELECT * FROM Notifications ORDER BY TIMESTAMP DESC")
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

    def generate_shipped_stock_report(self):
        # Create a new window to display Shipped_Stock entity
        report_window = ctk.CTkToplevel(self.root)
        report_window.title('Shipped Stock Report')
        report_window.geometry('1000x500')
        report_window.attributes('-topmost', 'true')
        report_window.configure(fg_color='#BF2C37')
        report_window.resizable(0, 0)

        # # Configure dark mode style for Treeview
        # style = ttk.Style()
        # style.theme_use('clam')
        # style.configure("Treeview",
        #                 background="#2E2E2E",
        #                 foreground="white",
        #                 fieldbackground="#2E2E2E",
        #                 font=("Helvetica", 10))
        # style.map("Treeview", background=[("selected", "#5E5E5E")])

        # Treeview to display data
        tree = ttk.Treeview(report_window, columns=(
            "Shipped ID", "Product Name", "Product ID", "Category", "Quantity", "Date", "Store Branch", "Shipped Time"),
                            show='headings')
        tree.pack(expand=True, fill='both')

        # Define column headings
        for col in tree['columns']:
            tree.heading(col, text=col)
            tree.column(col, minwidth=0, width=100)

        # Fetch data from the database
        self.cursor.execute('SELECT * FROM Shipped_Stock')
        rows = self.cursor.fetchall()

        # Insert data into the treeview
        for row in rows:
            tree.insert("", "end", values=row)

        save_label = ctk.CTkLabel(report_window, text="Select rows and Save Shipped Stock Report as PDF",
                                  font=("Helvetica", 14, 'bold'))
        save_label.pack(pady=20)

        def save_pdf():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning("No selection", "Please select rows to generate the report")
                return
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if file_path:
                selected_rows = [tree.item(item, 'values') for item in selected_items]
                self.create_pdf_report(file_path, selected_rows)
                messagebox.showinfo('Success', f'Report saved successfully at {file_path}')
                report_window.destroy()

        save_button = ctk.CTkButton(report_window, text="Save as PDF", command=save_pdf)
        save_button.pack(pady=10)

    def create_pdf_report(self, file_path, rows):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(200, 10, txt="Shipped Stock Report", ln=True, align='C')

        pdf.set_font("Arial", size=12)
        for row in rows:
            shipped_id, product_name, product_id, category, quantity, date, store_branch, shipped_time = row
            pdf.cell(200, 10, txt=f"Shipped ID: {shipped_id}", ln=True)
            pdf.cell(200, 10, txt=f"Product Name: {product_name}", ln=True)
            pdf.cell(200, 10, txt=f"Product ID: {product_id}", ln=True)
            pdf.cell(200, 10, txt=f"Category: {category}", ln=True)
            pdf.cell(200, 10, txt=f"Quantity: {quantity}", ln=True)
            pdf.cell(200, 10, txt=f"Date: {date}", ln=True)
            pdf.cell(200, 10, txt=f"Store Branch: {store_branch}", ln=True)
            pdf.cell(200, 10, txt=f"Shipped Time: {shipped_time}", ln=True)
            pdf.cell(200, 10, txt="", ln=True)  # Add a blank line for spacing

        pdf.output(file_path)


if __name__ == "__main__":
    root = ctk.CTk()
    app = SalesApp(root, "admin")
    root.mainloop()
