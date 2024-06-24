import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class AdminApp:
    def __init__(self, root, username):
        self.connector3 = sqlite3.connect('vendor.db')
        self.cursor3 = self.connector3.cursor()

        self.connector3.execute(
            'CREATE TABLE IF NOT EXISTS Inventory (VENDOR_ID INTEGER PRIMARY KEY, NAME VARCHAR(20), '
            'EMAIL VARCHAR(20), PHONE_NUMBER VARCHAR(10), COMPANY VARCHAR(20))'
        )
        self.connector3.commit()

        self.root = root
        self.username = username
        self.root.title('Vendor List')
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')

        self.create_widgets()
        self.load_data()  # Load data initially

    def create_widgets(self):
        top_frame = tk.Frame(self.root, bg='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = tk.Label(top_frame, text="VENDOR DETAILS", font=("Helvetica", 16), bg='#BF2C37', fg='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        welcome_label = tk.Label(top_frame, text=f"Welcome, {self.username}", font=("Helvetica", 12), bg='#BF2C37', fg='white')
        welcome_label.pack(side=tk.LEFT, padx=20, pady=20)

        left_frame = tk.Frame(self.root, bg='#BF2C37')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)

        self.button1 = tk.Button(left_frame, text="ADD VENDOR'S INFORMATION", padx=30, pady=10, command=self.create_window)
        self.button1.pack(pady=10)

        self.button2 = tk.Button(left_frame, text="EDIT VENDOR'S DETAILS", padx=50, pady=10, command=self.edit_window)
        self.button2.pack(pady=10)

        self.button3 = tk.Button(left_frame, text="DELETE VENDOR'S INFORMATION", padx=25, pady=10, command=self.delete_vendor)
        self.button3.pack(pady=10)

        self.back_button = tk.Button(left_frame, text="Back", command=self.root.quit)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        vendor_details_label = tk.Label(main_frame, text="VENDOR DETAILS:", font=("Helvetica", 14), bg='white')
        vendor_details_label.pack(anchor=tk.W, pady=10)

        self.task_tree = ttk.Treeview(main_frame, columns=("Vendor ID", "Name", "Email", "Phone Number", "Company"),
                                      show='headings')
        self.task_tree.heading("Vendor ID", text="Vendor ID")
        self.task_tree.heading("Name", text="Name")
        self.task_tree.heading("Email", text="Email")
        self.task_tree.heading("Phone Number", text="Phone Number")
        self.task_tree.heading("Company", text="Company")
        self.task_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_data(self):
        self.task_tree.delete(*self.task_tree.get_children())  # Clear existing items

        self.cursor3.execute('SELECT * FROM Inventory')
        rows = self.cursor3.fetchall()

        for row in rows:
            self.task_tree.insert('', 'end', values=row)

    def create_window(self):
        self.extra_window = tk.Toplevel(self.root)
        self.extra_window.title('Add Vendor')
        self.extra_window.geometry('600x600')

        title_label = tk.Label(self.extra_window, text="ADD NEW VENDOR'S DETAIL", font=("Helvetica", 14))
        title_label.pack(pady=20)

        # Vendor Name
        name_frame = tk.Frame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = tk.Label(name_frame, text="Name:")
        name_label.pack(side=tk.LEFT)
        self.name_entry = tk.Entry(name_frame)
        self.name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Vendor Email
        email_frame = tk.Frame(self.extra_window)
        email_frame.pack(pady=5, padx=10, fill=tk.X)
        email_label = tk.Label(email_frame, text="Email:")
        email_label.pack(side=tk.LEFT)
        self.email_entry = tk.Entry(email_frame)
        self.email_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Contact Number
        contact_frame = tk.Frame(self.extra_window)
        contact_frame.pack(pady=5, padx=10, fill=tk.X)
        contact_label = tk.Label(contact_frame, text="Phone Number:")
        contact_label.pack(side=tk.LEFT)
        self.contact_entry = tk.Entry(contact_frame)
        self.contact_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Business Name
        company_frame = tk.Frame(self.extra_window)
        company_frame.pack(pady=5, padx=10, fill=tk.X)
        company_label = tk.Label(company_frame, text="Company:")
        company_label.pack(side=tk.LEFT)
        self.company_entry = tk.Entry(company_frame)
        self.company_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        add_button = tk.Button(self.extra_window, text="Add Vendor", command=self.add_vendor)
        add_button.pack(pady=10)

        clear_button = tk.Button(self.extra_window, text="Clear", command=self.clear_entries)
        clear_button.pack(pady=10)

    def add_vendor(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        phone = self.contact_entry.get()
        company = self.company_entry.get()

        if name and email and phone and company:
            self.cursor3.execute(
                'INSERT INTO Inventory (NAME, EMAIL, PHONE_NUMBER, COMPANY) VALUES (?, ?, ?, ?)',
                (name, email, phone, company)
            )
            self.connector3.commit()

            self.load_data()  # Reload data into TreeView
            self.clear_entries()
        else:
            messagebox.showwarning("Input Error", "All fields are required")

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.company_entry.delete(0, tk.END)

    def edit_window(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No vendor selected")
            return

        item = self.task_tree.item(selected_item)
        values = item['values']

        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title('Edit Vendor')
        self.edit_window.geometry('600x600')

        title_label = tk.Label(self.edit_window, text="EDIT VENDOR'S DETAILS", font=("Helvetica", 14))
        title_label.pack(pady=20)

        # Vendor Name
        name_frame = tk.Frame(self.edit_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = tk.Label(name_frame, text="Name:")
        name_label.pack(side=tk.LEFT)
        self.name_edit_entry = tk.Entry(name_frame)
        self.name_edit_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.name_edit_entry.insert(0, values[1])

        # Vendor Email
        email_frame = tk.Frame(self.edit_window)
        email_frame.pack(pady=5, padx=10, fill=tk.X)
        email_label = tk.Label(email_frame, text="Email:")
        email_label.pack(side=tk.LEFT)
        self.email_edit_entry = tk.Entry(email_frame)
        self.email_edit_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.email_edit_entry.insert(0, values[2])

        # Contact Number
        contact_frame = tk.Frame(self.edit_window)
        contact_frame.pack(pady=5, padx=10, fill=tk.X)
        contact_label = tk.Label(contact_frame, text="Phone Number:")
        contact_label.pack(side=tk.LEFT)
        self.contact_edit_entry = tk.Entry(contact_frame)
        self.contact_edit_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.contact_edit_entry.insert(0, values[3])

        # Business Name
        company_frame = tk.Frame(self.edit_window)
        company_frame.pack(pady=5, padx=10, fill=tk.X)
        company_label = tk.Label(company_frame, text="Company:")
        company_label.pack(side=tk.LEFT)
        self.company_edit_entry = tk.Entry(company_frame)
        self.company_edit_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.company_edit_entry.insert(0, values[4])

        save_button = tk.Button(self.edit_window, text="Save Changes", command=lambda: self.save_edit(selected_item))
        save_button.pack(pady=10)

        clear_button = tk.Button(self.edit_window, text="Clear", command=self.clear_edit_entries)
        clear_button.pack(pady=10)

    def save_edit(self, selected_item):
        name = self.name_edit_entry.get()
        email = self.email_edit_entry.get()
        phone = self.contact_edit_entry.get()
        company = self.company_edit_entry.get()

        if name and email and phone and company:
            vendor_id = self.task_tree.item(selected_item)['values'][0]
            self.cursor3.execute(
                'UPDATE Inventory SET NAME = ?, EMAIL = ?, PHONE_NUMBER = ?, COMPANY = ? WHERE VENDOR_ID = ?',
                (name, email, phone, company, vendor_id)
            )
            self.connector3.commit()

            self.load_data()  # Reload data into TreeView
            self.edit_window.destroy()
        else:
            messagebox.showwarning("Input Error", "All fields are required")

    def clear_edit_entries(self):
        self.name_edit_entry.delete(0, tk.END)
        self.email_edit_entry.delete(0, tk.END)
        self.contact_edit_entry.delete(0, tk.END)
        self.company_edit_entry.delete(0, tk.END)

    def delete_vendor(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No vendor selected")
            return

        vendor_id = self.task_tree.item(selected_item)['values'][0]
        self.cursor3.execute('DELETE FROM Inventory WHERE VENDOR_ID = ?', (vendor_id,))
        self.connector3.commit()

        self.load_data()  # Reload data into TreeView


if __name__ == '__main__':
    username = "Admin"
    root = tk.Tk()
    app = AdminApp(root, username)
    root.mainloop()
