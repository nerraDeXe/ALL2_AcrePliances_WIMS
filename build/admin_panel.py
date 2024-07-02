import datetime
import sqlite3
import matplotlib.pyplot as plt
import customtkinter
from customtkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib import style
from tkcalendar import DateEntry
from tkinter import *
import tkinter.messagebox as mb
import tkinter.ttk as ttk
import sv_ttk
from fpdf import FPDF
import subprocess
import hashlib
from PIL import Image, ImageTk
import sys


class AdminApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect("AcrePliances.db")
        self.cursor = self.connector.cursor()
        self.connector.commit()

        self.root = root
        self.username = username
        self.root.title('ACREPILLANCE')
        self.root.geometry('1600x1000')
        self.root.resizable(0, 0)

        self.setup_variables()
        self.setup_frames()
        self.setup_widgets()
        sv_ttk.set_theme("light")
        self.root.tk.call("source", "azure.tcl")
        self.root.tk.call("set_theme", "light")
        customtkinter.set_appearance_mode("light")
        self.custom_style = ttk.Style()
        self.custom_style.configure('Bold.TButton', font=('Helvetica', 12, 'bold'), background="black")

        self.list_all_inventory()
        self.original_items = {}

    def setup_variables(self):
        self.PRODUCT_NAME = StringVar()
        self.PRODUCT_ID = StringVar()
        self.STOCKS = IntVar()
        self.QUANTITY = IntVar()
        self.PURCHASE_PRICE = DoubleVar()
        self.SELLING_PRICE = DoubleVar()
        self.CATEGORY = StringVar(value='Electronics')
        self.LOCATION = StringVar(value='Warehouse A')
        self.INTERNAL_REFERENCE = StringVar()
        self.AMOUNT_TO_MOVE = IntVar()
        self.NEW_LOCATION = StringVar()
        self.NOTIFICATION_LIST = StringVar()

    def setup_frames(self):

        self.dashboard1_frame = Frame(self.root, bg='#9C0014')
        self.dashboard1_frame.place(relx=0.00, rely=0.00, relwidth=1.00, relheight=0.20)

        self.button_frame = Frame(self.root, bg='#9C0014')
        self.button_frame.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)

        self.button_frame_inventory = Frame(self.root, bg='#9C0014')
        self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.15, relwidth=0.22)
        self.button_frame_inventory.place_forget()

        self.button_frame_users = Frame(self.root, bg='#9C0014')
        self.button_frame_users.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.button_frame_users.place_forget()

        self.table_frame = Frame(self.root)
        self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame.place_forget()

        self.table_frame2 = Frame(self.root)
        self.table_frame2.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame2.place_forget()

        self.table_frame3 = Frame(self.root)
        self.table_frame3.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame3.place_forget()

        self.table_frame4 = Frame(self.root)
        self.table_frame4.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame4.place_forget()

        self.data_entry_frame = Frame(self.root)
        self.data_entry_frame.pack()
        self.data_entry_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)
        self.data_entry_frame.place_forget()

        self.task_assignment_frame = Frame(self.root)
        self.task_assignment_frame.pack()
        self.task_assignment_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.task_assignment_frame.place_forget()

        self.task_assignment_frame2 = Frame(self.root)
        self.task_assignment_frame2.pack()
        self.task_assignment_frame2.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.task_assignment_frame2.place_forget()

        self.chart_frame = Frame(self.root)
        self.chart_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.65)
        self.show_bar_chart()

    def setup_widgets(self):
        self.setup_data_entry_widgets()
        self.setup_move_product_widgets()
        self.setup_button_widgets()
        self.setup_inventory_button_widgets()
        self.setup_table()
        self.setup_user_table()

        self.username_label = Label(self.dashboard1_frame, text=f"Welcome, {self.username}",
                                    font=("Microsoft YaHei UI Light", 15),
                                    bg="#9C0014", fg='white')
        self.username_label.place(x=50, y=50)

    def setup_data_entry_widgets(self):
        # Setup Data Entry Widgets
        self.date_label = ttk.Label(self.data_entry_frame, text='Date (M/DD/YY):', font=('Gill Sans MT', 13))
        self.date_label.place(x=130, y=40)
        self.date = DateEntry(self.data_entry_frame, date=datetime.datetime.now().date(), font=('Gill Sans MT', 13))
        self.date.place(x=300, y=40)

        self.product_name_label = ttk.Label(self.data_entry_frame, text='Product Name:', font=('Gill Sans MT', 13))
        self.product_name_label.place(x=130, y=80)
        self.product_name = ttk.Entry(self.data_entry_frame, font=('Gill Sans MT', 13), width=20,
                                      textvariable=self.PRODUCT_NAME)
        self.product_name.place(x=300, y=80)

        self.location_label = ttk.Label(self.data_entry_frame, text='Location:', font=('Gill Sans MT', 13))
        self.location_label.place(x=130, y=120)
        self.location_menu = ttk.OptionMenu(self.data_entry_frame, self.LOCATION, 'Receiving Area', 'Receiving Area',
                                            'Staging Area', 'Storage Area', 'Shipping Area')
        self.location_menu.place(x=300, y=120)

        self.stocks_label = ttk.Label(self.data_entry_frame, text='Stocks:', font=('Gill Sans MT', 13))
        self.stocks_label.place(x=130, y=160)
        self.stocks = ttk.Entry(self.data_entry_frame, font=('Gill Sans MT', 13), width=20, textvariable=self.STOCKS)
        self.stocks.place(x=300, y=160)

        self.category_label = ttk.Label(self.data_entry_frame, text='Category:', font=('Gill Sans MT', 13))
        self.category_label.place(x=580, y=40)
        self.dd1 = ttk.OptionMenu(self.data_entry_frame, self.CATEGORY, 'Electronics', 'Electronics', 'Appliances',
                                  'Personal Care', 'Homeware', 'Furniture')
        self.dd1.place(x=750, y=35)

        self.purchase_label = ttk.Label(self.data_entry_frame, text='Purchase Price:', font=('Gill Sans MT', 13))
        self.purchase_label.place(x=580, y=120)
        self.purchase = ttk.Entry(self.data_entry_frame, font=('Gill Sans MT', 13), width=20,
                                  textvariable=self.PURCHASE_PRICE)
        self.purchase.place(x=750, y=120)

        self.selling_label = ttk.Label(self.data_entry_frame, text='Selling Price:', font=('Gill Sans MT', 13))
        self.selling_label.place(x=580, y=160)
        self.selling = ttk.Entry(self.data_entry_frame, font=('Gill Sans MT', 13), width=20,
                                 textvariable=self.SELLING_PRICE)
        self.selling.place(x=750, y=160)

        # Hide Data Entry Widgets
        def hide():
            self.date_label.place_forget()
            self.date.place_forget()
            self.product_name_label.place_forget()
            self.product_name.place_forget()
            self.location_label.place_forget()
            self.location_menu.place_forget()
            self.stocks_label.place_forget()
            self.stocks.place_forget()
            self.category_label.place_forget()
            self.dd1.place_forget()
            self.purchase_label.place_forget()
            self.purchase.place_forget()
            self.selling_label.place_forget()
            self.selling.place_forget()
            self.NOTIFICATION_LIST_forget()

        # Make the hide function available
        self.hide_data_entry_widgets = hide

    def setup_move_product_widgets(self):
        # Setup Move Product Widgets
        self.moveamount_label = ttk.Label(self.data_entry_frame, text='Enter Amount to add:', font=('Gill Sans MT', 13))
        self.moveamount_label.place(x=200, y=40)
        self.moveamount = ttk.Entry(self.data_entry_frame, font=('Gill Sans MT', 13), width=70,
                                    textvariable=self.AMOUNT_TO_MOVE)
        self.moveamount.place(x=200, y=70)

        self.newlocation_label = ttk.Label(self.data_entry_frame, text='New Location:', font=('Gill Sans MT', 13))
        self.newlocation_label.place(x=200, y=110)
        self.newlocation = ttk.OptionMenu(self.data_entry_frame, self.NEW_LOCATION, 'Receiving Area', 'Receiving Area',
                                          'Staging Area', 'Storage Area', 'Shipping Area')
        self.newlocation.place(x=200, y=140)

        # Hide Move Product Widgets
        def hide():
            self.moveamount_label.place_forget()
            self.moveamount.place_forget()
            self.newlocation_label.place_forget()
            self.newlocation.place_forget()

        # Make the hide function available
        self.hide_move_product_widgets = hide

    def setup_button_widgets(self):
        CTkButton(self.button_frame, text='User Management', command=self.open_user_management_panel, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22),
                  corner_radius=15, hover_color='orange').place(x=40, y=70, anchor=W)

        CTkButton(self.button_frame, text='Inventory Management', command=self.open_inventory_panel,
                  width=275, height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22),
                  corner_radius=15, hover_color='orange').place(x=40, y=180, anchor=W)

        CTkButton(self.button_frame, text='Purchase Order', command=self.open_purchase_order_panel, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=290, anchor=W)

        CTkButton(self.button_frame, text='Sales Order', command=self.open_sales_order_panel, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=400, anchor=W)

        CTkButton(self.button_frame, text='Vendor Details', command=self.open_vendor_details_panel, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22),
                  corner_radius=15, hover_color='orange').place(x=40, y=510, anchor=W)

        CTkButton(self.button_frame, text='Log out', command=self.restart_login_page,
                  height=30, width=20, border_width=0, fg_color='white', border_color='black',
                  text_color='black').place(x=20, y=630)

    def setup_inventory_button_widgets(self):

        CTkButton(self.button_frame_inventory, text='Delete Inventory', command=self.remove_inventory, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=100, anchor=W)

        CTkButton(self.button_frame_inventory, text='Edit Selected Product', command=self.edit_product_details,
                  width=275, height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=250, anchor=W)

        CTkButton(self.button_frame_inventory, text='Move Product Location', command=self.move_product_location,
                  width=275, height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=400, anchor=W)

        CTkButton(self.button_frame_inventory, text='Back', command=self.close_subpanel, width=90, height=45,
                  border_width=0, fg_color='red', border_color='black', text_color='white',
                  font=('Microsoft YaHei UI Light', 16), corner_radius=15, hover_color='orange'
                  ).place(x=20, y=700, anchor=W)

    def sort_by_column(self, treeview, col, descending):
        # Get the current data in the treeview
        data = [(treeview.set(child, col), child) for child in treeview.get_children("")]

        # Sort data based on the given column
        data.sort(reverse=descending)

        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(data):
            treeview.move(child, "", index)

        # Reverse sort next time
        treeview.heading(col, command=lambda: self.sort_by_column(treeview, col, not descending))

    def setup_table(self):
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)  # Increase row height to 25 pixels

        self.table = ttk.Treeview(self.table_frame, style="Treeview", selectmode='browse',
                                  columns=(
                                      'PRODUCT_REAL_ID', 'DATE', 'PRODUCT_NAME', 'PRODUCT_ID', 'STOCKS', 'CATEGORY',
                                      'PURCHASE_PRICE', 'SELLING_PRICE', 'LOCATION', 'INTERNAL_REFERENCE'))

        X_Scroller = ttk.Scrollbar(self.table, orient='horizontal', command=self.table.xview)
        Y_Scroller = ttk.Scrollbar(self.table, orient='vertical', command=self.table.yview)
        X_Scroller.pack(side='bottom', fill='x')
        Y_Scroller.pack(side='right', fill='y')

        self.table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

        for col in self.table["columns"]:
            self.table.heading(col, text=col.replace('_', ' ').title(), anchor='center',
                               command=lambda _col=col: self.sort_by_column(self.table, _col, False))

        self.table.column('#0', width=0, stretch=NO)
        self.table.column('#1', width=0, stretch=NO)
        self.table.column('#2', width=90, stretch=NO)
        self.table.column('#3', width=90, stretch=NO)
        self.table.column('#4', width=90, stretch=NO)
        self.table.column('#5', width=100, stretch=NO)
        self.table.column('#6', width=135, stretch=NO)
        self.table.column('#7', width=115, stretch=NO)
        self.table.column('#8', width=115, stretch=NO)
        self.table.column('#9', width=125, stretch=NO)
        self.table.column('#10', width=125, stretch=NO)

        self.table.place(relx=0, rely=0, relheight=1, relwidth=1)

    def setup_user_table(self):
        self.user_table = ttk.Treeview(self.table_frame2, selectmode=BROWSE,
                                       columns=('ID', 'Username', 'Role'))

        Y_Scroller = Scrollbar(self.user_table, orient=VERTICAL, command=self.user_table.yview)
        Y_Scroller.pack(side=RIGHT, fill=Y)

        self.user_table.config(yscrollcommand=Y_Scroller.set)

        self.user_table.heading('ID', text='ID', anchor=CENTER)
        self.user_table.heading('Username', text='Username', anchor=CENTER)
        self.user_table.heading('Role', text='Role', anchor=CENTER)

        self.user_table.column('#0', width=0, stretch=NO)
        self.user_table.column('#1', width=50, stretch=NO)
        self.user_table.column('#2', width=200, stretch=NO)
        self.user_table.column('#3', width=150, stretch=NO)

        self.user_table.place(relx=0, rely=0, relheight=1, relwidth=1)

    # Dashboards buttons open
    # def open_inventory_panel(self):
    #     self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
    #     self.button_frame.place_forget()
    #     self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)
    #     self.chart_frame.place_forget()
    #     self.hide_move_product_widgets()

    def close_subpanel(self):
        self.button_frame_users.place_forget()
        self.button_frame.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.button_frame_inventory.place_forget()
        self.table_frame.place_forget()
        self.table_frame2.place_forget()
        self.table_frame3.place_forget()
        self.table_frame4.place_forget()
        self.data_entry_frame.place_forget()
        self.task_assignment_frame.place_forget()
        self.task_assignment_frame2.place_forget()
        self.chart_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)
        self.show_bar_chart()


    def open_inventory_panel(self):
        root.withdraw()
        subprocess.run(["python", "Inventory Management.py"])
        root.deiconify()
    def open_purchase_order_panel(self):
        root.withdraw()
        subprocess.run(["python", "Purchase order.py"])
        root.deiconify()

    def open_vendor_details_panel(self):
        root.withdraw()
        subprocess.run(["python", "Vendor details.py"])
        root.deiconify()

    def open_sales_order_panel(self):
        root.withdraw()
        subprocess.run(["python", "Sales order.py"])
        root.deiconify()

    def open_user_management_panel(self):
        root.withdraw()
        subprocess.run(["python", "User Management.py"])
        root.deiconify()


    def list_all_inventory(self):
        self.table.delete(*self.table.get_children())

        all_data = self.connector.execute('SELECT * FROM Inventory')
        data = all_data.fetchall()

        for values in data:
            self.table.insert('', END, values=values)

    def clear_fields(self):
        today_date = datetime.datetime.now().date()

        self.PRODUCT_NAME.set('PRODUCT NAME')
        self.STOCKS.set(0)
        self.PURCHASE_PRICE.set(0.00)
        self.SELLING_PRICE.set(0.00)
        self.CATEGORY.set('Electronics')
        self.date.set_date(today_date)
        self.table.selection_remove(*self.table.selection())

        ## Notification OG############################################################################################
        self.parent = self.parent
        self.root = Tk()
        self.root.title('Notification')
        self.root.geometry('500x600')

        self.dashboard1_frame = Frame(self.root)
        self.dashboard1_frame.pack()

        self.NOTIFICATION_LIST = Listbox(self.root)
        self.NOTIFICATION_LIST.pack()

        self.delete_notification_button = Button(self.dashboard1_frame,
                                                 text="Delete Notification",
                                                 command=self.delete_notification)
        self.delete_notification_button.pack(pady=10)

        self.display_notifications()

    ####################### CRUD#########################################################################################
    def remove_inventory(self):
        if not self.table.selection():
            mb.showerror('No record selected!', 'Please select a record to delete!')
            return

        current_selected_inventory = self.table.item(self.table.focus())
        values_selected = current_selected_inventory['values']

        surety = mb.askyesno('Are you sure?',
                             f'Are you sure that you want to delete the record of {values_selected[0]}')

        if surety:
            self.connector.execute('DELETE FROM Inventory WHERE PRODUCT_REAL_ID=?', (values_selected[0],))
            self.connector.commit()

            self.list_all_inventory()
            mb.showinfo('Record deleted successfully!', f'The record of {values_selected[0]} was deleted successfully')
            self.add_notification()

    def edit_product_details(self):
        if not self.table.selection():
            mb.showerror('No record selected!', 'Please select a record to edit!')
            return

        current_selected_product = self.table.item(self.table.focus())
        values = current_selected_product['values']

        # Create a new Toplevel window for editing
        self.edit_window = CTkToplevel(self.root)
        self.edit_window.title("Edit Inventory")
        self.edit_window.resizable(False, False)

        # Add a red heading
        CTkLabel(self.edit_window, text="Edit Product", font=('Helvetica', 16, 'bold'), text_color='red').grid(row=0,
                                                                                                               columnspan=2,
                                                                                                               padx=10,
                                                                                                               pady=5)

        # Create and place labels and entries in the new window
        CTkLabel(self.edit_window, text="Product Name:").grid(row=1, column=0, padx=10, pady=5)
        self.product_name_entry = CTkEntry(self.edit_window, width=400)
        self.product_name_entry.grid(row=1, column=1, padx=10, pady=5)
        self.product_name_entry.insert(0, values[2])

        CTkLabel(self.edit_window, text="Stocks:").grid(row=2, column=0, padx=10, pady=5)
        self.stocks_entry = CTkEntry(self.edit_window, width=400)
        self.stocks_entry.grid(row=2, column=1, padx=10, pady=5)
        self.stocks_entry.insert(0, values[4])

        CTkLabel(self.edit_window, text="Category:").grid(row=3, column=0, padx=10, pady=5)
        self.category_var = StringVar(self.edit_window)
        self.category_var.set(values[5])
        self.category_entry = CTkOptionMenu(self.edit_window, variable=self.category_var,
                                            values=['Electronics', 'Appliances', 'Personal Care', 'Homeware',
                                                    'Furniture'])
        self.category_entry.grid(row=3, column=1, padx=10, pady=5)

        CTkLabel(self.edit_window, text="Purchase Price:").grid(row=4, column=0, padx=10, pady=5)
        self.purchase_price_entry = CTkEntry(self.edit_window, width=400)
        self.purchase_price_entry.grid(row=4, column=1, padx=10, pady=5)
        self.purchase_price_entry.insert(0, values[6])

        CTkLabel(self.edit_window, text="Selling Price:").grid(row=5, column=0, padx=10, pady=5)
        self.selling_price_entry = CTkEntry(self.edit_window, width=400)
        self.selling_price_entry.grid(row=5, column=1, padx=10, pady=5)
        self.selling_price_entry.insert(0, values[7])

        CTkLabel(self.edit_window, text="Location:").grid(row=6, column=0, padx=10, pady=5)
        self.location_var = StringVar(self.edit_window)
        self.location_var.set(values[8])
        self.location_entry = CTkOptionMenu(self.edit_window, variable=self.location_var,
                                            values=['Receiving Area', 'Staging Area', 'Storage Area', 'Shipping Area'])
        self.location_entry.grid(row=6, column=1, padx=10, pady=5)

        CTkLabel(self.edit_window, text="Date:").grid(row=7, column=0, padx=10, pady=5)
        self.date_entry = CTkEntry(self.edit_window, width=400)
        self.date_entry.grid(row=7, column=1, padx=10, pady=5)
        self.date_entry.insert(0, values[1])

        # Add buttons for Update and Cancel
        CTkButton(self.edit_window, text='Update Record', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                  command=self.update_record_direct).grid(row=8, column=0, padx=10, pady=10)
        CTkButton(self.edit_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                  command=self.edit_window.destroy).grid(row=8, column=1, padx=10, pady=10)

    def move_product_location(self):
        if not self.table.selection():
            mb.showerror('No record selected!', 'Please select a record to edit!')
            return

        current_selected_product = self.table.item(self.table.focus())
        values = current_selected_product['values']

        # Create a new Toplevel window for moving product location
        self.move_window = CTkToplevel(self.root)
        self.move_window.title("Move Product Location")
        self.move_window.resizable(False, False)  # Lock window resizing
        self.move_window.geometry("450x300")

        # Add a red heading
        CTkLabel(self.move_window, text="Move Product Location", font=('Helvetica', 16, 'bold'), text_color='red').grid(
            row=0, columnspan=2, padx=10, pady=5)

        # Setup Move Product Widgets
        self.moveamount_label = CTkLabel(self.move_window, text='Enter Amount to add:', font=('Gill Sans MT', 13))
        self.moveamount_label.grid(row=1, column=0, padx=10, pady=10)
        self.moveamount = CTkEntry(self.move_window, font=('Gill Sans MT', 13), width=200,
                                   textvariable=self.AMOUNT_TO_MOVE)
        self.moveamount.grid(row=1, column=1, padx=10, pady=10)

        self.newlocation_label = CTkLabel(self.move_window, text='New Location:', font=('Gill Sans MT', 13))
        self.newlocation_label.grid(row=2, column=0, padx=10, pady=10)
        self.newlocation = CTkOptionMenu(self.move_window, variable=self.NEW_LOCATION,
                                         values=['Receiving Area', 'Staging Area', 'Storage Area', 'Shipping Area'])
        self.newlocation.grid(row=2, column=1, padx=10, pady=10)

        # Get the rest of the values
        self.PRODUCT_NAME.set(values[2])
        self.STOCKS.set(values[4])
        self.CATEGORY.set(values[5])
        self.PURCHASE_PRICE.set(values[6])
        self.SELLING_PRICE.set(values[7])
        self.LOCATION.set(values[8])
        self.PRODUCT_ID.set(values[3])
        self.date.set_date(datetime.datetime.strptime(values[1], '%Y-%m-%d'))

        # Add buttons for Move Product and Cancel
        CTkButton(self.move_window, text='Move Product', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                  command=self.update_record).grid(row=3, column=0, padx=10, pady=10)
        CTkButton(self.move_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                  command=self.move_window.destroy).grid(row=3, column=1, padx=10, pady=10)

    def show_add_inventory_window(self):
        # Create a new Toplevel window
        self.add_window = CTkToplevel(self.root)
        self.add_window.title("Add Inventory")
        self.add_window.resizable(False, False)  # Lock the window size

        # Add a red heading
        CTkLabel(self.add_window, text="Add Product", font=('Helvetica', 16, 'bold'), text_color='red').grid(row=0,
                                                                                                             columnspan=2,
                                                                                                             padx=10,
                                                                                                             pady=5)

        # Add data entry widgets to the new window
        CTkLabel(self.add_window, text="Product Name").grid(row=1, column=0, padx=10, pady=5)
        CTkEntry(self.add_window, textvariable=self.PRODUCT_NAME, width=400).grid(row=1, column=1, padx=10, pady=5)

        CTkLabel(self.add_window, text="Stocks").grid(row=2, column=0, padx=10, pady=5)
        CTkEntry(self.add_window, textvariable=self.STOCKS, width=400).grid(row=2, column=1, padx=10, pady=5)

        CTkLabel(self.add_window, text="Category").grid(row=3, column=0, padx=10, pady=5)
        CTkOptionMenu(self.add_window, variable=self.CATEGORY,
                      values=['Electronics', 'Appliances', 'Personal Care', 'Homeware', 'Furniture']).grid(row=3,
                                                                                                           column=1,
                                                                                                           padx=10,
                                                                                                           pady=5)

        CTkLabel(self.add_window, text="Purchase Price").grid(row=4, column=0, padx=10, pady=5)
        CTkEntry(self.add_window, textvariable=self.PURCHASE_PRICE, width=400).grid(row=4, column=1, padx=10,
                                                                                    pady=5)

        CTkLabel(self.add_window, text="Selling Price").grid(row=5, column=0, padx=10, pady=5)
        CTkEntry(self.add_window, textvariable=self.SELLING_PRICE, width=400).grid(row=5, column=1, padx=10, pady=5)

        CTkLabel(self.add_window, text="Location").grid(row=6, column=0, padx=10, pady=5)
        CTkOptionMenu(self.add_window, variable=self.LOCATION,
                      values=['Receiving Area', 'Staging Area', 'Storage Area', 'Shipping Area']).grid(row=6,
                                                                                                       column=1,
                                                                                                       padx=10,
                                                                                                       pady=5)

        CTkLabel(self.add_window, text="Date").grid(row=7, column=0, padx=10, pady=5)
        DateEntry(self.add_window, date=datetime.datetime.now().date(), font=('Gill Sans MT', 13)).grid(row=7, column=1,
                                                                                                        padx=10, pady=5)

        # Add buttons for submitting and cancelling
        CTkButton(self.add_window, text='Add Inventory', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                  command=self.add_inventory).grid(row=8, column=0, padx=10, pady=10)
        CTkButton(self.add_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                  command=self.add_window.destroy).grid(row=8, column=1, padx=10, pady=10)

    def update_record(self):
        current_selected_product = self.table.item(self.table.focus())
        contents = current_selected_product['values']

        try:
            # Get the amount to move and new location
            amount_to_move = int(self.AMOUNT_TO_MOVE.get())
            new_location = self.NEW_LOCATION.get()

            if (
                    not self.date.get() or not self.PRODUCT_NAME.get() or not self.STOCKS.get() or not self.CATEGORY.get() or
                    not self.PURCHASE_PRICE.get() or not self.SELLING_PRICE.get() or not self.LOCATION.get() or not new_location or
                    amount_to_move <= 0):
                mb.showerror('Fields empty or invalid amount!',
                             "Please fill all missing fields and ensure the amount to move is greater than zero.")
                return

            current_stock = int(self.STOCKS.get())

            if amount_to_move > current_stock:
                mb.showerror('Invalid amount', "The amount to move exceeds the current stock.")
                return

            # Deduct stock from the original location
            new_stock = current_stock - amount_to_move
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
                new_stock_existing = existing_product[4] + amount_to_move
                self.connector.execute(
                    'UPDATE Inventory SET STOCKS=? WHERE PRODUCT_ID=?',
                    (new_stock_existing, existing_product[3])
                )
            else:
                location_prefix = new_location[:3].upper()
                new_internal_reference = f"WH-{location_prefix}-{self.PRODUCT_ID.get()}"

                self.connector.execute(
                    'INSERT INTO Inventory (date, PRODUCT_NAME, STOCKS, CATEGORY, PURCHASE_PRICE, SELLING_PRICE, '
                    'LOCATION, INTERNAL_REFERENCE, PRODUCT_ID)'
                    'VALUES (?, LTRIM(RTRIM(?)), ?, ?, ?, ?, ?, ?, ?)', (
                        self.date.get_date(), self.PRODUCT_NAME.get(), amount_to_move, self.CATEGORY.get(),
                        self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), new_location, new_internal_reference,
                        self.PRODUCT_ID.get())
                )

            self.connector.commit()

            mb.showinfo('Updated successfully',
                        f'The record of {self.PRODUCT_NAME.get()} was updated successfully and {amount_to_move} items '
                        f'were moved to {new_location}')

            # self.add_notification()
            self.list_all_inventory()
            self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
            self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
            self.add_btn.place_forget()
            # self.add_btn1.place_forget()
            # self.add_btn2.place_forget()
            # self.add_btn3.place_forget()
            self.setup_data_entry_widgets()
            self.data_entry_frame.pack()
            self.data_entry_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)
            self.hide_move_product_widgets()
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
                    self.PRODUCT_NAME.get(), existing_product[0], amount_to_move,
                    self.CATEGORY.get(),
                    self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), new_location,
                    self.date.get(), 'Move'
                )

            self.clear_fields()

        except Exception as e:
            mb.showerror('Error', f"An error occurred: {e}")

    def update_record_direct(self):
        try:
            # Validate required fields
            if not self.date_entry.get() or not self.product_name_entry.get() or not self.stocks_entry.get() or not self.category_entry.get() or \
                    not self.purchase_price_entry.get() or not self.selling_price_entry.get() or not self.location_entry.get():
                mb.showerror('Fields empty or invalid amount!', "Please fill all missing fields.")
                return

            # Update the product record directly
            self.connector.execute(
                'UPDATE Inventory SET date=?, PRODUCT_NAME=LTRIM(RTRIM(?)), STOCKS=?, CATEGORY=?, PURCHASE_PRICE=?, '
                'SELLING_PRICE=?, LOCATION=? WHERE PRODUCT_REAL_ID=?', (
                    self.date_entry.get(), self.product_name_entry.get(), int(self.stocks_entry.get()),
                    self.category_entry.get(),
                    self.purchase_price_entry.get(), self.selling_price_entry.get(), self.location_entry.get(),
                    self.table.item(self.table.focus())['values'][0])
            )

            self.connector.commit()

            mb.showinfo('Updated successfully',
                        f'The record of {self.product_name_entry.get()} was updated successfully.')
            self.add_notification()
            self.list_all_inventory()
            self.edit_window.destroy()
        except Exception as e:
            mb.showerror("Error", f"Inappropriate values. {str(e)}")

    def cancel_update(self):
        self.list_all_inventory()
        self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.hide_move_product_widgets()
        self.hide_data_entry_widgets()
        self.setup_data_entry_widgets()
        self.clear_fields()

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

        mb.showinfo('PDF Report', f'{action} report generated: {pdf_name}')

    def show_bar_chart(self):
        self.chart_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)

        # Modify SQL query to group by product name and sum stocks
        all_data = self.connector.execute('SELECT PRODUCT_NAME, SUM(STOCKS) FROM Inventory GROUP BY PRODUCT_NAME')
        data = all_data.fetchall()

        if not data:
            mb.showerror('No Data', 'No data available to display!')
            return

        product_names = [item[0] for item in data]
        stocks = [item[1] for item in data]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(product_names, stocks, color='orange')
        ax.set_xlabel('Product Name', color='black')
        ax.set_ylabel('Total Stocks', color='black')
        ax.set_title('Inventory Stocks', color='black')

        # Set the tick positions to match the number of products
        ax.set_xticks(range(len(product_names)))
        # Set the tick labels to the product names
        ax.set_xticklabels(product_names, rotation=45, ha='right', color='black')
        ax.tick_params(axis='y', colors='black')  # Set the color of the y-axis ticks

        plt.tight_layout()

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    def restart_login_page(self):
        root.quit()
        root.destroy()
        subprocess.Popen(["python", "login.py"])


if __name__ == '__main__':
    username = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    root = Tk()
    app = AdminApp(root, username)
    root.mainloop()
