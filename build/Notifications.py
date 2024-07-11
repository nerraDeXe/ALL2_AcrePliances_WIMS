import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from ttkthemes import ThemedTk
import sqlite3
from datetime import datetime
import pytz

class NotificationApp:
    def __init__(self, root):
        self.root = root
        self.connector = sqlite3.connect('AcrePliances.db')
        self.cursor = self.connector.cursor()
        self.setup_ui()

    def setup_ui(self):
        self.root.title('Notifications')
        self.root.geometry('600x500')
        self.root.resizable(0, 0)
        self.root.configure(bg='#1E1E1E')

        # Set customtkinter theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        notification_label = ctk.CTkLabel(self.root, text="Notifications",
                                          font=("Helvetica", 18, 'bold'), text_color="#FFFFFF")
        notification_label.pack(pady=20)

        container = ctk.CTkFrame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.notification_canvas = tk.Canvas(container, bg='#1E1E1E', highlightthickness=0)
        self.notification_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ctk.CTkScrollbar(container, orientation=tk.VERTICAL, command=self.notification_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notification_canvas.configure(yscrollcommand=scrollbar.set)
        self.notification_frame = ctk.CTkFrame(self.notification_canvas)
        self.notification_canvas.create_window((0, 0), window=self.notification_frame, anchor="nw")

        self.notification_frame.bind("<Configure>", lambda e: self.notification_canvas.configure(scrollregion=self.notification_canvas.bbox("all")))

        self.load_notifications()

        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=10, fill=tk.X)

        delete_button = ctk.CTkButton(button_frame, text="Dismiss Selected",
                                      command=self.delete_selected_notification,
                                      fg_color="#BF2C37")
        delete_button.pack(side=tk.LEFT, padx=20, pady=10, expand=True)

        delete_all_button = ctk.CTkButton(button_frame, text="Dismiss All",
                                          command=self.delete_all_notifications,
                                          fg_color="#BF2C37")
        delete_all_button.pack(side=tk.RIGHT, padx=20, pady=10, expand=True)

    def delete_selected_notification(self):
        selected_notifications = [child for child in self.notification_frame.winfo_children() if child.cget('fg_color') == '#BF2C37']

        if not selected_notifications:
            messagebox.showwarning('No notification selected!', 'Please select a notification to delete.')
            return

        confirm_delete = messagebox.askyesno('Confirm Delete',
                                             'Are you sure you want to delete the selected notification(s)?')
        if not confirm_delete:
            return

        for notification in selected_notifications:
            try:
                notification_id = notification.notification_id
                self.cursor.execute('DELETE FROM Notifications WHERE NOTIFICATION_ID=?', (notification_id,))
                self.connector.commit()
            except sqlite3.Error as e:
                messagebox.showerror('Error', f'Error deleting notification: {str(e)}')
                return

        self.load_notifications()

    def delete_all_notifications(self):
        confirm_delete = messagebox.askyesno('Confirm Delete',
                                             'Are you sure you want to delete all notifications?')
        if not confirm_delete:
            return

        try:
            self.cursor.execute('DELETE FROM Notifications')
            self.connector.commit()
        except sqlite3.Error as e:
            messagebox.showerror('Error', f'Error deleting all notifications: {str(e)}')
            return

        self.load_notifications()

    def load_notifications(self):
        for widget in self.notification_frame.winfo_children():
            widget.destroy()

        try:
            self.cursor.execute("SELECT * FROM Notifications ORDER BY TIMESTAMP DESC")
            notifications = self.cursor.fetchall()

            for notification in notifications:
                timestamp = datetime.strptime(notification[2], '%Y-%m-%d %H:%M:%S')
                utc_timezone = pytz.utc
                local_timezone = pytz.timezone('Asia/Singapore')
                utc_timestamp = utc_timezone.localize(timestamp)
                local_timestamp = utc_timestamp.astimezone(local_timezone)
                formatted_timestamp = local_timestamp.strftime('%Y-%m-%d %H:%M:%S')

                notification_frame = ctk.CTkFrame(self.notification_frame, fg_color="#2E2E2E", corner_radius=10)
                notification_frame.pack(fill=tk.X, pady=5, padx=10)
                notification_frame.bind("<Button-1>", lambda e, nf=notification_frame: self.select_notification(nf))

                message_label = ctk.CTkLabel(notification_frame, text=notification[1], font=("Helvetica", 12), text_color="#FFFFFF", wraplength=400, justify=tk.LEFT)
                message_label.pack(side=tk.LEFT, padx=10, pady=10)

                timestamp_label = ctk.CTkLabel(notification_frame, text=formatted_timestamp, font=("Helvetica", 10), text_color="#AAAAAA")
                timestamp_label.pack(side=tk.RIGHT, padx=10, pady=10)

                notification_frame.notification_id = notification[0]

        except sqlite3.Error as e:
            messagebox.showerror('Error', f'Error loading notifications: {str(e)}')

    def select_notification(self, frame):
        current_color = frame.cget("fg_color")
        new_color = "#BF2C37" if current_color == "#2E2E2E" else "#2E2E2E"
        frame.configure(fg_color=new_color)


if __name__ == "__main__":
    root = ThemedTk(theme="radiance")  # Use ThemedTk for better modern themes
    app = NotificationApp(root)
    root.mainloop()
