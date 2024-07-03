from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, messagebox, BooleanVar
from PIL import Image, ImageTk
import sv_ttk
import sqlite3
import hashlib
import subprocess


class Database:
    def __init__(self, db_name='AcrePliances.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                USER_REAL_ID INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                roles TEXT NOT NULL CHECK(roles IN ('Administrator', 'Supervisor', 'Worker'))
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role_id INTEGER PRIMARY KEY,
                role_name TEXT NOT NULL UNIQUE)
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY,
                task_name TEXT NOT NULL,
                task_description TEXT,
                assigned_to TEXT NOT NULL,
                status TEXT,
                deadline DATE,
                FOREIGN KEY (assigned_to) REFERENCES workers (username))
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Inventory (
                PRODUCT_REAL_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                PRODUCT_NAME TEXT,
                PRODUCT_ID TEXT,
                STOCKS INTEGER,
                CATEGORY VARCHAR(30),
                PURCHASE_PRICE FLOAT,
                SELLING_PRICE FLOAT,
                LOCATION VARCHAR(30),
                INTERNAL_REFERENCE VARCHAR(30))
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchase_Orders (
                PURCHASE_ORDER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                PRODUCT_NAME VARCHAR(20),
                CATEGORY TEXT,
                QUANTITY INTEGER,
                VENDOR_ID INTEGER,
                DATETIME DATETIME,
                FOREIGN KEY(VENDOR_ID) REFERENCES Vendors(VENDOR_ID))
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales_Orders (
                ORDER_ID INTEGER PRIMARY KEY,
                PRODUCT_NAME VARCHAR(20),
                PRODUCT_ID TEXT,
                CATEGORY TEXT,
                QUANTITY INTEGER,
                DATE date,
                STORE_BRANCH TEXT)
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Vendors (
                VENDOR_ID INTEGER PRIMARY KEY,
                NAME VARCHAR(20),
                EMAIL VARCHAR(20),
                PHONE_NUMBER VARCHAR(10),
                COMPANY VARCHAR(20))
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Notifications (
                NOTIFICATION_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                DESCRIPTION TEXT,
                TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP)
        ''')

        # Create separate tables for supervisors and workers
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS supervisors (
                supervisor_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                FOREIGN KEY (username) REFERENCES users (username))
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS workers (
                worker_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                performance_rating INTEGER,
                FOREIGN KEY (username) REFERENCES users (username))
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS Shipped_Stock (
            SHIPPED_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PRODUCT_NAME TEXT,
            PRODUCT_ID TEXT,
            CATEGORY TEXT,
            QUANTITY INTEGER,
            DATE TEXT,
            STORE_BRANCH TEXT,
            SHIPPED_TIME TEXT)''')

        # Create product id counter
        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Product_Counter (
                    CATEGORY TEXT PRIMARY KEY,
                    LAST_PRODUCT_ID INTEGER NOT NULL)
                ''')

        self.conn.commit()

    def fetch_user_role(self, username, hashed_password):
        self.cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, hashed_password))
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()


class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title('ACREPLIANCES LOGIN')
        self.db = Database()
        self.setup_ui()

        self.fixed_admin_username = "admin"
        self.fixed_admin_password = "admin123"

    def setup_ui(self):
        self.root.geometry("901x540")
        self.root.configure(bg="#FFFFFF")

        self.canvas = Canvas(self.root, bg="#FFFFFF", height=540, width=901, bd=0, highlightthickness=0, relief="ridge")
        self.canvas.place(x=0, y=0)

        self.load_images()
        self.create_widgets()
        self.create_entries()
        self.create_buttons()

        sv_ttk.set_theme("light")
        self.root.resizable(False, False)

    def load_images(self):
        self.image_1 = PhotoImage(file=self.relative_to_assets("image_1.png"))
        self.canvas.create_image(450.0, 270.0, image=self.image_1)

        self.canvas.create_rectangle(338.0, 0.0, 901.0, 540.0, fill="#C30000", outline="")

        image_path = self.relative_to_assets("default-monochrome.png")
        original_image = Image.open(image_path)
        width, height = original_image.size
        resized_image = original_image.resize((width // 2, height // 2), Image.LANCZOS)
        self.acre_app = ImageTk.PhotoImage(resized_image)
        self.canvas.create_image(620.0, 100.0, image=self.acre_app)

    def create_widgets(self):
        self.canvas.create_text(468.0, 280.0, anchor="nw", text="Password", fill="#FFFFFF",
                                font=("Microsoft YaHei UI Light", 15))
        self.canvas.create_text(468.0, 172.0, anchor="nw", text="Username", fill="#FFFFFF",
                                font=("Microsoft YaHei UI Light", 15))
        self.canvas.create_text(468.0, 130.0, anchor="nw", text="WAREHOUSE INVENTORY MANAGEMENT SYSTEM", fill="#FFFFFF",
                                font=("Microsoft YaHei UI Light", 10))

    def create_entries(self):
        self.entry_bg_1 = PhotoImage(file=self.relative_to_assets("entry_1.png"))
        self.canvas.create_image(619.5, 235.5, image=self.entry_bg_1)
        self.entry_username = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_username.place(x=478.0, y=208.5, width=290.0, height=47.0)

        self.entry_bg_2 = PhotoImage(file=self.relative_to_assets("entry_2.png"))
        self.canvas.create_image(619.5, 339.5, image=self.entry_bg_2)
        self.entry_password = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0, show='*')
        self.entry_password.place(x=478.0, y=313.0, width=290.0, height=47.0)

        # Load icons for password visibility toggle
        self.show_icon = ImageTk.PhotoImage(Image.open("show_password.png"))
        self.hide_icon = ImageTk.PhotoImage(Image.open("hide_password.png"))

        self.show_password_var = BooleanVar(value=True)
        self.user_toggle_button = Button(self.root, image=self.show_icon,
                                         command=lambda: self.new_user_toggle_password(self.entry_password,
                                                                                       self.show_password_var,
                                                                                       self.user_toggle_button),
                                         borderwidth=0, highlightthickness=1, relief="flat", bg='#C30000')
        self.user_toggle_button.place(x=790, y=320, width=30, height=30)

    def create_buttons(self):
        self.button_image_1 = PhotoImage(file=self.relative_to_assets("button_1.png"))
        self.button_1 = Button(image=self.button_image_1, borderwidth=0, highlightthickness=0,
                               command=self.validate_login, relief="flat",
                               bg='#C40000', activebackground='#C40000')
        self.button_1.place(x=544.0, y=390.0, width=147.0, height=40.0)

    def relative_to_assets(self, path: str) -> Path:
        output_path = Path(__file__).parent
        assets_path = output_path / "assets/frame0"
        return assets_path / Path(path)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def new_user_toggle_password(self, password_entry, show_password_var, toggle_button):
        if show_password_var.get():
            password_entry.config(show='*')
            toggle_button.config(image=self.show_icon)
        else:
            password_entry.config(show='')
            toggle_button.config(image=self.hide_icon)
        show_password_var.set(not show_password_var.get())

    def validate_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        hashed_password = self.hash_password(password)

        result = self.db.fetch_user_role(username, hashed_password)

        if username == self.fixed_admin_username and password == self.fixed_admin_password:
            messagebox.showinfo("Login Successful", f"Welcome {username}! Your role is Administrator.")
            self.root.quit()
            self.root.destroy()
            subprocess.run(["python", "admin_panel.py", username])
        elif result:
            role = result[0]
            if role == 'Supervisor':
                messagebox.showinfo("Login Successful", f"Welcome {username}! Your role is {role}.")
                self.root.quit()
                self.root.destroy()
                subprocess.run(["python", "supervisor_panel.py", username])
            elif role == 'Worker':
                messagebox.showinfo("Login Successful", f"Welcome {username}! Your role is {role}.")
                self.root.quit()
                self.root.destroy()
                subprocess.run(["python", "worker_panel.py", username])
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")


if __name__ == "__main__":
    root = Tk()
    app = LoginApp(root)
    root.mainloop()
