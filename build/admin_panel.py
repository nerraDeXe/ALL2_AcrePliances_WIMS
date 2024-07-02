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

        self.button2= ctk.CTkButton(left_frame, text="INVENTORY MANAGEMENT", fg_color='#FFFFFF',
                                                       text_color='#000000',
                                                       command=self.open_inventory_panel)
        self.button2.pack(pady=10)

        self.button3 = ctk.CTkButton(left_frame, text="PURCHASE ORDER", fg_color='#FFFFFF',
                                                   text_color='#000000',
                                                       command=self.open_purchase_order_panel )
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
        root.quit()
        root.destroy()
        subprocess.Popen(["python", "login.py"])

    def create_graph(self):
        # Create a graph in the left frame
        conn = sqlite3.connect('AcrePliances.db')
        cursor = conn.cursor()
        cursor.execute('SELECT PRODUCT_NAME, SUM(STOCKS) FROM Inventory GROUP BY PRODUCT_NAME')
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

        cursor.execute('SELECT COUNT(*) FROM tasks')
        total_tasks = cursor.fetchone()[0]

        conn.close()

        stats = {
            'Total Inventory Stocks': total_stocks,
            'Total Purchase Orders': total_purchase_orders,
            'Pending Sales Orders': total_sales_orders,
            'Remaining Product in Staging Area': product_sta,
            'Remaining Product in Storage Area': product_sto,
            'Remaining Tasks': total_tasks
        }

        industrial_colors = ['orange', 'light blue', 'light blue', 'light blue', 'light blue', 'light blue']
        white = ['white', 'white', 'white', 'white', 'white', 'white']
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
        self.load_notifications()

    def show_notifications_window(self):
        self.notification_window = ctk.CTkToplevel(self.root)
        self.notification_window.title('Notifications')
        self.notification_window.geometry('500x400')
        self.notification_window.resizable(0, 0)
        self.notification_window.attributes('-topmost', 'true')

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
    username = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    root = ctk.CTk()
    app = AdminApp(root, username)
    root.mainloop()
