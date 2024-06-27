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


class SupervisorApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect("AcrePliances.db")
        self.cursor = self.connector.cursor()
        self.connector2 = sqlite3.connect('users.db')
        self.cursor2 = self.connector2.cursor()

        self.connector.execute(
            'CREATE TABLE IF NOT EXISTS Inventory (PRODUCT_REAL_ID INTEGER PRIMARY KEY, date DATE, PRODUCT_NAME TEXT, '
            'PRODUCT_ID TEXT,'
            'STOCKS INTEGER, CATEGORY VARCHAR(30), PURCHASE_PRICE FLOAT, '
            'SELLING_PRICE FLOAT, LOCATION VARCHAR(30), INTERNAL_REFERENCE VARCHAR(30))'
        )
        self.connector.commit()

        self.root = root
        self.username = username
        self.root.title('ACREPILLANCE')
        self.root.geometry('1920x1000')
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

    def setup_frames(self):
        self.dashboard_frame = Frame(self.root, bg='#C21A2F')
        self.dashboard_frame.place(relx=0.00, rely=0.00, relwidth=1.00, relheight=0.20)

        self.button_frame = Frame(self.root, bg='#9C0014')
        self.button_frame.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)

        self.button_frame_inventory = Frame(self.root, bg='#9C0014')
        self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.15, relwidth=0.22)
        self.button_frame_inventory.place_forget()

        self.button_frame_tasks = Frame(self.root, bg='#9C0014')
        self.button_frame_tasks.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.button_frame_tasks.place_forget()

        self.button_frame_tasks2 = Frame(self.root)
        self.button_frame_tasks2.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.button_frame_tasks2.place_forget()

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
        self.setup_tasks_button_widgets()
        self.setup_tasks_entry_widgets()
        self.setup_tasks_table()
        self.setup_tasks2_button_widgets()
        self.setup_tasks2_entry_widgets()
        self.setup_tasks2_table()
        # self.load_dashboard_image()

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
        self.newlocation = ttk.OptionMenu(self.data_entry_frame, self.NEW_LOCATION, 'Receiving Area',
                                          'Receiving Area', 'Staging Area', 'Storage Area', 'Shipping Area')
        self.newlocation.place(x=200, y=140)

        # Hide Move Product Widgets
        def hide():
            self.moveamount_label.place_forget()
            self.moveamount.place_forget()
            self.newlocation_label.place_forget()
            self.newlocation.place_forget()

        # Make the hide function available
        self.hide_move_product_widgets = hide

    # Dashboard Buttons
    def setup_button_widgets(self):

        ttk.Button(self.button_frame, text='Inventory Management', width=20, style='Bold.TButton',
                   command=self.open_inventory_panel).place(x=40, y=35, width=200, height=50)

        ttk.Button(self.button_frame, text='Task Assignment', width=20, style='Bold.TButton',
                   command=self.open_task_panel).place(x=40, y=135, width=200, height=50)

        ttk.Button(self.button_frame, text='Log out', command=self.restart_login_page, style='Bold.TButton',
                   width=20).place(x=20, y=630, width=100, height=30)

    # Inventory Management Buttons
    def setup_inventory_button_widgets(self):

        CTkButton(self.button_frame_inventory, text='Add Inventory', command=self.add_inventory, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=75, y=80, anchor=W)

        CTkButton(self.button_frame_inventory, text='Delete Inventory', command=self.remove_inventory, width=275,
                  height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=75, y=180, anchor=W)

        CTkButton(self.button_frame_inventory, text='Edit Selected Product', command=self.edit_product_details,
                  width=275, height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=75, y=290, anchor=W)

        CTkButton(self.button_frame_inventory, text='Move Product Location', command=self.move_product_location,
                  width=275, height=80, border_width=0, fg_color='white', border_color='black', text_color='black',
                  font=('Microsoft YaHei UI Light', 22), corner_radius=15, hover_color='orange'
                  ).place(x=75, y=400, anchor=W)

        CTkButton(self.button_frame_inventory, text='Back', command=self.close_subpanel, width=90, height=45,
                  border_width=0, fg_color='red', border_color='black', text_color='white',
                  font=('Microsoft YaHei UI Light', 16), corner_radius=15, hover_color='orange'
                  ).place(x=160, y=500, anchor=W)

    # Task Management Buttons
    def setup_tasks_button_widgets(self):
        ttk.Button(self.button_frame_tasks, text='Assign Task', command=self.assign_task, width=20,
                   style='Bold.TButton',
                   ).place(x=40, y=35, width=200, height=50)
        ttk.Button(self.button_frame_tasks, text='Back', command=self.close_subpanel, style='Bold.TButton',
                   width=20).place(x=20, y=630, width=60, height=30)

    # Task Management Entry
    def setup_tasks_entry_widgets(self):

        self.task_entry_label = ttk.Label(self.task_assignment_frame, text='Task:', font=('Gill Sans MT', 13))
        self.task_entry_label.place(x=130, y=30)
        self.task_entry = ttk.Entry(self.task_assignment_frame, font=('Gill Sans MT', 13), width=20)
        self.task_entry.place(x=300, y=30)

        self.worker_label = ttk.Label(self.task_assignment_frame, text='Assign to Worker:', font=('Gill Sans MT', 13))
        self.worker_label.place(x=130, y=80)
        self.worker_entry = ttk.Entry(self.task_assignment_frame, font=('Gill Sans MT', 13), width=20)
        self.worker_entry.place(x=300, y=80)

        self.assign_button = ttk.Button(self.task_assignment_frame, text='Assign', command=self.assign_task,
                                        style='Bold.TButton', width=20).place(x=300, y=130, width=160, height=50)

    def setup_tasks2_button_widgets(self):
        ttk.Button(self.button_frame_tasks2, text='Update Status', command=self.update_status, width=20,
                   style='Bold.TButton',
                   ).place(x=40, y=35, width=200, height=50)
        ttk.Button(self.button_frame_tasks2, text='Back', command=self.close_subpanel, style='Bold.TButton',
                   width=20).place(x=20, y=630, width=60, height=30)

    def setup_tasks2_entry_widgets(self):

        self.status_var = StringVar()
        self.status_menu = ttk.Combobox(self.task_assignment_frame2, textvariable=self.status_var, state='readonly',
                                        values=["Incomplete", "In Progress", "Blocked", "Complete"])
        self.status_menu.place(x=130, y=80)

    # Inventory Management Table
    def setup_table(self):
        self.table = ttk.Treeview(self.table_frame, selectmode=BROWSE,
                                  columns=(
                                      'PRODUCT_REAL_ID', 'DATE', 'PRODUCT_NAME', 'PRODUCT_ID', 'STOCKS', 'CATEGORY',
                                      'PURCHASE_PRICE', 'SELLING_PRICE', 'LOCATION', 'INTERNAL_REFERENCE'))

        X_Scroller = Scrollbar(self.table, orient=HORIZONTAL, command=self.table.xview)
        Y_Scroller = Scrollbar(self.table, orient=VERTICAL, command=self.table.yview)
        X_Scroller.pack(side=BOTTOM, fill=X)
        Y_Scroller.pack(side=RIGHT, fill=Y)

        self.table.config(yscrollcommand=Y_Scroller.set)

        self.table.heading('PRODUCT_REAL_ID', text='', anchor=CENTER)
        self.table.heading('DATE', text='Date', anchor=CENTER)
        self.table.heading('PRODUCT_NAME', text='Product Name', anchor=CENTER)
        self.table.heading('PRODUCT_ID', text='Product ID', anchor=CENTER)
        self.table.heading('STOCKS', text='Stocks', anchor=CENTER)
        self.table.heading('CATEGORY', text='Category', anchor=CENTER)
        self.table.heading('PURCHASE_PRICE', text='Purchase Price', anchor=CENTER)
        self.table.heading('SELLING_PRICE', text='Selling Price', anchor=CENTER)
        self.table.heading('LOCATION', text='Warehouse Location', anchor=CENTER)
        self.table.heading('INTERNAL_REFERENCE', text='Product IR', anchor=CENTER)

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

    # Task Management Table
    def setup_tasks_table(self):
        self.task_table = ttk.Treeview(self.table_frame3, selectmode=BROWSE,
                                       columns=('ID', 'Task', 'Assigned To', 'Status'))

        Y_Scroller = Scrollbar(self.task_table, orient=VERTICAL, command=self.task_table.yview)
        Y_Scroller.pack(side=RIGHT, fill=Y)

        self.task_table.config(yscrollcommand=Y_Scroller.set)

        self.task_table.heading('ID', text='ID', anchor=CENTER)
        self.task_table.heading('Task', text='Task', anchor=CENTER)
        self.task_table.heading('Assigned To', text='Assigned To', anchor=CENTER)
        self.task_table.heading('Status', text='Status', anchor=CENTER)

        self.task_table.column('#0', width=0, stretch=NO)
        self.task_table.column('#1', width=50, stretch=NO)
        self.task_table.column('#2', width=300, stretch=NO)
        self.task_table.column('#3', width=50, stretch=NO)

        self.task_table.place(relx=0, rely=0, relheight=1, relwidth=1)

    def setup_tasks2_table(self):
        self.task2_table = ttk.Treeview(self.table_frame4, selectmode=BROWSE,
                                        columns=('ID', 'Task', 'Status'))

        Y_Scroller = Scrollbar(self.task2_table, orient=VERTICAL, command=self.task2_table.yview)
        Y_Scroller.pack(side=RIGHT, fill=Y)

        self.task2_table.heading('ID', text='ID', anchor=CENTER)
        self.task2_table.heading('Task', text='Task', anchor=CENTER)
        self.task2_table.heading('Status', text='Status', anchor=CENTER)

        self.task2_table.column('#0', width=0, stretch=NO)
        self.task2_table.column('#1', width=300, stretch=NO)
        self.task2_table.column('#2', width=100, stretch=NO)

        self.task2_table.place(relx=0, rely=0, relheight=1, relwidth=1)

    # Inventory Management Functions
    def open_inventory_panel(self):
        self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.button_frame.place_forget()
        self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)
        self.data_entry_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.25)
        self.chart_frame.place_forget()
        self.hide_move_product_widgets()

    def close_subpanel(self):
        self.button_frame_users.place_forget()
        self.button_frame.place(relx=0.00, rely=0.20, relheight=0.80, relwidth=0.22)
        self.button_frame_inventory.place_forget()
        self.button_frame_tasks.place_forget()
        self.button_frame_tasks2.place_forget()
        self.table_frame.place_forget()
        self.table_frame2.place_forget()
        self.table_frame3.place_forget()
        self.table_frame4.place_forget()
        self.data_entry_frame.place_forget()
        self.task_assignment_frame.place_forget()
        self.task_assignment_frame2.place_forget()
        self.chart_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)
        self.show_bar_chart()

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

    def edit_product_details(self):
        if not self.table.selection():
            mb.showerror('No record selected!', 'Please select a record to edit!')
            return
        else:
            self.table_frame.place_forget()
            self.button_frame_inventory.place_forget()
            self.data_entry_frame.place(relx=0.10, rely=0.20, relwidth=1.0, relheight=0.90)
            self.hide_move_product_widgets()

            current_selected_product = self.table.item(self.table.focus())
            values = current_selected_product['values']

            self.PRODUCT_NAME.set(values[2])
            self.STOCKS.set(values[4])
            self.CATEGORY.set(values[5])
            self.PURCHASE_PRICE.set(values[6])
            self.SELLING_PRICE.set(values[7])
            self.LOCATION.set(values[8])
            self.date.set_date(datetime.datetime.strptime(values[1], '%Y-%m-%d'))

            self.add_btn = Button(self.data_entry_frame, text='Update Record', font='Helvetica 13 bold',
                                  bg='SpringGreen4', command=self.update_record_direct)
            self.add_btn.place(x=270, y=220)

            self.add_btn = Button(self.data_entry_frame, text='Cancel', font='Helvetica 13 bold',
                                  bg='red', command=self.cancel_update)

            self.add_btn.place(x=420, y=220)

    def move_product_location(self):
        if not self.table.selection():
            mb.showerror('No record selected!', 'Please select a record to edit!')
            return
        else:
            self.table_frame.place_forget()
            self.button_frame_inventory.place_forget()
            self.data_entry_frame.place(relx=0.10, rely=0.20, relwidth=1.0, relheight=0.90)
            self.hide_data_entry_widgets()
            self.setup_move_product_widgets()

            # self.dashboard_frame.pack(fill='both', side='top', expand=1)

            current_selected_product = self.table.item(self.table.focus())
            values = current_selected_product['values']

            self.PRODUCT_NAME.set(values[2])
            self.STOCKS.set(values[4])
            self.CATEGORY.set(values[5])
            self.PURCHASE_PRICE.set(values[6])
            self.SELLING_PRICE.set(values[7])
            self.LOCATION.set(values[8])
            self.PRODUCT_ID.set(values[3])
            self.date.set_date(datetime.datetime.strptime(values[1], '%Y-%m-%d'))

            self.add_btn = Button(self.data_entry_frame, text='Move Product', font='Helvetica 13 bold',
                                  bg='SpringGreen4', command=self.update_record)
            self.add_btn.place(x=270, y=220)

            self.add_btn = Button(self.data_entry_frame, text='Cancel', font='Helvetica 13 bold',
                                  bg='red', command=self.cancel_update)

            self.add_btn.place(x=420, y=220)

    def add_inventory(self):
        # Generate product ID based on category
        category_prefix = self.CATEGORY.get()[0].upper()  # Get the first letter of the category
        count = \
            self.cursor.execute('SELECT COUNT(*) FROM Inventory WHERE CATEGORY=?', (self.CATEGORY.get(),)).fetchone()[0]
        product_id = f"{category_prefix}{count + 1:03d}"  # Format product ID with category prefix and padded number

        location_prefix = self.LOCATION.get()[:3].upper()  # Get the first 3 letters of the location
        product_internal_reference = f"WH-{location_prefix}-{product_id}"

        try:
            if (
                    not self.date.get_date() or not self.date.get_date() or not self.STOCKS.get() or not self.CATEGORY.get() or not
            self.PURCHASE_PRICE.get() or not self.SELLING_PRICE.get() or not self.LOCATION.get()):
                mb.showerror('Fields empty!',
                             "Please fill all missing fields before adding.")
            else:
                # Insert data into database
                self.cursor.execute(
                    'INSERT INTO Inventory (date, PRODUCT_NAME, PRODUCT_ID, STOCKS, CATEGORY, PURCHASE_PRICE, '
                    'SELLING_PRICE, LOCATION, INTERNAL_REFERENCE)'
                    'VALUES (?, LTRIM(RTRIM(?)), ?, ?, ?, ?, ?, LTRIM(RTRIM(?)), ?)',
                    (
                        self.date.get_date(), self.PRODUCT_NAME.get(), product_id, self.STOCKS.get(),
                        self.CATEGORY.get(),
                        self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), self.LOCATION.get(),
                        product_internal_reference
                    )
                )
                self.connector.commit()

                mb.showinfo('Success', 'Inventory added successfully')
                self.list_all_inventory()

                # Generate PDF report
                self.generate_pdf_report(
                    self.PRODUCT_NAME.get(), product_id, self.STOCKS.get(), self.CATEGORY.get(),
                    self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), self.LOCATION.get(),
                    self.date.get_date(), 'Add'
                )

                self.clear_fields()
        except:
            mb.showerror("Error", "Inappropriate values.")

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
                        f'The record of {self.PRODUCT_NAME.get()} was updated successfully and {amount_to_move} items were moved to {new_location}')
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
            mb.showerror("Error", f"Inappropriate values. {str(e)}")

    def update_record_direct(self):
        current_selected_product = self.table.item(self.table.focus())
        contents = current_selected_product['values']

        try:
            # Validate required fields
            if (
                    not self.date.get() or not self.PRODUCT_NAME.get() or not self.STOCKS.get() or not self.CATEGORY.get() or
                    not self.PURCHASE_PRICE.get() or not self.SELLING_PRICE.get() or not self.LOCATION.get()):
                mb.showerror('Fields empty or invalid amount!',
                             "Please fill all missing fields.")
                return

            # Update the product record directly
            self.connector.execute(
                'UPDATE Inventory SET date=?, PRODUCT_NAME=LTRIM(RTRIM(?)), STOCKS=?, CATEGORY=?, PURCHASE_PRICE=?, '
                'SELLING_PRICE=?, LOCATION=? WHERE PRODUCT_REAL_ID=?', (
                    self.date.get_date(), self.PRODUCT_NAME.get(), int(self.STOCKS.get()), self.CATEGORY.get(),
                    self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), self.LOCATION.get(), contents[0])
            )

            self.connector.commit()

            mb.showinfo('Updated successfully',
                        f'The record of {self.PRODUCT_NAME.get()} was updated successfully.')
            self.list_all_inventory()
            self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
            self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
            self.add_btn.place_forget()
            # self.add_btn1.place_forget()
            # self.add_btn2.place_forget()
            # self.add_btn3.place_forget()
            self.data_entry_frame.place_forget()
            self.data_entry_frame.pack()
            self.data_entry_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)

            # Generate PDF report for the updated record
            self.generate_pdf_report(
                self.PRODUCT_NAME.get(), contents[0], int(self.STOCKS.get()), self.CATEGORY.get(),
                self.PURCHASE_PRICE.get(), self.SELLING_PRICE.get(), self.LOCATION.get(),
                self.date.get(), 'Edit'
            )

            self.clear_fields()
        except Exception as e:
            mb.showerror("Error", f"Inappropriate values. {str(e)}")

    def cancel_update(self):
        self.list_all_inventory()
        self.table_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.60)
        self.button_frame_inventory.place(relx=0.00, rely=0.20, relheight=0.90, relwidth=0.22)
        self.data_entry_frame.pack()
        self.data_entry_frame.place(relx=0.22, rely=0.75, relwidth=0.78, relheight=0.30)
        self.hide_move_product_widgets()
        self.hide_data_entry_widgets()
        self.setup_data_entry_widgets()
        self.clear_fields()

# Task Management Functions
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
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, task, assigned_to, status FROM tasks')
        tasks = cursor.fetchall()
        conn.close()

        for task in tasks:
            self.task_table.insert("", "end", values=(task[0], task[1], task[2], task[3]), iid=task[0])

    def load_tasks2(self):
        for i in self.task2_table.get_children():
            self.task2_table.delete(i)

        conn = sqlite3.connect('users.db')
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
                    conn = sqlite3.connect('users.db')
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

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (task, assigned_to, status) VALUES (?, ?, ?)", (task, worker, "Incomplete"))
        conn.commit()
        conn.close()
        self.load_tasks()

# Inventory Report
    @staticmethod
    def generate_pdf_report(product_name, product_id, stocks, category, purchase_price, selling_price, location,
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

# Dashboard Bar Chart
    def show_bar_chart(self):
        self.chart_frame.place(relx=0.22, rely=0.20, relwidth=0.78, relheight=0.55)

        all_data = self.connector.execute('SELECT PRODUCT_NAME, STOCKS FROM Inventory')
        data = all_data.fetchall()

        if not data:
            mb.showerror('No Data', 'No data available to display!')
            return

        product_names = [item[0] for item in data]
        stocks = [item[1] for item in data]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(product_names, stocks, color='orange')
        ax.set_xlabel('Product Name', color='black')
        ax.set_ylabel('Stocks', color='black')
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

    @staticmethod
    def restart_login_page():
        root.quit()
        root.destroy()
        subprocess.Popen(["python", "login.py"])


if __name__ == '__main__':
    username = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    root = Tk()
    app = SupervisorApp(root, username)
    root.mainloop()
