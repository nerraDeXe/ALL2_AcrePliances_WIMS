import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import pytz
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from playsound import playsound
import os
from plyer import notification


class AdminApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect('AcrePliances.db')
        self.cursor = self.connector.cursor()

        self.connector.commit()

        self.root = root
        self.username = username
        self.root.title('Dashboard')
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')
        self.root.resizable(0, 0)
        self.stat_frames = []
        self.create_widgets()
        self.check_low_stock()

    def open_purchase_order_panel(self):
        root.withdraw()
        subprocess.run(["python", "Purchase order.py"])
        root.deiconify()
        self.destroy_graph()
        self.create_graph()
        self.destroy_inventory_stats()
        self.create_inventory_stats()

    def open_vendor_details_panel(self):
        root.withdraw()
        subprocess.run(["python", "Vendor details.py"])
        root.deiconify()
        self.destroy_graph()
        self.create_graph()
        self.destroy_inventory_stats()
        self.create_inventory_stats()

    def open_sales_order_panel(self):
        root.withdraw()
        subprocess.run(["python", "Sales order.py"])
        root.deiconify()
        self.destroy_graph()
        self.create_graph()
        self.destroy_inventory_stats()
        self.create_inventory_stats()

    def open_user_management_panel(self):
        root.withdraw()
        subprocess.run(["python", "User Management.py"])
        root.deiconify()
        self.destroy_graph()
        self.create_graph()
        self.destroy_inventory_stats()
        self.create_inventory_stats()

    def open_inventory_panel(self):
        root.withdraw()
        subprocess.run(["python", "Inventory Management.py"])
        root.deiconify()
        self.destroy_graph()
        self.create_graph()
        self.destroy_inventory_stats()
        self.create_inventory_stats()

    def open_tasks_panel(self):
        root.withdraw()
        subprocess.run(["python", "Task Status Update.py", username])
        root.deiconify()
        self.destroy_graph()
        self.create_graph()
        self.destroy_inventory_stats()
        self.create_inventory_stats()

    def open_tasks_assignment_panel(self):
        root.withdraw()
        subprocess.run(["python", "Task Assignment.py"])
        root.deiconify()
        self.destroy_graph()
        self.create_graph()
        self.destroy_inventory_stats()
        self.create_inventory_stats()

    def create_widgets(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="HOME", font=("Helvetica", 16),
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

        self.button1 = ctk.CTkButton(left_frame, text="USER MANAGEMENT", fg_color='#FFFFFF',
                                     text_color='#000000',
                                     command=self.open_user_management_panel
                                     )
        self.button1.pack(pady=10)

        self.button2 = ctk.CTkButton(left_frame, text="INVENTORY MANAGEMENT", fg_color='#FFFFFF',
                                     text_color='#000000',
                                     command=self.open_inventory_panel)
        self.button2.pack(pady=10)

        self.button3 = ctk.CTkButton(left_frame, text="PURCHASE ORDER", fg_color='#FFFFFF',
                                     text_color='#000000',
                                     command=self.open_purchase_order_panel)
        self.button3.pack(pady=10)

        self.button4 = ctk.CTkButton(left_frame, text="SALES ORDER", fg_color='#FFFFFF',
                                     text_color='#000000',
                                     command=self.open_sales_order_panel
                                     )
        self.button4.pack(pady=10)

        self.button5 = ctk.CTkButton(left_frame, text="VENDORS", fg_color='#FFFFFF',
                                     text_color='#000000',
                                     command=self.open_vendor_details_panel)
        self.button5.pack(pady=10)

        # self.button6 = ctk.CTkButton(left_frame, text="TASK ASSIGNMENT", fg_color='#FFFFFF',
        #                              text_color='#000000',
        #                              command=self.open_tasks_assignment_panel
        #                              )
        # self.button6.pack(pady=10)
        #
        # self.button7 = ctk.CTkButton(left_frame, text="TASKS", fg_color='#FFFFFF',
        #                              text_color='#000000',
        #                              command=self.open_tasks_panel
        #                              )
        # self.button7.pack(pady=10)

        self.back_button = ctk.CTkButton(left_frame, text="LOG OUT", command=self.close_subpanel)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = ctk.CTkFrame(self.root, fg_color='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=20)

        self.dashboard_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = ctk.CTkFrame(self.dashboard_frame, fg_color='lightgray')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.right_frame = ctk.CTkFrame(self.dashboard_frame, fg_color='lightgray')
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_graph()
        self.create_inventory_stats()

    def close_subpanel(self):
        root.destroy()
        root.quit()
        subprocess.run(["python", "login.py"])

    def create_graph(self):
        # Create a graph in the left frame
        conn = sqlite3.connect('AcrePliances.db')
        cursor = conn.cursor()
        cursor.execute('SELECT PRODUCT_ID, SUM(STOCKS) FROM Inventory GROUP BY PRODUCT_NAME')
        data = cursor.fetchall()
        conn.close()

        product_ids = [item[0] for item in data]
        stocks = [item[1] for item in data]

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(product_ids, stocks, color='skyblue')
        ax.set_title('Stock Levels of Different Products')
        ax.set_xlabel('Products')
        ax.set_ylabel('Stock Level')

        self.canvas = FigureCanvasTkAgg(fig, master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def destroy_graph(self):
        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()  # Remove the canvas from the frame
            self.canvas = None  # Clear the reference to the canvas

    def create_inventory_stats(self):
        # Create stats in the right frame
        conn = sqlite3.connect('AcrePliances.db')
        cursor = conn.cursor()

        cursor.execute('SELECT SUM(STOCKS) FROM Inventory')
        total_stocks = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM Purchase_Orders')
        total_purchase_orders = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM Sales_Orders')
        total_sales_orders = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(STOCKS) FROM Inventory WHERE LOCATION="Staging Area"')
        product_sta = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(STOCKS) FROM Inventory WHERE LOCATION="Storage Area"')
        product_sto = cursor.fetchone()[0]



        conn.close()

        stats = {
            'Total Inventory Stocks': total_stocks,
            'Total Purchase Orders': total_purchase_orders,
            'Pending Sales Orders': total_sales_orders,
            'Remaining Product in Staging Area': product_sta,
            'Remaining Product in Storage Area': product_sto,
        }

        industrial_colors = ['orange', 'light blue', 'light blue', 'light blue', 'light blue']
        white = ['white', 'white', 'white', 'white', 'white']
        font = ('Arial', 18, 'bold')
        number_font = ('Arial', 30, 'bold')  # Increased font size for the numbers

        for index, (stat, value) in enumerate(stats.items()):
            stat_frame = ctk.CTkFrame(self.right_frame, fg_color='white')
            stat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.stat_frames.append(stat_frame)  # Store the stat frame reference

            number_label = ctk.CTkLabel(stat_frame, text=f"{value}",
                                        fg_color=white[index % len(white)],
                                        text_color='green',
                                        font=number_font)
            number_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            description_label = ctk.CTkLabel(stat_frame, text=f"{stat}",
                                             fg_color=industrial_colors[index % len(industrial_colors)],
                                             text_color='black',
                                             font=font)
            description_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def destroy_inventory_stats(self):
        for stat_frame in self.stat_frames:
            stat_frame.pack_forget()  # Remove the stat frame from the frame
        self.stat_frames = []  # Clear the list of stat frames

    def add_notification(self, description):
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION, TIMESTAMP) VALUES (?, ?)',
                            (description, timestamp))
        self.connector.commit()
    #     self.play_notification_sound()
    #
    # def play_notification_sound(self):
    #     sound_file = 'rebound.mp3'
    #     if not os.path.isfile(sound_file):
    #         print(f"Sound file '{sound_file}' not found.")
    #         return
    #
    #     try:
    #         playsound(sound_file)  # Path to your alert sound file
    #     except Exception as e:
    #         print(f"Error playing sound: {e}")
    #         print("Attempting to play sound with an alternative library (pygame).")
    #         try:
    #             import pygame
    #             pygame.mixer.init()
    #             pygame.mixer.music.load(sound_file)
    #             pygame.mixer.music.play()
    #             while pygame.mixer.music.get_busy():
    #                 pygame.time.Clock().tick(10)
    #         except Exception as e:
    #             print(f"Alternative method failed: {e}")

    def show_notifications_window(self):
        subprocess.Popen(["python", "Notifications.py"])

    def check_low_stock(self):
        try:
            # Query to select products with stock quantity less than 5 in Storage Area
            self.cursor.execute(
                "SELECT PRODUCT_NAME, STOCKS FROM Inventory WHERE STOCKS < 5 AND LOCATION='Storage Area'"
            )
            low_stock_products = self.cursor.fetchall()

            # Add a notification for each product with low stock
            for product in low_stock_products:
                self.add_notification(
                    f'Stock alert: {product[0]} stock is low in Storage Area! (Quantity: {product[1]})')

            for product in low_stock_products:
                notification.notify(
                    title='Stock Alert',
                    message=f'Stock alert: {product[0]} stock is low in Storage Area! (Quantity: {product[1]})',
                    app_name='Your App Name',
                    timeout=10  # duration in seconds for the notification to stay on screen
                )

        except sqlite3.Error as e:
            messagebox.showerror('Error', f'Error checking low stock: {str(e)}')


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    root = ctk.CTk()
    app = AdminApp(root, username)
    root.mainloop()
