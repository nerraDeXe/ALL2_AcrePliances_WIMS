import datetime
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox, Menu
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import pytz
from fpdf import FPDF
from tkcalendar import DateEntry


class InventoryApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect('AcrePliances.db')
        self.cursor = self.connector.cursor()

        self.connector.commit()

        self.root = root
        self.username = username
        self.root.title('Inventory Management')
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')
        self.root.resizable(0, 0)

        self.setup_variables()
        self.create_widgets()
        self.detached_items = []
        self.load_inventory_data()

    def setup_variables(self):
        self.PRODUCT_NAME = tk.StringVar()
        self.PRODUCT_ID = tk.StringVar()
        self.STOCKS = tk.IntVar()
        self.QUANTITY = tk.IntVar()
        self.PURCHASE_PRICE = tk.DoubleVar()
        self.SELLING_PRICE = tk.DoubleVar()
        self.CATEGORY = tk.StringVar(value='Electronics')
        self.LOCATION = tk.StringVar(value='Staging Area')
        self.INTERNAL_REFERENCE = tk.StringVar()
        self.AMOUNT_TO_MOVE = tk.IntVar()
        self.NEW_LOCATION = tk.StringVar()
        self.date = DateEntry(date=datetime.now().date())

    def create_widgets(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="INVENTORY", font=("Helvetica", 16),
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

        self.delete_inventory_button = ctk.CTkButton(left_frame, text="DELETE INVENTORY", fg_color='#FFFFFF', command=self.remove_inventory,
                                                    text_color='#000000'
                                                    )
        self.delete_inventory_button.pack(pady=10)

        self.edit_inventory_button = ctk.CTkButton(left_frame, text="EDIT SELECTED PRODUCT", fg_color='#FFFFFF', command=self.edit_product_details,
                                                       text_color='#000000')
        self.edit_inventory_button.pack(pady=10)

        self.move_inventory_button = ctk.CTkButton(left_frame, text="MOVE PRODUCT LOCATION", fg_color='#FFFFFF', command=self.move_product_location,
                                                   text_color='#000000')
        self.move_inventory_button.pack(pady=10)

        self.back_button = ctk.CTkButton(left_frame, text="Back", command=self.close_subpanel)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = ctk.CTkFrame(self.root, fg_color='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=20)

        self.inventory_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.inventory_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

        # Adjust column widths
        self.adjust_column_widths()

        # Right-click menu for header
        self.header_menu = Menu(self.root, tearoff=0)
        self.header_menu.add_command(label="Filter", command=self.filter_by_column)

        # Bind right-click to show context menu
        self.inventory_tree.bind("<Button-3>", self.show_header_menu)

        # Bind resize event to adjust column widths dynamically
        self.root.bind("<Configure>", self.on_resize)

    def adjust_column_widths(self):
        # Calculate available width for remaining columns
        total_width = self.inventory_frame.winfo_width()
        visible_columns = [col for col in self.inventory_tree["columns"] if col != "PRODUCT_REAL_ID"]
        column_count = len(visible_columns)

        if column_count > 0 and total_width > 0:
            equal_width = total_width // column_count

            for col in visible_columns:
                self.inventory_tree.column(col, width=equal_width)

    def show_header_menu(self, event):
        # Find the column heading that was clicked
        region = self.inventory_tree.identify("region", event.x, event.y)
        if (region == "heading"):
            col = self.inventory_tree.identify_column(event.x)
            self.selected_column = self.inventory_tree.heading(col)["text"]
            self.update_header_menu(col)
            self.header_menu.post(event.x_root, event.y_root)

    def update_header_menu(self, col):
        # Clear previous menu items
        self.header_menu.delete(0, tk.END)

        # Add submenu for unique items
        unique_items_menu = Menu(self.header_menu, tearoff=0)
        unique_items = self.get_unique_items(col)

        for item in unique_items:
            unique_items_menu.add_command(label=item, command=lambda value=item: self.filter_by_column(value))

        self.header_menu.add_cascade(label="Filter by", menu=unique_items_menu)
        self.header_menu.add_command(label="Show All", command=self.show_all)

    def get_unique_items(self, col):
        # Get unique items in the specified column
        col_index = int(col.replace('#', '')) - 1
        items = set()

        for child in self.inventory_tree.get_children():
            item = self.inventory_tree.item(child, 'values')[col_index]
            items.add(item)

        return sorted(items)

    def filter_by_column(self, filter_value):
        col_index = self.inventory_tree["columns"].index(self.selected_column.upper().replace(" ", "_"))

        self.detached_items = []  # Clear the detached items list

        for item in self.inventory_tree.get_children():
            values = self.inventory_tree.item(item, 'values')
            if values[col_index] != filter_value:
                self.detached_items.append(item)
                self.inventory_tree.detach(item)

    def show_all(self):
        for item in self.detached_items:
            self.inventory_tree.reattach(item, '', 'end')
        self.detached_items = []  # Clear the detached items list

    def on_resize(self, event):
        # Adjust column widths dynamically on window resize
        self.adjust_column_widths()

    def close_subpanel(self):
        self.root.destroy()  # Close the main window and all associated frames

    def load_inventory_data(self):
        self.inventory_tree.delete(*self.inventory_tree.get_children())

        self.cursor.execute("SELECT * FROM Inventory")
        rows = self.cursor.fetchall()

        for row in rows:
            self.inventory_tree.insert('', 'end', values=row)

    ############################CRUD####################################################################
    
    def remove_inventory(self):
        if not self.inventory_tree.selection():
            messagebox.showerror('No record selected!', 'Please select a record to delete!')
            return

        current_selected_inventory = self.inventory_tree.item(self.inventory_tree.focus())
        values_selected = current_selected_inventory['values']

        surety = messagebox.askyesno('Are you sure?',
                             f'Are you sure that you want to delete the record of {values_selected[0]}')

        if surety:
            self.connector.execute('DELETE FROM Inventory WHERE PRODUCT_REAL_ID=?', (values_selected[0],))
            self.connector.commit()

            self.load_inventory_data()
            messagebox.showinfo('Record deleted successfully!', f'The record of {values_selected[0]} was deleted successfully')
            self.add_notification()

    def edit_product_details(self):
        if not self.inventory_tree.selection():
            messagebox.showerror('No record selected!', 'Please select a record to edit!')
            return

        current_selected_product = self.inventory_tree.item(self.inventory_tree.focus())
        values = current_selected_product['values']

        # Create a new Toplevel window for editing
        self.edit_window = ctk.CTkToplevel(self.root)
        self.edit_window.title("Edit Inventory")
        self.edit_window.resizable(False, False)

        # Add a red heading
        ctk.CTkLabel(self.edit_window, text="Edit Product", font=('Helvetica', 16, 'bold'), text_color='red').grid(row=0,
                                                                                                               columnspan=2,
                                                                                                               padx=10,
                                                                                                               pady=5)

        # Create and place labels and entries in the new window
        ctk.CTkLabel(self.edit_window, text="Product Name:").grid(row=1, column=0, padx=10, pady=5)
        self.product_name_entry = ctk.CTkEntry(self.edit_window, width=400)
        self.product_name_entry.grid(row=1, column=1, padx=10, pady=5)
        self.product_name_entry.insert(0, values[2])

        ctk.CTkLabel(self.edit_window, text="Stocks:").grid(row=2, column=0, padx=10, pady=5)
        self.stocks_entry = ctk.CTkEntry(self.edit_window, width=400)
        self.stocks_entry.grid(row=2, column=1, padx=10, pady=5)
        self.stocks_entry.insert(0, values[4])

        ctk.CTkLabel(self.edit_window, text="Purchase Price:").grid(row=3, column=0, padx=10, pady=5)
        self.purchase_price_entry = ctk.CTkEntry(self.edit_window, width=400)
        self.purchase_price_entry.grid(row=3, column=1, padx=10, pady=5)
        self.purchase_price_entry.insert(0, values[6])

        ctk.CTkLabel(self.edit_window, text="Selling Price:").grid(row=4, column=0, padx=10, pady=5)
        self.selling_price_entry = ctk.CTkEntry(self.edit_window, width=400)
        self.selling_price_entry.grid(row=4, column=1, padx=10, pady=5)
        self.selling_price_entry.insert(0, values[7])

        # Add buttons for Update and Cancel
        ctk.CTkButton(self.edit_window, text='Update Record', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                  command=self.update_record_direct).grid(row=7, column=0, padx=10, pady=10)
        ctk.CTkButton(self.edit_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                  command=self.edit_window.destroy).grid(row=7, column=1, padx=10, pady=10)

    def move_product_location(self):
        if not self.inventory_tree.selection():
            messagebox.showerror('No record selected!', 'Please select a record to edit!')
            return

        current_selected_product = self.inventory_tree.item(self.inventory_tree.focus())
        values = current_selected_product['values']

        # Create a new Toplevel window for moving product location
        self.move_window = ctk.CTkToplevel(self.root)
        self.move_window.title("Move Product Location")
        self.move_window.resizable(False, False)  # Lock window resizing

        # Add a red heading
        ctk.CTkLabel(self.move_window, text="Move Product Location", font=('Helvetica', 16, 'bold'),
                     text_color='red').grid(
            row=0, columnspan=2, padx=10, pady=5)

        # Setup Move Product Widgets
        self.moveamount_label = ctk.CTkLabel(self.move_window, text='Enter Amount to add:', font=('Gill Sans MT', 13))
        self.moveamount_label.grid(row=1, column=0, padx=10, pady=10)
        self.moveamount = ctk.CTkEntry(self.move_window, font=('Gill Sans MT', 13), width=200,
                                       textvariable=self.AMOUNT_TO_MOVE)
        self.moveamount.grid(row=1, column=1, padx=10, pady=10)

        self.newlocation_label = ctk.CTkLabel(self.move_window, text='New Location:', font=('Gill Sans MT', 13))
        self.newlocation_label.grid(row=2, column=0, padx=10, pady=10)
        self.newlocation = ctk.CTkOptionMenu(self.move_window, variable=self.NEW_LOCATION,
                                             values=['Staging Area', 'Storage Area'])
        self.newlocation.grid(row=2, column=1, padx=10, pady=10)

        # Get the rest of the values
        self.PRODUCT_NAME.set(values[2])
        self.STOCKS.set(values[4])
        self.CATEGORY.set(values[5])
        self.PURCHASE_PRICE.set(values[6])
        self.SELLING_PRICE.set(values[7])
        self.LOCATION.set(values[8])
        self.PRODUCT_ID.set(values[3])
        self.date.set_date(datetime.strptime(values[1], '%Y-%m-%d'))

        # Add buttons for Move Product and Cancel
        ctk.CTkButton(self.move_window, text='Move Product', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                      command=self.update_record).grid(row=3, column=0, padx=10, pady=10)
        ctk.CTkButton(self.move_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                      command=self.move_window.destroy).grid(row=3, column=1, padx=10, pady=10)

    def update_record(self):
        current_selected_product = self.inventory_tree.item(self.inventory_tree.focus())
        contents = current_selected_product['values']

        try:
            # Get the amount to move and new location
            amount_to_move = int(self.AMOUNT_TO_MOVE.get())
            new_location = self.NEW_LOCATION.get()

            if (
                    not self.date.get() or not self.PRODUCT_NAME.get() or not self.STOCKS.get() or not self.CATEGORY.get() or
                    not self.PURCHASE_PRICE.get() or not self.SELLING_PRICE.get() or not self.LOCATION.get() or not new_location or
                    amount_to_move <= 0):
                messagebox.showerror('Fields empty or invalid amount!',
                                     "Please fill all missing fields and ensure the amount to move is greater than zero.")
                return

            current_stock = int(self.STOCKS.get())

            if amount_to_move > current_stock:
                messagebox.showerror('Invalid amount', "The amount to move exceeds the current stock.")
                return

            # Deduct stock from the original location
            new_stock = current_stock - amount_to_move
            if new_stock == 0:
                # Delete the record if all stock is moved
                self.connector.execute(
                    'DELETE FROM Inventory WHERE PRODUCT_REAL_ID=?',
                    (contents[0],)
                )
            else:
                self.connector.execute(
                    'UPDATE Inventory SET STOCKS=? WHERE PRODUCT_REAL_ID=?',
                    (new_stock, contents[0])
                )

            # Check if the product already exists in the new location
            existing_product = self.connector.execute(
                'SELECT * FROM Inventory WHERE PRODUCT_NAME=? AND CATEGORY=? AND LOCATION=?',
                (self.PRODUCT_NAME.get(), self.CATEGORY.get(), new_location)
            ).fetchone()

            if existing_product:
                # Update the existing product's stock at the new location
                new_stock_existing = int(existing_product[4]) + amount_to_move
                self.connector.execute(
                    'UPDATE Inventory SET STOCKS=? WHERE PRODUCT_REAL_ID=?',
                    (new_stock_existing, existing_product[0])  # Use PRODUCT_REAL_ID to avoid confusion
                )
            else:
                location_prefix = new_location[:3].upper()
                new_internal_reference = f"WH-{location_prefix}-{self.PRODUCT_ID.get()}"

                self.connector.execute(
                    'INSERT INTO Inventory (date, PRODUCT_NAME, STOCKS, CATEGORY, PURCHASE_PRICE, SELLING_PRICE, '
                    'LOCATION, INTERNAL_REFERENCE, PRODUCT_ID)'
                    'VALUES (?, LTRIM(RTRIM(?)), ?, ?, ?, ?, ?, ?, ?)', (
                        self.date.get_date(), self.PRODUCT_NAME.get().strip(), amount_to_move, self.CATEGORY.get(),
                        self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), new_location, new_internal_reference,
                        self.PRODUCT_ID.get())
                )

            self.connector.commit()

            messagebox.showinfo('Updated successfully',
                                f'The record of {self.PRODUCT_NAME.get()} was updated successfully and {amount_to_move} items '
                                f'were moved to {new_location}')

            # self.add_notification()
            self.load_inventory_data()
            self.move_window.destroy()

            # Generate PDF report for the original and new record
            self.generate_pdf_report(
                self.PRODUCT_NAME.get(), contents[0], new_stock, self.CATEGORY.get(),
                self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), self.LOCATION.get(),
                self.date.get(), 'Edit'
            )

            if existing_product:
                self.generate_pdf_report(
                    self.PRODUCT_NAME.get(), existing_product[0], new_stock_existing,
                    self.CATEGORY.get(),
                    self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), new_location,
                    self.date.get(), 'Update'
                )
            else:
                self.generate_pdf_report(
                    self.PRODUCT_NAME.get(), contents[0], amount_to_move,
                    self.CATEGORY.get(),
                    self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), new_location,
                    self.date.get(), 'Move'
                )

        except Exception as e:
            messagebox.showerror('Error', f"An error occurred: {e}")

    def update_record_direct(self):
        try:
            # Validate required fields
            if not self.product_name_entry.get() or not self.stocks_entry.get() or \
                    not self.purchase_price_entry.get() or not self.selling_price_entry.get():
                messagebox.showerror('Fields empty or invalid amount!', "Please fill all missing fields.")
                return

            # Update the product record directly
            self.connector.execute(
                'UPDATE Inventory SET PRODUCT_NAME=LTRIM(RTRIM(?)), STOCKS=?, PURCHASE_PRICE=?, '
                'SELLING_PRICE=? WHERE PRODUCT_REAL_ID=?', (
                    self.product_name_entry.get(), int(self.stocks_entry.get()),
                    self.purchase_price_entry.get(), self.selling_price_entry.get(),
                    self.inventory_tree.item(self.inventory_tree.focus())['values'][0])
            )

            self.connector.commit()

            messagebox.showinfo('Updated successfully',
                        f'The record of {self.product_name_entry.get()} was updated successfully.')

            self.load_inventory_data()
            self.edit_window.destroy()
            self.add_notification()
        except Exception as e:
            messagebox.showerror("Error", f"Inappropriate values. {str(e)}")

    def cancel_update(self):
        self.load_inventory_data()


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

    def generate_pdf_report(self, product_name, product_id, stocks, category, purchase_price, selling_price, location,
                            date, action):
        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(200, 10, f'{action} Product Report', ln=True, align='C')

        # Product details
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, f'Date: {date}', ln=True)
        pdf.cell(200, 10, f'Product Name: {product_name}', ln=True)
        pdf.cell(200, 10, f'Product ID: {product_id}', ln=True)
        pdf.cell(200, 10, f'Stocks: {stocks}', ln=True)
        pdf.cell(200, 10, f'Category: {category}', ln=True)
        pdf.cell(200, 10, f'Purchase Price: {purchase_price}', ln=True)
        pdf.cell(200, 10, f'Selling Price: {selling_price}', ln=True)
        pdf.cell(200, 10, f'Location: {location}', ln=True)

        # Save the PDF with a dynamic name
        pdf_name = f'{action}_Product_{product_id}.pdf'
        pdf.output(pdf_name)

        messagebox.showinfo('PDF Report', f'{action} report generated: {pdf_name}')


if __name__ == "__main__":
    root = ctk.CTk()
    app = InventoryApp(root, "Admin")
    root.mainloop()
