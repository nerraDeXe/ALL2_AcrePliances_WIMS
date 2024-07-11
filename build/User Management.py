import sqlite3
import tkinter as tk
from tkinter import Toplevel, StringVar, BooleanVar, Label, Entry, Button, messagebox as mb
from PIL import Image, ImageTk
import hashlib
import customtkinter as ctk
from tkinter import ttk, messagebox
import pytz
from datetime import datetime, timezone
import subprocess


class UserApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect("AcrePliances.db")
        self.cursor = self.connector.cursor()

        self.username = username
        self.root = root
        self.root.title("User Management")
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')
        self.root.resizable(0, 0)

        # Load icons for password visibility toggle
        self.show_icon = ImageTk.PhotoImage(Image.open("show_password.png"))
        self.hide_icon = ImageTk.PhotoImage(Image.open("hide_password.png"))

        self.create_main_window()
        self.load_users()

    def create_main_window(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="USER MANAGEMENT", font=("Helvetica", 16, 'bold'),
                                   text_color='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        self.notification_image = ImageTk.PhotoImage(Image.open("nored.png"))
        self.notification_button = tk.Button(top_frame, image=self.notification_image, bg='white',
                                             activebackground='darkred', command=self.show_notifications_window)
        self.notification_button.pack(side=tk.RIGHT, padx=20, pady=20)
        left_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)

        self.back_button = ctk.CTkButton(left_frame, text="BACK", command=self.close_subpanel)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = ctk.CTkFrame(self.root, fg_color='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.user_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.user_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        task_details_label = ctk.CTkLabel(self.user_frame, text="Task Details:", font=("Helvetica", 20, 'bold'),
                                          text_color='black')
        task_details_label.pack(anchor=tk.NW, pady=0)

        self.user_table = ttk.Treeview(self.user_frame,
                                       columns=('ID', 'Username', 'Role'), show='headings')
        self.user_table.heading('ID', text='ID')
        self.user_table.heading('Username', text='Username')
        self.user_table.heading('Role', text='Role')

        self.user_table.column('#0', width=0)
        self.user_table.column('#1', width=50)
        self.user_table.column('#2', width=200)
        self.user_table.column('#3', width=150)

        self.user_table.pack(fill=tk.BOTH, expand=False, padx=0, pady=0)

        self.create_user_management_buttons(left_frame)

    def load_users(self):
        self.user_table.delete(*self.user_table.get_children())

        self.cursor.execute('SELECT USER_REAL_ID, username, roles FROM users')
        rows = self.cursor.fetchall()

        for row in rows:
            self.user_table.insert('', 'end', values=row)

    def create_user_management_buttons(self, left_frame):
        self.add_user_button = ctk.CTkButton(left_frame, text="ADD USER", fg_color='#FFFFFF', text_color='#000000',
                                             command=self.add_user)
        self.add_user_button.pack(pady=10)

        self.delete_user_button = ctk.CTkButton(left_frame, text="DELETE USER", fg_color='#FFFFFF', text_color='#000000',
                                                command=self.delete_user)
        self.delete_user_button.pack(pady=10)



    def close_subpanel(self):
        self.root.destroy()

    def add_user(self):
        add_user_window = Toplevel(self.root)
        add_user_window.title("Add User")
        add_user_window.geometry("400x300")
        add_user_window.resizable(False, False)

        username_var = StringVar()
        password_var = StringVar()
        role_var = StringVar()
        show_password_var = BooleanVar(value=False)

        Label(add_user_window, text="Username").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        Entry(add_user_window, textvariable=username_var).grid(row=0, column=1, padx=10, pady=5)

        Label(add_user_window, text="Password").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        password_entry = Entry(add_user_window, textvariable=password_var, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        user_toggle_button = Button(add_user_window, image=self.show_icon,
                                    command=lambda: self.new_user_toggle_password(password_entry, show_password_var,
                                                                                  user_toggle_button))
        user_toggle_button.grid(row=1, column=2, padx=10, pady=5)

        Label(add_user_window, text="Role:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        ttk.OptionMenu(add_user_window, role_var, 'Supervisor', 'Supervisor', 'Worker').grid(row=2, column=1, padx=10,
                                                                                             pady=5)

        def save_user():

            usernameA = username_var.get()
            password = password_var.get()
            role = role_var.get()
            if usernameA and password and role:
                try:
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()
                    conn = sqlite3.connect('AcrePliances.db')
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO users (username, password, roles) VALUES (?, ?, ?)',
                                   (usernameA, hashed_password, role))
                    conn.commit()

                    if role == 'Supervisor':
                        cursor.execute('INSERT INTO supervisors (username) VALUES (?)', (usernameA,))
                    elif role == 'Worker':
                        cursor.execute('INSERT INTO workers (username) VALUES (?)', (usernameA,))
                    conn.commit()

                    mb.showinfo('User added', 'The user was successfully added')
                    self.load_users()
                except sqlite3.Error as e:
                    mb.showerror('Database Error', f'Error: {e}')
                finally:
                    conn.close()
                add_user_window.destroy()
            else:
                mb.showerror('Error', 'All fields are required')

        Button(add_user_window, text="Save", command=save_user).grid(row=3, column=1, padx=10, pady=15)

    def delete_user(self):
        selected_item = self.user_table.selection()
        if not selected_item:
            mb.showerror('Error', 'No user selected')
            return

        user_data = self.user_table.item(selected_item)['values']
        user_id = user_data[0]

        confirm = mb.askyesno('Confirm Delete', 'Are you sure you want to delete this user?')
        if confirm:
            try:
                conn = sqlite3.connect('AcrePliances.db')
                cursor = conn.cursor()

                cursor.execute('DELETE FROM users WHERE USER_REAL_ID = ?', (user_id,))
                cursor.execute(
                    'DELETE FROM supervisors WHERE username = (SELECT username FROM users WHERE USER_REAL_ID = ?)',
                    (user_id,))
                cursor.execute(
                    'DELETE FROM workers WHERE username = (SELECT username FROM users WHERE USER_REAL_ID = ?)',
                    (user_id,))
                conn.commit()

                mb.showinfo('User deleted', 'The user was successfully deleted')
                self.load_users()
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

    def add_notification(self, description):
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION, TIMESTAMP) VALUES (?, ?)',
                            (description, timestamp))
        self.connector.commit()

    def show_notifications_window(self):
        subprocess.Popen(["python", "Notifications.py"])

if __name__ == "__main__":
    root = tk.Tk()
    app = UserApp(root, username="Admin")
    root.mainloop()