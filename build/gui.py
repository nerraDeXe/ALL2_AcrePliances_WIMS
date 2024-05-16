from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, Checkbutton, BooleanVar, messagebox
from PIL import Image, ImageTk
import sv_ttk
import sqlite3

# Create a new SQLite database or connect to an existing one
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create a table for users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Administrator', 'Supervisor', 'Worker'))
)
''')


conn.close()

# Define paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets/frame0"


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


# Initialize window
window = Tk()
window.geometry("901x540")
window.configure(bg="#FFFFFF")

# Create canvas
canvas = Canvas(window, bg="#FFFFFF", height=540, width=901, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

# Load and place images
image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
canvas.create_image(450.0, 270.0, image=image_1)

# Create red rectangle
canvas.create_rectangle(338.0, 0.0, 901.0, 540.0, fill="#C30000", outline="")

# Open the image file
image_path = relative_to_assets("default-monochrome.png")
original_image = Image.open(image_path)

# AcrePliances Logo Resized
width, height = original_image.size
new_width = width // 2
new_height = height // 2
resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)

# Convert the resized image to a PhotoImage object
acre_app = ImageTk.PhotoImage(resized_image)
canvas.create_image(620.0, 100.0, image=acre_app)

# Create and place entry fields
entry_bg_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
canvas.create_image(619.5, 339.5, image=entry_bg_1)
entry_1 = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0, show='*')
entry_1.place(x=478.0, y=315.0, width=283.0, height=47.0)

entry_bg_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
canvas.create_image(619.5, 235.5, image=entry_bg_2)
entry_2 = Entry(bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
entry_2.place(x=478.0, y=211.0, width=283.0, height=47.0)

# Create text labels
canvas.create_text(468.0, 280.0, anchor="nw", text="Password", fill="#FFFFFF", font=("Microsoft YaHei UI Light", 15))
canvas.create_text(468.0, 172.0, anchor="nw", text="Username", fill="#FFFFFF", font=("Microsoft YaHei UI Light", 15))
canvas.create_text(468.0, 130.0, anchor="nw", text="WAREHOUSE INVENTORY MANAGEMENT SYSTEM", fill="#FFFFFF",
                   font=("Microsoft YaHei UI Light", 10))


# Function to toggle password visibility
def toggle_password():
    if show_password.get():
        entry_1.config(show='')
    else:
        entry_1.config(show='*')


# Add checkbox to toggle password visibility
show_password = BooleanVar()
checkbutton = Checkbutton(window, text="Show Password", variable=show_password, command=toggle_password, bg='#C30000',
                          fg='white')
checkbutton.place(x=560.0, y=370.0)


# Function to validate login
def validate_login():
    username = entry_2.get()
    password = entry_1.get()

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        role = result[0]
        messagebox.showinfo("Login Successful", f"Welcome {username}! Your role is {role}.")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

    conn.close()


# Create and place button
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
button_1 = Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=validate_login, relief="flat",
                  bg='#C40000', activebackground='#C40000')
button_1.place(x=544.0, y=410.0, width=147.0, height=40.0)

sv_ttk.set_theme("light")

# Finalize window settings
window.resizable(False, False)
window.mainloop()
