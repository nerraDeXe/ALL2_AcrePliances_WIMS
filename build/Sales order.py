import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timezone
from PIL import Image, ImageTk
import pytz
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from tkinter import filedialog
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors


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
        self.is_filter_active = False
        self.detached_items = []
        self.selected_column = ''
        self.header_menu = tk.Menu(root, tearoff=0)
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
        self.generate_report_button = ctk.CTkButton(left_frame, text="GENERATE SHIPPED STOCK REPORT",
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

        # Create a new Toplevel window for adding sales order
        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Add Sales Order')
        self.extra_window.attributes('-topmost', True)

        # Add a red heading
        ctk.CTkLabel(self.extra_window, text="Add Sales Order", font=('Helvetica', 20, 'bold'), text_color='red').grid(
            row=0, columnspan=2, padx=10, pady=10)

        # Setup Quantity Widgets
        ctk.CTkLabel(self.extra_window, text="Quantity:", font=('Gill Sans MT', 13)).grid(row=1, column=0, padx=10,
                                                                                          pady=10)
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ctk.CTkEntry(self.extra_window, textvariable=self.quantity_var, font=('Gill Sans MT', 13),
                                           width=200)
        self.quantity_entry.grid(row=1, column=1, padx=10, pady=10)

        # Setup Location Branch Widgets
        ctk.CTkLabel(self.extra_window, text="Location Branch:", font=('Gill Sans MT', 13)).grid(row=2, column=0,
                                                                                                 padx=10, pady=10)
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
        self.location_branch_combobox = ctk.CTkComboBox(self.extra_window, variable=self.location_branch_var,
                                                        values=branches)
        self.location_branch_combobox.grid(row=2, column=1, padx=10, pady=10)

        # Add buttons for Add Order and Cancel
        ctk.CTkButton(self.extra_window, text='Add Order', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                      command=self.add_sales_order).grid(row=3, column=0, padx=10, pady=10)
        ctk.CTkButton(self.extra_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                      command=self.extra_window.destroy).grid(row=3, column=1, padx=10, pady=10)

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

        # Retrieve the details of the selected sales order before deleting it
        self.cursor.execute('SELECT PRODUCT_ID, QUANTITY FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))
        order_details = self.cursor.fetchone()
        if not order_details:
            messagebox.showerror('Error', 'Failed to retrieve sales order details.')
            return

        product_id, quantity = order_details

        # Delete the sales order
        self.cursor.execute('DELETE FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))

        # Update the inventory by adding back the quantity
        self.cursor.execute('UPDATE Inventory SET STOCKS = STOCKS + ? WHERE PRODUCT_ID = ?', (quantity, product_id))

        # Commit the changes to the database
        self.connector.commit()

        # Reload the sales order and inventory data
        self.load_sales_order_data()
        self.load_inventory_data()

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

    def show_notifications_window(self):
        subprocess.Popen(["python", "Notifications.py"])

    def generate_shipped_stock_report(self):
        report_window = ctk.CTkToplevel(self.root)
        report_window.title('Shipped Stock Report')
        report_window.geometry('1000x500')
        report_window.attributes('-topmost', 'true')
        report_window.configure(fg_color='#BF2C37')
        report_window.resizable(0, 0)

        # Treeview to display data
        columns = (
            "Shipped ID", "Product Name", "Product ID", "Category", "Quantity", "Date", "Store Branch", "Shipped Time")
        tree = ttk.Treeview(report_window, columns=columns, show='headings')
        tree.pack(expand=True, fill='both')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, minwidth=0, width=100)

        self.cursor.execute('SELECT * FROM Shipped_Stock')
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", "end", values=row)

        # Add filtering functionality
        def show_filter_menu(event):
            selected_column = tree.identify_column(event.x)
            column_index = int(selected_column.replace("#", "")) - 1

            if self.selected_column != column_index:
                self.selected_column = column_index
                self.is_filter_active = False

            menu = tk.Menu(report_window, tearoff=0)
            menu.add_command(label="Sort Ascending", command=lambda: self.sort_column(tree, self.selected_column, True))
            menu.add_command(label="Sort Descending",
                             command=lambda: self.sort_column(tree, self.selected_column, False))
            menu.add_command(label="Filter", command=lambda: self.filter_column(tree, self.selected_column))
            menu.tk_popup(event.x_root, event.y_root)

        tree.bind("<Button-3>", show_filter_menu)

        # Save as PDF
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

    def sort_column(self, tree, col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))

    def filter_column(self, tree, col):
        filter_value = simpledialog.askstring("Filter", f"Enter value to filter {col}:")
        if not filter_value:
            return

        children = tree.get_children('')
        for child in children:
            tree.detach(child)

        filtered_items = [child for child in children if filter_value.lower() in tree.set(child, col).lower()]
        for item in filtered_items:
            tree.reattach(item, '', 'end')

        self.detached_items = [child for child in children if child not in filtered_items]
        self.is_filter_active = True

    def create_pdf_report(self, file_path, rows):
        document = SimpleDocTemplate(file_path, pagesize=letter)
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
        elements.append(Spacer(1, 12))

        # Title
        title_style = ParagraphStyle(name='Title', fontSize=18, alignment=1, spaceAfter=14)
        title = Paragraph("Shipped Stock Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Line separator
        elements.append(Paragraph('<hr width="100%" color="black"/>', getSampleStyleSheet()["Normal"]))
        elements.append(Spacer(1, 12))

        # Table Data
        for row in rows:
            data = [
                ["Shipped ID", f"{row[0]}"],
                ["Product Name", f"{row[1]}"],
                ["Product ID", f"{row[2]}"],
                ["Category", f"{row[3]}"],
                ["Quantity", f"{row[4]}"],
                ["Date", f"{row[5]}"],
                ["Store Branch", f"{row[6]}"],
                ["Shipped Time", f"{row[7]}"],
            ]

            table = Table(data, colWidths=[2 * inch, 4 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))

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

        document.build(elements)


if __name__ == "__main__":
    root = ctk.CTk()
    app = SalesApp(root, "admin")
    root.mainloop()
