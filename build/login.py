from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, Checkbutton, BooleanVar, messagebox
from PIL import Image, ImageTk
import sv_ttk
import sqlite3
import hashlib
import subprocess


class Database:
    def __init__(self, db_name='users.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Administrator', 'Supervisor', 'Worker'))
        )
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
        self.db = Database()
        self.setup_ui()

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
        self.canvas.create_image(619.5, 339.5, image=self.entry_bg_1)
        self.entry_password = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0, show='*')
        self.entry_password.place(x=478.0, y=315.0, width=283.0, height=47.0)

        self.entry_bg_2 = PhotoImage(file=self.relative_to_assets("entry_2.png"))
        self.canvas.create_image(619.5, 235.5, image=self.entry_bg_2)
        self.entry_username = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.entry_username.place(x=478.0, y=211.0, width=283.0, height=47.0)

        self.show_password = BooleanVar()
        self.checkbutton = Checkbutton(self.root, text="Show Password", variable=self.show_password,
                                       command=self.toggle_password, bg='#C30000', fg='white')
        self.checkbutton.place(x=560.0, y=370.0)

    def create_buttons(self):
        self.button_image_1 = PhotoImage(file=self.relative_to_assets("button_1.png"))
        self.button_1 = Button(image=self.button_image_1, borderwidth=0, highlightthickness=0,
                               command=self.validate_login, relief="flat",
                               bg='#C40000', activebackground='#C40000')
        self.button_1.place(x=544.0, y=410.0, width=147.0, height=40.0)

    def relative_to_assets(self, path: str) -> Path:
        output_path = Path(__file__).parent
        assets_path = output_path / "assets/frame0"
        return assets_path / Path(path)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def toggle_password(self):
        if self.show_password.get():
            self.entry_password.config(show='')
        else:
            self.entry_password.config(show='*')

    def validate_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        hashed_password = self.hash_password(password)

        result = self.db.fetch_user_role(username, hashed_password)

        if result:
            role = result[0]

            if role == 'Administrator':
                messagebox.showinfo("Login Successful", f"Welcome {username}! Your role is {role}.")
                self.root.quit()
                self.root.destroy()
                subprocess.run(["python", "admin_panel.py", username])
            else:
                messagebox.showinfo("Login Successful", f"Welcome {username}! Your role is {role}.")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")


if __name__ == "__main__":
    root = Tk()
    app = LoginApp(root)
    root.mainloop()
