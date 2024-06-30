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
import numpy as np


class AdminApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect("AcrePliances.db")
        self.cursor = self.connector.cursor()

        # self.connector.execute(
        #     'CREATE TABLE IF NOT EXISTS Inventory ('
        #     'PRODUCT_REAL_ID INTEGER PRIMARY KEY, '
        #     'date DATE, '
        #     'PRODUCT_NAME TEXT, '
        #     'PRODUCT_ID TEXT, '
        #     'STOCKS INTEGER, '
        #     'CATEGORY VARCHAR(30), '
        #     'PURCHASE_PRICE FLOAT, '
        #     'SELLING_PRICE FLOAT, '
        #     'LOCATION VARCHAR(30), '
        #     'INTERNAL_REFERENCE VARCHAR(30))'
        # )

        # self.connector.execute('''
        #     CREATE TABLE IF NOT EXISTS users (
        #         USER_REAL_ID INTEGER PRIMARY KEY,
        #         username TEXT NOT NULL UNIQUE,
        #         password TEXT NOT NULL,
        #         role TEXT NOT NULL CHECK(role IN ('Administrator', 'Supervisor', 'Worker'))
        #     )
        # ''')

        self.connector.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_description TEXT NOT NULL
            )
        ''')

        # self.connector.execute('''
        #     CREATE TABLE IF NOT EXISTS Vendors (
        #         VENDOR_ID INTEGER PRIMARY KEY,
        #         NAME VARCHAR(20),
        #         EMAIL VARCHAR(20),
        #         PHONE_NUMBER VARCHAR(10),
        #         COMPANY VARCHAR(20)
        #     )
        # ''')

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
        self.load_users()
        self.load_order_data()
        self.load_vendor_data()
        self.load_vendor_data1()
        self.show_dashboard()
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
        self.dashboard1_frame = CTkFrame(self.root, bg_color='grey', border_color='white', fg_color='#9C0014')
        self.dashboard1_frame.place(relx=0.00, rely=0.00, relwidth=1.00, relheight=0.20)

        self.button_frame = CTkFrame(self.root, bg_color='#9C0014', border_color='white', fg_color='#9C0014')
        self.button_frame.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)

        self.button_frame_inventory = CTkFrame(self.root, bg_color='#9C0014', border_color='white', fg_color='#9C0014')
        self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.15, relwidth=0.22)
        self.button_frame_inventory.place_forget()

        self.button_frame_users = CTkFrame(self.root, bg_color='#9C0014', border_color='white', fg_color='#9C0014')
        self.button_frame_users.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.button_frame_users.place_forget()

        self.button_frame_purchase = CTkFrame(self.root, bg_color='#9C0014', border_color='white', fg_color='#9C0014')
        self.button_frame_purchase.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.button_frame_purchase.place_forget()

        self.button_frame_sales = CTkFrame(self.root, bg_color='#9C0014', border_color='white', fg_color='#9C0014')
        self.button_frame_sales.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.button_frame_sales.place_forget()

        self.button_frame_vendor = CTkFrame(self.root, bg_color='#9C0014', border_color='white', fg_color='#9C0014')
        self.button_frame_vendor.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.button_frame_vendor.place_forget()

        self.table_frame = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame.place_forget()

        self.table_frame2 = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.table_frame2.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame2.place_forget()

        self.table_frame3 = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.table_frame3.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame3.place_forget()

        self.table_frame4 = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.table_frame4.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame4.place_forget()

        self.table_frame5 = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.table_frame5.place(relx=0.17, rely=0.20, relwidth=0.78, relheight=0.30)
        self.table_frame5.place_forget()

        self.table_frame6 = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.table_frame6.place(relx=0.17, rely=0.20, relwidth=0.78, relheight=0.30)
        self.table_frame6.place_forget()

        self.table_frame7 = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.table_frame7.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.30)
        self.table_frame7.place_forget()

        self.table_frame8 = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.table_frame8.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.30)
        self.table_frame8.place_forget()

        self.table_frame9 = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.table_frame9.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.table_frame9.place_forget()

        self.data_entry_frame = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.data_entry_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)
        self.data_entry_frame.place_forget()

        self.inventory_stats_frame = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.inventory_stats_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)
        self.inventory_stats_frame.place_forget()

        self.order_stats_frame = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.order_stats_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.20)
        self.order_stats_frame.place_forget()

        self.task_assignment_frame = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.task_assignment_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.task_assignment_frame.place_forget()

        self.task_assignment_frame2 = CTkFrame(self.root, border_color='white', fg_color='#9C0014')
        self.task_assignment_frame2.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.task_assignment_frame2.place_forget()

        self.purchase_order_frame = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.purchase_order_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.purchase_order_frame.place_forget()

        self.sales_order_frame = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.sales_order_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.sales_order_frame.place_forget()

        self.vendor_frame = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.vendor_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.vendor_frame.place_forget()

        self.chart_frame = CTkFrame(self.root, border_color='white', fg_color='orange')
        self.chart_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.80)


    def setup_widgets(self):
        self.setup_data_entry_widgets()
        self.setup_move_product_widgets()
        self.setup_button_widgets()
        self.setup_inventory_button_widgets()
        self.setup_table()
        self.setup_user_management_widgets()
        self.setup_user_table()
        self.setup_purchase_order_buttons()
        self.setup_purchase_order_table()
        self.setup_sales_order_buttons()
        self.setup_sales_order_table()
        self.setup_vendor_buttons()
        self.setup_vendor_table()

        self.username_label = Label(self.dashboard1_frame, text=f"Welcome, {self.username}",
                                    font=("Microsoft YaHei UI Light", 15),
                                    bg="#9C0014", fg='white')
        self.username_label.place(x=50, y=50)

    def setup_data_entry_widgets(self):
        # Setup Data Entry Widgets
        self.date_label = ttk.Label(self.data_entry_frame, text='Date (M/DD/YY):', font=('Gill Sans MT', 13))
        self.date_label.place(x=130, y=40)
        self.date = DateEntry(self.data_entry_frame, date=datetime.datetime.now().date(), font=('Gill Sans MT', 13), date_pattern='yyyy-mm-dd')
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

        CTkButton(self.button_frame, text='Vendor', command=self.open_vendor_panel, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=510, anchor=W)

        # CTkButton(self.button_frame, text='Vendor Details', command=self.open_vendor_details_panel, width=275,
        #           height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
        #           font=('Microsoft YaHei UI Light', 22),
        #           corner_radius=15, hover_color='orange').place(x=40, y=510, anchor=W)

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

    def setup_user_management_widgets(self):
        CTkButton(self.button_frame_users, text='Add User', command=self.add_user, width=275, height=80,
                  border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=100)

        CTkButton(self.button_frame_users, text='Delete User', command=self.delete_user, width=275, height=80,
                  border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22),
                  corner_radius=15, hover_color='orange').place(x=40, y=280)

        CTkButton(self.button_frame_users, text='Back', command=self.close_subpanel, width=90, height=45,
                  border_width=0, fg_color='red', border_color='black', text_color='white',
                  font=('Microsoft YaHei UI Light', 16),
                  corner_radius=15, hover_color='orange').place(x=20, y=700)

    def setup_purchase_order_buttons(self):
        CTkButton(self.button_frame_purchase, text='Add Purchase Order', command=self.create_purchase_order_window,
                  width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22),
                  corner_radius=15, hover_color='orange').place(x=40, y=70, anchor=W)

        CTkButton(self.button_frame_purchase, text='Edit Purchase Order', command=self.edit_order_window,
                  width=275, height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22),
                  corner_radius=15, hover_color='orange').place(x=40, y=180, anchor=W)

        CTkButton(self.button_frame_purchase, text='Delete Purchase Order', command=self.delete_order, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=290, anchor=W)

        CTkButton(self.button_frame_purchase, text='Complete Order', command=self.complete_order_window, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=400, anchor=W)

        CTkButton(self.button_frame_purchase, text='Back', command=self.close_subpanel, width=90, height=45,
                  border_width=0, fg_color='red', border_color='black', text_color='white',
                  font=('Microsoft YaHei UI Light', 16), corner_radius=15, hover_color='orange'
                  ).place(x=20, y=700, anchor=W)

    def setup_sales_order_buttons(self):
        CTkButton(self.button_frame_sales, text='Add Sales Order', command=self.create_sales_order_window,
                      width=275,
                      height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                      font=('Microsoft YaHei UI Light', 22),
                      corner_radius=15, hover_color='orange').place(x=40, y=70, anchor=W)

        CTkButton(self.button_frame_sales, text='Edit Sales Order', command=self.edit_order_window,
                      width=275, height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                      font=('Microsoft YaHei UI Light', 22),
                      corner_radius=15, hover_color='orange').place(x=40, y=180, anchor=W)

        CTkButton(self.button_frame_sales, text='Delete Sales Order', command=self.delete_order, width=275,
                      height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                      font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                      ).place(x=40, y=290, anchor=W)

        CTkButton(self.button_frame_sales, text='Complete Order', command=self.complete_sales_order, width=275,
                      height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                      font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                      ).place(x=40, y=400, anchor=W)

        CTkButton(self.button_frame_sales, text='Back', command=self.close_subpanel, width=90, height=45,
                      border_width=0, fg_color='red', border_color='black', text_color='white',
                      font=('Microsoft YaHei UI Light', 16), corner_radius=15, hover_color='orange'
                      ).place(x=20, y=700, anchor=W)

    def setup_vendor_buttons(self):
        CTkButton(self.button_frame_vendor, text='Add Vendor', command=self.create_vendor_window,
                  width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22),
                  corner_radius=15, hover_color='orange').place(x=40, y=70, anchor=W)

        CTkButton(self.button_frame_vendor, text='Edit Vendor', command=self.edit_vendor_window,
                  width=275, height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22),
                  corner_radius=15, hover_color='orange').place(x=40, y=180, anchor=W)

        CTkButton(self.button_frame_vendor, text='Delete Vendor', command=self.delete_vendor, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=40, y=290, anchor=W)

        CTkButton(self.button_frame_vendor, text='Back', command=self.close_subpanel, width=90, height=45,
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

    def setup_purchase_order_table(self):
        order_details_label = CTkLabel(self.table_frame5, text="Purchase Order Details:",
                                       font=("Helvetica", 20, 'bold'),
                                       text_color='black')
        order_details_label.pack(anchor=W, pady=10)

        self.order_table = ttk.Treeview(self.table_frame5, columns=(
            "ID", "Product Name", "Product ID", "Category", "Quantity", "Vendor ID", "Date"), show='headings')
        self.order_table.heading("ID", text="ID")
        self.order_table.heading("Product Name", text="Product Name")
        self.order_table.heading("Product ID", text="Product ID")
        self.order_table.heading("Category", text="Category")
        self.order_table.heading("Quantity", text="Quantity")
        self.order_table.heading("Vendor ID", text="Vendor ID")
        self.order_table.heading("Date", text="Date")

        self.order_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

        vendor_details_label = CTkLabel(self.table_frame6, text="Vendor Details:", font=("Helvetica", 20, 'bold'),
                                        text_color='black')
        vendor_details_label.pack(anchor=W, pady=10)

        self.vendor_table = ttk.Treeview(self.table_frame6, columns=("ID", "Name", "Email", "Phone", "Company"),
                                         show='headings')
        self.vendor_table.heading("ID", text="ID")
        self.vendor_table.heading("Name", text="Name")
        self.vendor_table.heading("Email", text="Email")
        self.vendor_table.heading("Phone", text="Phone")
        self.vendor_table.heading("Company", text="Company")
        self.vendor_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def setup_sales_order_table(self):
        # Sales Order Details Label
        sales_order_details_label = CTkLabel(self.table_frame7, text="Sales Order Details:",
                                             font=("Helvetica", 20, 'bold'),
                                             text_color='black')
        sales_order_details_label.pack(anchor=W, pady=10)

        # Sales Order Table
        self.sales_order_table = ttk.Treeview(self.table_frame7, columns=(
            "ID", "Product Name", "Product ID", "Category", "Quantity", "Date", "Store Branch"), show='headings')
        self.sales_order_table.heading("ID", text="ID")
        self.sales_order_table.heading("Product Name", text="Product Name")
        self.sales_order_table.heading("Product ID", text="Product ID")
        self.sales_order_table.heading("Category", text="Category")
        self.sales_order_table.heading("Quantity", text="Quantity")
        self.sales_order_table.heading("Date", text="Date")
        self.sales_order_table.heading("Store Branch", text="Store Branch")
        self.sales_order_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Inventory Details Label
        inventory_details_label = CTkLabel(self.table_frame8, text="Inventory Details:",
                                           font=("Helvetica", 20, 'bold'),
                                           text_color='black')
        inventory_details_label.pack(anchor=W, pady=10)

        # Inventory Table
        self.inventory_table = ttk.Treeview(self.table_frame8, columns=(
            "PRODUCT_REAL_ID", "DATE", "PRODUCT_NAME", "PRODUCT_ID", "STOCKS", "CATEGORY",
            "PURCHASE_PRICE", "SELLING_PRICE", "LOCATION", "INTERNAL_REFERENCE"), show='headings')
        self.inventory_table.heading("PRODUCT_REAL_ID", text="Product Real ID")
        self.inventory_table.heading("DATE", text="Date")
        self.inventory_table.heading("PRODUCT_NAME", text="Product Name")
        self.inventory_table.heading("PRODUCT_ID", text="Product ID")
        self.inventory_table.heading("STOCKS", text="Stocks")
        self.inventory_table.heading("CATEGORY", text="Category")
        self.inventory_table.heading("PURCHASE_PRICE", text="Purchase Price")
        self.inventory_table.heading("SELLING_PRICE", text="Selling Price")
        self.inventory_table.heading("LOCATION", text="Location")
        self.inventory_table.heading("INTERNAL_REFERENCE", text="Internal Reference")

        # Hide the PRODUCT_REAL_ID column
        self.inventory_table.column("PRODUCT_REAL_ID", width=0, stretch=NO)

        self.inventory_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def setup_vendor_table(self):
        vendor_details_label1 = CTkLabel(self.table_frame9, text="Vendor Details:", font=("Helvetica", 20, 'bold'),
                                        text_color='black')
        vendor_details_label1.pack(anchor=W, pady=10)

        self.vendor_table1 = ttk.Treeview(self.table_frame9, columns=("ID", "Name", "Email", "Phone", "Company"),
                                         show='headings')
        self.vendor_table1.heading("ID", text="ID")
        self.vendor_table1.heading("Name", text="Name")
        self.vendor_table1.heading("Email", text="Email")
        self.vendor_table1.heading("Phone", text="Phone")
        self.vendor_table1.heading("Company", text="Company")
        self.vendor_table1.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Dashboards buttons open
    def open_inventory_panel(self):
        self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.button_frame.place_forget()
        self.inventory_stats_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)
        self.show_inventory_stats()
        self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)
        self.chart_frame.place_forget()
        self.hide_move_product_widgets()
        self.list_all_inventory()
        self.show_inventory_stats()

    def close_subpanel(self):
        self.button_frame_users.place_forget()
        self.button_frame.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.button_frame_inventory.place_forget()
        # self.button_frame_tasks.place_forget()
        # self.button_frame_tasks2.place_forget()
        self.button_frame_purchase.place_forget()
        self.button_frame_sales.place_forget()
        self.button_frame_vendor.place_forget()
        self.table_frame.place_forget()
        self.table_frame2.place_forget()
        self.table_frame3.place_forget()
        self.table_frame4.place_forget()
        self.table_frame5.place_forget()
        self.table_frame6.place_forget()
        self.table_frame7.place_forget()
        self.table_frame8.place_forget()
        self.table_frame9.place_forget()
        self.data_entry_frame.place_forget()
        self.task_assignment_frame.place_forget()
        self.task_assignment_frame2.place_forget()
        self.inventory_stats_frame.place_forget()
        self.order_stats_frame.place_forget()
        self.chart_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.80)
        self.show_dashboard()

    # def open_purchase_order_panel(self):
    #     subprocess.run(["python", "Purchase order.py"])
    #
    # def open_vendor_details_panel(self):
    #     subprocess.run(["python", "Vendor details.py"])

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

    def display_notifications(self):
        try:
            self.cursor.execute("SELECT * FROM notifications")
            records = self.cursor.fetchall()

            self.NOTIFICATION_LIST.delete(0, END)
            for record in records:
                self.NOTIFICATION_LIST.insert(END, record[1])
        except sqlite3.Error as e:
            print("Error fetching notifications:", e)

    # def add_notification(self):
    #     new_notification = "New Notification"
    #     self.cursor.execute("INSERT INTO notifications (notification_description) "
    #                         "VALUES (?)", (new_notification,))
    #     self.connector.commit()
    #     self.display_notifications()

    def delete_notification(self):
        selected_index = self.NOTIFICATION_LIST.curselection()
        if not selected_index:
            mb.showerror('No notification selected!', 'Please select a notification to delete!')
            return

        notification_id = selected_index[0] + 1  # Adjust index since SQLite starts from 1
        self.cursor.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        self.connector.commit()
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
            # self.add_notification()

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
        today_date = datetime.datetime.now().date()


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
        self.date.set_date(today_date)

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
        DateEntry(self.add_window, date=datetime.datetime.now().date(), font=('Gill Sans MT', 13), date_pattern='yyyy-mm-dd').grid(row=7, column=1,
                                                                                                        padx=10, pady=5)

        # Add buttons for submitting and cancelling
        CTkButton(self.add_window, text='Add Inventory', font=('Helvetica', 13, 'bold'), fg_color='SpringGreen4',
                  command=self.add_inventory).grid(row=8, column=0, padx=10, pady=10)
        CTkButton(self.add_window, text='Cancel', font=('Helvetica', 13, 'bold'), fg_color='red',
                  command=self.add_window.destroy).grid(row=8, column=1, padx=10, pady=10)

    def update_record(self):
        global new_stock_existing
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
            existing_product = self.cursor.execute(
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
            self.move_window.destroy()
            self.show_inventory_stats()

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
            mb.showerror("Error", f"Inappropriate values. {str(e)}")

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
            # self.add_notification()
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

    # User Management panel
    def open_user_management_panel(self):
        self.button_frame.place_forget()
        self.chart_frame.place_forget()
        self.button_frame_users.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.table_frame2.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)

    #  User Management (Add new user) update the code
    def add_user(self):
        add_user_window = CTkToplevel(self.root)
        add_user_window.title("Add User")
        add_user_window.geometry("400x300")
        add_user_window.resizable(False, False)

        username_var = StringVar()
        password_var = StringVar()
        role_var = StringVar()
        show_password_var = BooleanVar(value=False)

        CTkLabel(add_user_window, text="Username").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        CTkEntry(add_user_window, textvariable=username_var).grid(row=0, column=1, padx=10, pady=5)

        CTkLabel(add_user_window, text="Password").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        password_entry = CTkEntry(add_user_window, textvariable=password_var, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        # Load images using PIL and then convert them to CTkImage
        show_icon_img = Image.open("show_password.png")  # Path to your "show password" icon
        hide_icon_img = Image.open("hide_password.png")  # Path to your "hide password" icon

        self.show_icon = CTkImage(show_icon_img)
        self.hide_icon = CTkImage(hide_icon_img)

        def toggle_password():
            if show_password_var.get():
                password_entry.configure(show="")
                user_toggle_button.configure(image=self.hide_icon)
            else:
                password_entry.configure(show="*")
                user_toggle_button.configure(image=self.show_icon)
            show_password_var.set(not show_password_var.get())

        user_toggle_button = CTkButton(add_user_window, image=self.show_icon, command=toggle_password, text='')
        user_toggle_button.grid(row=1, column=2, padx=10, pady=5)

        CTkLabel(add_user_window, text="Role:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        CTkOptionMenu(add_user_window, variable=role_var, values=['Supervisor', 'Worker']).grid(row=2, column=1,
                                                                                                    padx=10, pady=5)

        def save_user():
            username = username_var.get()
            password = password_var.get()
            role = role_var.get()
            if username and password and role:
                try:
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    conn = sqlite3.connect('AcrePliances.db')
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                                   (username, hashed_password, role))
                    conn.commit()
                    mb.showinfo('User added', 'The user was successfully added')
                    self.load_users()
                    # self.add_notification()
                except sqlite3.Error as e:
                    mb.showerror('Database Error', f'Error: {e}')
                finally:
                    conn.close()
                add_user_window.destroy()
            else:
                mb.showerror('Error', 'All fields are required')

        Button(add_user_window, text="Save", command=save_user).grid(row=3, column=1, padx=10, pady=15)

    def load_users(self):
        self.user_table.delete(*self.user_table.get_children())
        try:
            conn = sqlite3.connect('AcrePliances.db')
            cursor = conn.cursor()
            cursor.execute('SELECT USER_REAL_ID, username, role FROM users')
            users = cursor.fetchall()
            for user in users:
                self.user_table.insert('', END, values=user)
        except sqlite3.Error as e:
            mb.showerror('Database Error', f'Error: {e}')
        finally:
            conn.close()

    def new_user_toggle_password(self, password_entry, show_password_var, toggle_button):
        if show_password_var.get():
            password_entry.config(show='*')
            toggle_button.config(image=self.show_icon)
        else:
            password_entry.config(show='')
            toggle_button.config(image=self.hide_icon)
        show_password_var.set(not show_password_var.get())

    ########################################################################################################################

    # Delete user from the WIMS
    def delete_user(self):
        selected_item = self.user_table.selection()
        if not selected_item:
            mb.showerror('No user selected!', 'Please select a user to delete')
        else:
            current_item = self.user_table.focus()
            contents = self.user_table.item(current_item)
            selected_user = contents['values']

            confirm = mb.askyesno('Delete user?', f'Are you sure you want to delete user {selected_user[1]}?',
                                  icon='warning')
            if confirm:
                conn = sqlite3.connect('AcrePliances.db')
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE USER_REAL_ID = ?', (selected_user[0],))
                conn.commit()
                conn.close()

                self.user_table.delete(current_item)
                mb.showinfo('User deleted', 'The selected user was successfully deleted')
                # self.add_notification()

    # Function that open the task window
    def open_task_panel(self):
        self.button_frame.place_forget()
        self.chart_frame.place_forget()
        self.table_frame3.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)
        self.button_frame_tasks.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.task_assignment_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.load_tasks()

    def open_task2_panel(self):
        self.button_frame.place_forget()
        self.chart_frame.place_forget()
        self.table_frame4.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)
        self.button_frame_tasks2.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.task_assignment_frame2.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.load_tasks2()

    def load_tasks(self):
        self.task_table.delete(*self.task_table.get_children())
        conn = sqlite3.connect('AcrePliances.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, task, assigned_to, status FROM tasks')
        tasks = cursor.fetchall()
        conn.close()

        for task in tasks:
            self.task_table.insert("", "end", values=(task[0], task[1], task[2], task[3]), iid=task[0])

    def load_tasks2(self):
        for i in self.task2_table.get_children():
            self.task2_table.delete(i)

        conn = sqlite3.connect('AcrePliances.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, task, status FROM tasks WHERE assigned_to=?", (self.username,))
        for task in cursor.fetchall():
            self.task2_table.insert("", "end", values=(task[0], task[1], task[2]), iid=task[0])
        conn.close()

    def update_status(self):
        selected_item = self.task2_table.focus()
        new_status = self.status_var.get()

        if selected_item:
            print(f"Selected Item: {selected_item}, New Status: {new_status}")
            if new_status:
                try:
                    conn = sqlite3.connect('AcrePliances.db')
                    cursor = conn.cursor()
                    cursor.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, selected_item))
                    conn.commit()
                    conn.close()
                    self.load_tasks2()
                except sqlite3.Error as e:
                    mb.showerror("Database Error", f"Error updating task status: {e}")
            else:
                mb.showwarning("Input Error", "Please select a status to update.")
        else:
            mb.showwarning("Selection Error", "Please select a task to update.")

    def assign_task(self):
        task = self.task_entry.get()
        worker = self.worker_entry.get()
        if not task or not worker:
            mb.showerror("Error", "Please fill in all fields")
            return

        conn = sqlite3.connect('AcrePliances.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task, assigned_to, status) VALUES (?, ?, ?)", (task, worker, "Incomplete"))
        conn.commit()
        conn.close()
        self.load_tasks()

    # Purchase Order

    def open_purchase_order_panel(self):
        self.button_frame_purchase.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.button_frame.place_forget()
        self.table_frame5.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.30)
        self.table_frame6.place(relx=0.22, rely=0.53, relwidth=0.78, relheight=0.20)
        self.order_stats_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)
        self.show_order_stats()
        self.chart_frame.place_forget()
        self.load_vendor_data()

    def load_order_data(self):
        self.order_table.delete(*self.order_table.get_children())

        self.cursor.execute('SELECT * FROM Orders')
        rows = self.cursor.fetchall()

        for row in rows:
            self.order_table.insert('', 'end', values=row)

    def create_purchase_order_window(self):
        self.extra_window = CTkToplevel(self.root)
        self.extra_window.title('Add Sales Order')
        self.extra_window.geometry('600x600')
        title_label = CTkLabel(self.extra_window, text="ADD NEW SALES ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)

        # Product Name
        name_frame = CTkFrame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=X)
        name_label = CTkLabel(name_frame, text="Product Name:")
        name_label.pack(side=LEFT)
        self.name_entry = CTkEntry(name_frame)
        self.name_entry.pack(side=RIGHT, fill=X, expand=True)

        # Category
        category_frame = CTkFrame(self.extra_window)
        category_frame.pack(pady=5, padx=10, fill=X)
        category_label = CTkLabel(category_frame, text="Category:")
        category_label.pack(side=LEFT)
        self.category_var = StringVar()
        self.category_menu = ttk.Combobox(category_frame, textvariable=self.category_var,
                                          values=["Electronics", "Appliances", "Personal Care", "Homeware",
                                                  "Furniture"])
        self.category_menu.pack(side=RIGHT, fill=X, expand=True)

        # Quantity
        quantity_frame = CTkFrame(self.extra_window)
        quantity_frame.pack(pady=5, padx=10, fill=X)
        quantity_label = CTkLabel(quantity_frame, text="Quantity:")
        quantity_label.pack(side=LEFT)
        self.quantity_entry = CTkEntry(quantity_frame)
        self.quantity_entry.pack(side=RIGHT, fill=X, expand=True)

        # Vendor ID
        vendor_id_frame = CTkFrame(self.extra_window)
        vendor_id_frame.pack(pady=5, padx=10, fill=X)
        vendor_id_label = CTkLabel(vendor_id_frame, text="Vendor ID:")
        vendor_id_label.pack(side=LEFT)
        self.vendor_id_var = StringVar()
        self.vendor_id_menu = ttk.Combobox(vendor_id_frame, textvariable=self.vendor_id_var)
        self.vendor_id_menu.pack(side=RIGHT, fill=X, expand=True)
        self.load_vendor_ids()

        # Date
        date_frame1 = CTkFrame(self.extra_window)
        date_frame1.pack(pady=5, padx=10, fill=X)
        date_label = CTkLabel(date_frame1, text="Date:")
        date_label.pack(side=LEFT)
        self.date = DateEntry(date_frame1, date=datetime.datetime.now().date(), font=('Gill Sans MT', 13), date_pattern='yyyy-mm-dd')
        self.date.pack(side=RIGHT, fill=X, expand=True)

        add_button = CTkButton(self.extra_window, text="Add Order", command=self.add_order)
        add_button.pack(pady=10)

        clear_button = CTkButton(self.extra_window, text="Clear", command=self.clear_order_entries)
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
        date = self.date.get()

        if product_name and category and quantity and vendor_id:
            product_id = self.generate_product_id(category)
            self.cursor.execute(
                'INSERT INTO Orders (PRODUCT_NAME, PRODUCT_ID, CATEGORY, QUANTITY, DATE, VENDOR_ID) VALUES (?, ?, ?, ?, ?, ?)',
                (product_name, product_id, category, quantity, date, vendor_id)
            )
            self.connector.commit()
            self.load_order_data()
            mb.showinfo('Success', 'Order added successfully!')
            self.extra_window.destroy()
        else:
            mb.showwarning('Error', 'Please fill in all fields.')

    def generate_product_id(self, category):
        self.cursor.execute('SELECT COUNT(*) FROM Orders WHERE CATEGORY=?', (category,))
        count = self.cursor.fetchone()[0]
        product_id = f"{category[0].upper()}{count + 1:03d}"
        return product_id

    def edit_order_window(self):
        selected_item = self.order_table.selection()
        if not selected_item:
            mb.showwarning('Error', 'Please select an order to edit.')
            return

        order_id = self.order_table.item(selected_item)['values'][0]
        self.extra_window = CTkToplevel(self.root)
        self.extra_window.title('Edit Sales Order')
        self.extra_window.geometry('600x600')

        title_label = CTkLabel(self.extra_window, text="EDIT SALES ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)

        self.cursor.execute('SELECT * FROM Orders WHERE ORDER_ID=?', (order_id,))
        order = self.cursor.fetchone()

        self.edit_order_id = order[0]

        # Product Name
        name_frame = CTkFrame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=X)
        name_label = CTkLabel(name_frame, text="Product Name:")
        name_label.pack(side=LEFT)
        self.name_entry = CTkEntry(name_frame)
        self.name_entry.insert(0, order[1])
        self.name_entry.pack(side=RIGHT, fill=X, expand=True)

        # Category
        category_frame = CTkFrame(self.extra_window)
        category_frame.pack(pady=5, padx=10, fill=X)
        category_label = CTkLabel(category_frame, text="Category:")
        category_label.pack(side=LEFT)
        self.category_var = StringVar()
        self.category_menu = ttk.Combobox(category_frame, textvariable=self.category_var,
                                          values=["Electronics", "Appliances", "Personal Care", "Homeware",
                                                  "Furniture"])
        self.category_menu.set(order[3])
        self.category_menu.pack(side=RIGHT, fill=X, expand=True)

        # Quantity
        quantity_frame = CTkFrame(self.extra_window)
        quantity_frame.pack(pady=5, padx=10, fill=X)
        quantity_label = CTkLabel(quantity_frame, text="Quantity:")
        quantity_label.pack(side=LEFT)
        self.quantity_entry = CTkEntry(quantity_frame)
        self.quantity_entry.insert(0, order[4])
        self.quantity_entry.pack(side=RIGHT, fill=X, expand=True)

        # Vendor ID
        vendor_id_frame = CTkFrame(self.extra_window)
        vendor_id_frame.pack(pady=5, padx=10, fill=X)
        vendor_id_label = CTkLabel(vendor_id_frame, text="Vendor ID:")
        vendor_id_label.pack(side=LEFT)
        self.vendor_id_var = StringVar()
        self.vendor_id_menu = ttk.Combobox(vendor_id_frame, textvariable=self.vendor_id_var)
        self.vendor_id_menu.pack(side=RIGHT, fill=X, expand=True)
        self.load_vendor_ids()
        self.vendor_id_menu.set(order[5])

        save_button = CTkButton(self.extra_window, text="Save Changes", command=self.save_order_changes)
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
            mb.showinfo('Success', 'Order updated successfully!')
            self.extra_window.destroy()
        else:
            mb.showwarning('Error', 'Please fill in all fields.')

    def delete_order(self):
        selected_item = self.order_table.selection()
        if not selected_item:
            mb.showwarning('Error', 'Please select an order to delete.')
            return

        confirm = mb.askyesno('Confirm Delete', 'Are you sure you want to delete the selected order?')
        if not confirm:
            return

        order_id = self.order_table.item(selected_item)['values'][0]
        self.cursor.execute('DELETE FROM Orders WHERE ORDER_ID=?', (order_id,))
        self.connector.commit()
        self.load_order_data()
        mb.showinfo('Success', 'Order deleted successfully!')

    def load_vendor_data(self):
        self.vendor_table.delete(*self.vendor_table.get_children())

        self.cursor.execute('SELECT * FROM Vendors')
        rows = self.cursor.fetchall()

        for row in rows:
            self.vendor_table.insert('', 'end', values=row)

    def clear_order_entries(self):
        self.name_entry.delete(0, END)
        self.category_menu.set('')
        self.quantity_entry.delete(0, END)
        self.vendor_id_menu.set('')

    def complete_order_window(self):
        selected_item = self.order_table.selection()
        if not selected_item:
            mb.showwarning('Error', 'Please select an order to complete.')
            return

        order_id = self.order_table.item(selected_item)['values'][0]
        self.extra_window = CTkToplevel(self.root)
        self.extra_window.title('Complete Order')
        self.extra_window.geometry('600x600')

        title_label = CTkLabel(self.extra_window, text="COMPLETE ORDER", font=("Helvetica", 14))
        title_label.pack(pady=20)

        self.cursor.execute('SELECT * FROM Orders WHERE ORDER_ID=?', (order_id,))
        order = self.cursor.fetchone()

        self.complete_order_id = order[0]

        # Date
        date_frame = CTkFrame(self.extra_window)
        date_frame.pack(pady=5, padx=10, fill=X)
        date_label = CTkLabel(date_frame, text="Date:")
        date_label.pack(side=LEFT)
        self.date_entry = DateEntry(date_frame, date=datetime.datetime.now().date(), font=('Gill Sans MT', 13), date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side=RIGHT, fill=X, expand=True)

        # Purchase Price
        purchase_price_frame = CTkFrame(self.extra_window)
        purchase_price_frame.pack(pady=5, padx=10, fill=X)
        purchase_price_label = CTkLabel(purchase_price_frame, text="Purchase Price:")
        purchase_price_label.pack(side=LEFT)
        self.purchase_price_entry = CTkEntry(purchase_price_frame)
        self.purchase_price_entry.pack(side=RIGHT, fill=X, expand=True)

        # Selling Price
        selling_price_frame = CTkFrame(self.extra_window)
        selling_price_frame.pack(pady=5, padx=10, fill=X)
        selling_price_label = CTkLabel(selling_price_frame, text="Selling Price:")
        selling_price_label.pack(side=LEFT)
        self.selling_price_entry = CTkEntry(selling_price_frame)
        self.selling_price_entry.pack(side=RIGHT, fill=X, expand=True)

        complete_button = CTkButton(self.extra_window, text="Complete Order", command=self.complete_order)
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
            mb.showwarning('Error', 'Please enter valid prices.')
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

        self.connector.execute(
            'INSERT INTO Inventory (date, PRODUCT_NAME, PRODUCT_ID, STOCKS, CATEGORY, PURCHASE_PRICE, SELLING_PRICE, '
            'LOCATION, INTERNAL_REFERENCE)'
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (date, product_name, product_id, quantity, category, purchase_price, selling_price, location,
             internal_reference)
        )
        self.connector.commit()

        self.cursor.execute('DELETE FROM Orders WHERE ORDER_ID=?', (order_id,))
        self.connector.commit()
        self.load_order_data()
        mb.showinfo('Success', 'Order completed and transferred successfully!')
        self.extra_window.destroy()

    # Sales Order

    def open_sales_order_panel(self):
        self.button_frame_sales.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.button_frame.place_forget()
        self.table_frame7.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.30)
        self.table_frame8.place(relx=0.22, rely=0.53, relwidth=0.78, relheight=0.20)
        self.chart_frame.place_forget()
        self.load_sales_order_data()
        self.load_inventory_data()
        self.order_stats_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)
        self.show_order_stats()

    def load_sales_order_data(self):
        self.sales_order_table.delete(*self.sales_order_table.get_children())

        self.cursor.execute('SELECT * FROM Sales_Orders')
        rows = self.cursor.fetchall()

        for row in rows:
            self.sales_order_table.insert('', 'end', values=row)

    # def create_sales_order_window(self):
    #     self.extra_window = CTkToplevel(self.root)
    #     self.extra_window.title('Add Sales Order')
    #     self.extra_window.geometry('600x600')
    #     title_label = CTkLabel(self.extra_window, text="ADD NEW SALES ORDER", font=("Helvetica", 20, 'bold'))
    #     title_label.pack(pady=20)
    #
    #     # Product Name
    #     name_frame = CTkFrame(self.extra_window)
    #     name_frame.pack(pady=5, padx=10, fill=X)
    #     name_label = CTkLabel(name_frame, text="Product Name:")
    #     name_label.pack(side=LEFT)
    #     self.name_entry = CTkEntry(name_frame)
    #     self.name_entry.pack(side=RIGHT, fill=X, expand=True)
    #
    #     # Category
    #     category_frame = CTkFrame(self.extra_window)
    #     category_frame.pack(pady=5, padx=10, fill=X)
    #     category_label = CTkLabel(category_frame, text="Category:")
    #     category_label.pack(side=LEFT)
    #     self.category_var = StringVar()
    #     self.category_menu = ttk.Combobox(category_frame, textvariable=self.category_var,
    #                                       values=["Electronics", "Appliances", "Personal Care", "Homeware",
    #                                               "Furniture"])
    #     self.category_menu.pack(side=RIGHT, fill=X, expand=True)
    #
    #     # Quantity
    #     quantity_frame = CTkFrame(self.extra_window)
    #     quantity_frame.pack(pady=5, padx=10, fill=X)
    #     quantity_label = CTkLabel(quantity_frame, text="Quantity:")
    #     quantity_label.pack(side=LEFT)
    #     self.quantity_entry = CTkEntry(quantity_frame)
    #     self.quantity_entry.pack(side=RIGHT, fill=X, expand=True)
    #
    #     # Store Branch
    #     store_branch_frame = CTkFrame(self.extra_window)
    #     store_branch_frame.pack(pady=5, padx=10, fill=X)
    #     store_branch_label = CTkLabel(store_branch_frame, text="Store Branch:")
    #     store_branch_label.pack(side=LEFT)
    #     self.store_branch_var = StringVar()
    #     self.store_branch_entry = CTkEntry(store_branch_frame, textvariable=self.store_branch_var)
    #     self.store_branch_entry.pack(side=RIGHT, fill=X, expand=True)
    #
    #     add_button = CTkButton(self.extra_window, text="Add Order", command=self.add_sales_order)
    #     add_button.pack(pady=10)
    #
    #     clear_button = CTkButton(self.extra_window, text="Clear", command=self.clear_sales_order_entries)
    #     clear_button.pack(pady=10)

    def create_sales_order_window(self):
        selected_item = self.inventory_table.selection()
        if not selected_item:
            mb.showwarning('Error', 'Please select an inventory item before adding a sales order.')
            return

        inventory_item = self.inventory_table.item(selected_item)['values']
        self.selected_product_name = inventory_item[2]
        self.selected_product_id = inventory_item[3]
        self.selected_category = inventory_item[5]
        self.selected_quantity = inventory_item[4]
        self.selected_date = inventory_item[1]

        self.extra_window = CTkToplevel(self.root)
        self.extra_window.title('Add Sales Order')
        self.extra_window.geometry('400x300')

        title_label = CTkLabel(self.extra_window, text="ADD NEW SALES ORDER", font=("Helvetica", 20, 'bold'))
        title_label.pack(pady=20)

        # Location Branch
        location_branch_frame = CTkFrame(self.extra_window)
        location_branch_frame.pack(pady=5, padx=10, fill=X)
        location_branch_label = CTkLabel(location_branch_frame, text="Location Branch:")
        location_branch_label.pack(side=LEFT)
        self.location_branch_var = StringVar()
        self.location_branch_entry = CTkEntry(location_branch_frame, textvariable=self.location_branch_var)
        self.location_branch_entry.pack(side=RIGHT, fill=X, expand=True)

        add_button = CTkButton(self.extra_window, text="Add Order", command=self.add_sales_order)
        add_button.pack(pady=10)

        clear_button = CTkButton(self.extra_window, text="Clear", command=self.clear_sales_order_entries)
        clear_button.pack(pady=10)

    def add_sales_order(self):
        location_branch = self.location_branch_var.get()

        if location_branch:
            self.cursor.execute(
                'INSERT INTO Sales_Orders (PRODUCT_NAME, PRODUCT_ID, CATEGORY, QUANTITY, DATE, STORE_BRANCH) VALUES (?, ?, ?, ?, ?, ?)',
                (self.selected_product_name, self.selected_product_id, self.selected_category, self.selected_quantity, self.selected_date,
                 location_branch)
            )
            self.connector.commit()
            self.load_sales_order_data()
            mb.showinfo('Success', 'Sales order added successfully!')
            self.extra_window.destroy()
        else:
            mb.showwarning('Error', 'Please fill in the location branch.')

    def save_sales_order_changes(self):
        product_name = self.name_entry.get()
        category = self.category_var.get()
        quantity = self.quantity_entry.get()
        store_branch = self.store_branch_var.get()

        if product_name and category and quantity and store_branch:
            self.cursor.execute(
                'UPDATE Sales_Orders SET PRODUCT_NAME=?, CATEGORY=?, QUANTITY=?, STORE_BRANCH=? WHERE ORDER_ID=?',
                (product_name, category, quantity, store_branch, self.edit_order_id)
            )
            self.connector.commit()
            self.load_sales_order_data()
            mb.showinfo('Success', 'Sales order updated successfully!')
            self.extra_window.destroy()
        else:
            mb.showwarning('Error', 'Please fill in all fields.')

    def delete_sales_order(self):
        selected_item = self.sales_order_table.selection()
        if not selected_item:
            mb.showwarning('Error', 'Please select a sales order to delete.')
            return

        confirm = mb.askyesno('Confirm Delete', 'Are you sure you want to delete the selected sales order?')
        if not confirm:
            return

        order_id = self.sales_order_table.item(selected_item)['values'][0]
        self.cursor.execute('DELETE FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))
        self.connector.commit()
        self.load_sales_order_data()
        mb.showinfo('Success', 'Sales order deleted successfully!')

    def load_inventory_data(self):
        self.inventory_table.delete(*self.inventory_table.get_children())

        self.cursor.execute("SELECT * FROM Inventory WHERE LOCATION='Shipping Area'")
        rows = self.cursor.fetchall()

        for row in rows:
            self.inventory_table.insert('', 'end', values=row)

    def clear_sales_order_entries(self):
        self.name_entry.delete(0, END)
        self.category_menu.set('')
        self.quantity_entry.delete(0, END)
        self.store_branch_entry.delete(0, END)

    def complete_sales_order(self):
        selected_item = self.sales_order_table.selection()
        if not selected_item:
            mb.showwarning('Error', 'Please select a sales order to complete.')
            return

        order_id = self.sales_order_table.item(selected_item)['values'][0]
        inv_id = self.inventory_table.item(selected_item)['values'][0]

        confirm = mb.askyesno('Confirm Complete', 'Are you sure you want to complete the selected sales order?')
        if not confirm:
            return

        self.cursor.execute('DELETE FROM Sales_Orders WHERE ORDER_ID=?', (order_id,))
        self.cursor.execute('DELETE FROM Inventory WHERE PRODUCT_REAL_ID=?', (inv_id,))
        self.connector.commit()
        self.load_sales_order_data()
        self.load_inventory_data()
        mb.showinfo('Success', 'Sales order completed successfully!')
        
    # Vendor
    def open_vendor_panel(self):
        self.button_frame_vendor.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.button_frame.place_forget()
        self.table_frame9.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.chart_frame.place_forget()
        self.load_vendor_data()
        self.load_vendor_ids()

    def load_vendor_ids(self):
        self.cursor.execute('SELECT VENDOR_ID FROM Vendors')
        vendor_ids = [row[0] for row in self.cursor.fetchall()]
        return vendor_ids

    def load_vendor_data1(self):
        self.vendor_table1.delete(*self.vendor_table1.get_children())

        self.cursor.execute('SELECT * FROM Vendors')
        rows = self.cursor.fetchall()

        for row in rows:
            self.vendor_table1.insert('', 'end', values=row)

    def create_vendor_window(self):
        self.extra_window = CTkToplevel(self.root)  # Use self.root as the parent
        self.extra_window.title('Add Vendor')
        self.extra_window.geometry('600x600')

        title_label = CTkLabel(self.extra_window, text="ADD NEW VENDOR", font=("Helvetica", 14))
        title_label.pack(pady=20)

        # Vendor Name
        name_frame = CTkFrame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=X)
        name_label = CTkLabel(name_frame, text="Vendor Name:")
        name_label.pack(side=LEFT)
        self.name_entry = CTkEntry(name_frame)
        self.name_entry.pack(side=RIGHT, fill=X, expand=True)

        # Email
        email_frame = CTkFrame(self.extra_window)
        email_frame.pack(pady=5, padx=10, fill=X)
        email_label = CTkLabel(email_frame, text="Email:")
        email_label.pack(side=LEFT)
        self.email_entry = CTkEntry(email_frame)
        self.email_entry.pack(side=RIGHT, fill=X, expand=True)

        # Phone Number
        phone_frame = CTkFrame(self.extra_window)
        phone_frame.pack(pady=5, padx=10, fill=X)
        phone_label = CTkLabel(phone_frame, text="Phone Number:")
        phone_label.pack(side=LEFT)
        self.phone_entry = CTkEntry(phone_frame)
        self.phone_entry.pack(side=RIGHT, fill=X, expand=True)

        # Company
        company_frame = CTkFrame(self.extra_window)
        company_frame.pack(pady=5, padx=10, fill=X)
        company_label = CTkLabel(company_frame, text="Company:")
        company_label.pack(side=LEFT)
        self.company_entry = CTkEntry(company_frame)
        self.company_entry.pack(side=RIGHT, fill=X, expand=True)

        add_button = CTkButton(self.extra_window, text="Add Vendor", command=self.add_vendor)
        add_button.pack(pady=10)

        clear_button = CTkButton(self.extra_window, text="Clear", command=self.clear_vendor_entries)
        clear_button.pack(pady=10)

    def add_notification(self, description):
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION) VALUES (?)', (description,))
        self.connector.commit()

    def add_vendor(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        company = self.company_entry.get()

        if name and email and phone and company:
            self.cursor.execute(
                'INSERT INTO Vendors (NAME, EMAIL, PHONE_NUMBER, COMPANY) VALUES (?, ?, ?, ?)',
                (name, email, phone, company)
            )
            self.connector.commit()
            self.load_vendor_data1()
            self.add_notification(f'Vendor {name} added.')
            mb.showinfo('Success', 'Vendor added successfully!')
            self.extra_window.destroy()
        else:
            mb.showwarning('Error', 'Please fill in all fields.')

    def edit_vendor_window(self):
        selected_item = self.vendor_frame.selection()
        if not selected_item:
            mb.showwarning('Error', 'Please select a vendor to edit.')
            return

        vendor_id = self.vendor_frame.item(selected_item)['values'][0]
        self.extra_window = CTkToplevel(self.root)
        self.extra_window.title('Edit Vendor')
        self.extra_window.geometry('600x600')

        title_label = CTkLabel(self.extra_window, text="EDIT VENDOR", font=("Helvetica", 14))
        title_label.pack(pady=20)

        self.cursor.execute('SELECT * FROM Vendors WHERE VENDOR_ID=?', (vendor_id,))
        vendor = self.cursor.fetchone()

        self.edit_vendor_id = vendor[0]

        # Vendor Name
        name_frame = CTkFrame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=X)
        name_label = CTkLabel(name_frame, text="Vendor Name:")
        name_label.pack(side=LEFT)
        self.name_entry = CTkEntry(name_frame)
        self.name_entry.insert(0, vendor[1])
        self.name_entry.pack(side=RIGHT, fill=X, expand=True)

        # Email
        email_frame = CTkFrame(self.extra_window)
        email_frame.pack(pady=5, padx=10, fill=X)
        email_label = CTkLabel(email_frame, text="Email:")
        email_label.pack(side=LEFT)
        self.email_entry = CTkEntry(email_frame)
        self.email_entry.insert(0, vendor[2])
        self.email_entry.pack(side=RIGHT, fill=X, expand=True)

        # Phone Number
        phone_frame = CTkFrame(self.extra_window)
        phone_frame.pack(pady=5, padx=10, fill=X)
        phone_label = CTkLabel(phone_frame, text="Phone Number:")
        phone_label.pack(side=LEFT)
        self.phone_entry = CTkEntry(phone_frame)
        self.phone_entry.insert(0, vendor[3])
        self.phone_entry.pack(side=RIGHT, fill=X, expand=True)

        # Company
        company_frame = CTkFrame(self.extra_window)
        company_frame.pack(pady=5, padx=10, fill=X)
        company_label = CTkLabel(company_frame, text="Company:")
        company_label.pack(side=LEFT)
        self.company_entry = CTkEntry(company_frame)
        self.company_entry.insert(0, vendor[4])
        self.company_entry.pack(side=RIGHT, fill=X, expand=True)

        save_button = CTkButton(self.extra_window, text="Save Changes", command=self.save_vendor_changes)
        save_button.pack(pady=10)

    def save_vendor_changes(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.phone_entry.get()
        company = self.company_entry.get()

        if name and email and phone and company:
            try:
                self.cursor.execute(
                    'UPDATE Vendors SET NAME=?, EMAIL=?, PHONE_NUMBER=?, COMPANY=? WHERE VENDOR_ID=?',
                    (name, email, phone, company, self.edit_vendor_id)
                )
                self.connector.commit()
                self.load_vendor_data1()
                self.add_notification(f'Updated details for Vendor {name}.')
                mb.showinfo('Success', 'Vendor updated successfully!')
                self.extra_window.destroy()
            except Exception as e:
                mb.showerror('Error', f'Error updating vendor: {str(e)}')
        else:
            mb.showwarning('Error', 'Please fill in all fields.')

    def delete_vendor(self):
        selected_item = self.vendor_table1.selection()
        if not selected_item:
            mb.showwarning('Error', 'Please select a vendor to delete.')
            return

        confirm = mb.askyesno('Confirm Delete', 'Are you sure you want to delete the selected vendor?')
        if not confirm:
            return

        vendor_id = self.vendor_table1.item(selected_item)['values'][0]
        try:
            self.cursor.execute('DELETE FROM Vendors WHERE VENDOR_ID=?', (vendor_id,))
            self.connector.commit()
            self.load_vendor_data1()
            # self.add_notification(f'Deleted Vendor with ID {vendor_id}.')
            mb.showinfo('Success', 'Vendor deleted successfully!')
        except Exception as e:
            mb.showerror('Error', f'Error deleting vendor: {str(e)}')

    def clear_vendor_entries(self):
        self.name_entry.delete(0, END)
        self.email_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.company_entry.delete(0, END)

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

    def show_dashboard(self):
        self.chart_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.75)

        # Modify SQL query to group by product name and sum stocks
        all_data = self.connector.execute('SELECT PRODUCT_NAME, SUM(STOCKS) FROM Inventory GROUP BY PRODUCT_NAME')
        data = all_data.fetchall()

        # Query to fetch total number of purchase orders
        purchase_order_count = self.connector.execute('SELECT COUNT(*) FROM Orders').fetchone()[0]

        # Query to fetch total number of sales orders
        sales_order_count = self.connector.execute('SELECT COUNT(*) FROM Sales_Orders').fetchone()[0]

        # Query to fetch total number of users
        total_users = self.connector.execute('SELECT COUNT(*) FROM users').fetchone()[0]

        # Query to fetch total number of tasks assigned to the current user
        total_tasks = \
        self.connector.execute('SELECT COUNT(*) FROM tasks WHERE assigned_to=?', (self.username,)).fetchone()[0]

        if not data:
            mb.showerror('No Data', 'No data available to display!')
            return

        product_names = [item[0] for item in data]
        stocks = [item[1] for item in data]
        total_stocks = sum(stocks)

        fig, axs = plt.subplots(2, 2, figsize=(14, 10), gridspec_kw={'hspace': 0.4, 'wspace': 0.4})

        # Bar Chart
        axs[0, 0].bar(product_names, stocks, color='orange', edgecolor='black')
        axs[0, 0].set_title('Total Stocks by Product', fontsize=14)
        axs[0, 0].set_xlabel('Product Name', fontsize=12)
        axs[0, 0].set_ylabel('Total Stocks', fontsize=12)
        axs[0, 0].set_xticklabels(product_names, rotation=45, ha='right')
        axs[0, 0].tick_params(axis='x', labelsize=10)
        axs[0, 0].tick_params(axis='y', labelsize=10)

        # Pie Chart
        axs[0, 1].pie(stocks, labels=product_names, autopct='%1.1f%%', startangle=140,
                      colors=plt.cm.Paired(np.arange(len(product_names))), wedgeprops={'edgecolor': 'black'})
        axs[0, 1].set_title('Stock Distribution by Product', fontsize=14)

        # Summary Statistics
        mean_stock = np.mean(stocks)
        median_stock = np.median(stocks)
        min_stock = np.min(stocks)
        max_stock = np.max(stocks)

        summary_text = (f'Total Stocks: {total_stocks}\n'
                        f'Mean Stock: {mean_stock:.2f}\n'
                        f'Median Stock: {median_stock:.2f}\n'
                        f'Minimum Stock: {min_stock}\n'
                        f'Maximum Stock: {max_stock}\n')

        order_summary_text = (f'Pending Purchase Orders: {purchase_order_count}\n'
                              f'Pending Sales Orders: {sales_order_count}\n')

        low_stock_threshold = 20
        low_stock_products = [(product_names[i], stocks[i]) for i in range(len(stocks)) if
                              stocks[i] < low_stock_threshold]

        if low_stock_products:
            low_stock_text = 'Products with Low Stocks:\n' + '\n'.join(
                [f'{item[0]}: {item[1]}' for item in low_stock_products])
        else:
            low_stock_text = 'No Low Stock Products'

        user_summary_text = f'Total Users: {total_users}'
        task_summary_text = f'Pending Tasks: {total_tasks}'

        # Hide the unused subplots
        for ax in [axs[1, 0], axs[1, 1]]:
            ax.axis('off')

        # Adjust the placement and size of the summary text boxes
        fig.text(0.4, 0.40, summary_text, ha='left', va='top', fontsize=14, color='black',
                 bbox=dict(facecolor='lightyellow', edgecolor='black', boxstyle='round,pad=1', alpha=0.9))

        fig.text(0.4, 0.15, order_summary_text, ha='left', va='top', fontsize=14, color='black',
                 bbox=dict(facecolor='lightgreen', edgecolor='black', boxstyle='round,pad=1', alpha=0.9))

        fig.text(0.7, 0.4, user_summary_text, ha='left', va='top', fontsize=14, color='black',
                 bbox=dict(facecolor='lightblue', edgecolor='black', boxstyle='round,pad=1', alpha=0.9))

        fig.text(0.7, 0.30, task_summary_text, ha='left', va='top', fontsize=14, color='black',
                 bbox=dict(facecolor='lightpink', edgecolor='black', boxstyle='round,pad=1', alpha=0.9))

        fig.text(0.1, 0.40, low_stock_text, ha='left', va='top', fontsize=14, color='black',
                 bbox=dict(facecolor='lightcyan', edgecolor='black', boxstyle='round,pad=1', alpha=0.9))

        plt.tight_layout(rect=[0, 0.1, 1, 0.95])

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    def show_inventory_stats(self):
        fig, axs = plt.subplots(2, 2, figsize=(14, 10), gridspec_kw={'hspace': 0.4, 'wspace': 0.4})

        for ax in [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]]:
            ax.axis('off')

        all_data = self.connector.execute('SELECT PRODUCT_NAME, SUM(STOCKS) FROM Inventory GROUP BY PRODUCT_NAME')
        data = all_data.fetchall()

        stocks = [item[1] for item in data]
        total_stocks = sum(stocks)

        mean_stock = np.mean(stocks)
        median_stock = np.median(stocks)
        min_stock = np.min(stocks)
        max_stock = np.max(stocks)

        summary_text = (f'Total Stocks: {total_stocks}\n'
                        f'Mean Stock: {mean_stock:.2f}\n'
                        f'Median Stock: {median_stock:.2f}\n'
                        f'Minimum Stock: {min_stock}\n'
                        f'Maximum Stock: {max_stock}\n')

        fig.text(0.05, 0.75, summary_text, ha='left', va='top', fontsize=14, color='black',
                 bbox=dict(facecolor='lightyellow', edgecolor='black', boxstyle='round,pad=1', alpha=0.9))

        canvas = FigureCanvasTkAgg(fig, master=self.inventory_stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    def show_order_stats(self):
        # Query to fetch total number of purchase orders
        purchase_order_count = self.connector.execute('SELECT COUNT(*) FROM Orders').fetchone()[0]

        # Query to fetch total number of sales orders
        sales_order_count = self.connector.execute('SELECT COUNT(*) FROM Sales_Orders').fetchone()[0]

        fig, axs = plt.subplots(2, 2, figsize=(14, 10), gridspec_kw={'hspace': 0.4, 'wspace': 0.4})

        for ax in [axs[0, 0], axs[0, 1], axs[1, 0], axs[1, 1]]:
            ax.axis('off')

        all_data = self.connector.execute('SELECT PRODUCT_NAME, SUM(STOCKS) FROM Inventory GROUP BY PRODUCT_NAME')
        data = all_data.fetchall()

        order_summary_text = (f'Pending Purchase Orders: {purchase_order_count}\n'
                              f'Pending Sales Orders: {sales_order_count}\n')


        fig.text(0.1, 0.70, order_summary_text, ha='left', va='top', fontsize=14, color='black',
                 bbox=dict(facecolor='lightgreen', edgecolor='black', boxstyle='round,pad=1', alpha=0.9))

        canvas = FigureCanvasTkAgg(fig, master=self.order_stats_frame)
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
