import subprocess
import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk
import pytz


class VendorApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect('AcrePliances.db')
        self.cursor = self.connector.cursor()
        self.connector.commit()

        self.root = root
        self.username = username
        self.root.title('Vendor Details Management')
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')
        self.root.resizable(0, 0)

        self.create_vendor_widgets()
        self.load_vendor_data()

    def create_vendor_widgets(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="VENDOR DETAILS MANAGEMENT", font=("Helvetica", 16),
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
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)

        self.add_vendor_button = ctk.CTkButton(left_frame, text="ADD VENDOR'S INFORMATION", fg_color='#FFFFFF',
                                               text_color='#000000', command=self.create_vendor_window)
        self.add_vendor_button.pack(pady=10)

        self.edit_vendor_button = ctk.CTkButton(left_frame, text="EDIT VENDOR'S DETAILS", fg_color='#FFFFFF',
                                                text_color='#000000', command=self.edit_vendor_window)
        self.edit_vendor_button.pack(pady=10)

        self.delete_vendor_button = ctk.CTkButton(left_frame, text="DELETE VENDOR'S INFORMATION", fg_color='#FFFFFF',
                                                  text_color='#000000', command=self.delete_vendor)
        self.delete_vendor_button.pack(pady=10)

        self.back_button = ctk.CTkButton(left_frame, text="Back", command=self.close_subpanel)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = ctk.CTkFrame(self.root, fg_color='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.vendor_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.vendor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        vendor_details_label = ctk.CTkLabel(self.vendor_frame, text="Vendor Details:", font=("Helvetica", 20, 'bold'),
                                            text_color='black')
        vendor_details_label.pack(anchor=tk.NW, pady=0)

        self.vendor_tree = ttk.Treeview(self.vendor_frame, columns=("ID", "Name", "Email", "Phone", "Company"),
                                        show='headings')
        self.vendor_tree.heading("ID", text="ID")
        self.vendor_tree.heading("Name", text="Name")
        self.vendor_tree.heading("Email", text="Email")
        self.vendor_tree.heading("Phone", text="Phone")
        self.vendor_tree.heading("Company", text="Company")
        self.vendor_tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

    def close_subpanel(self):
        self.root.destroy()  # Close the main window and all associated frames

    def load_vendor_ids(self):
        self.cursor.execute('SELECT VENDOR_ID FROM Vendors')
        vendor_ids = [row[0] for row in self.cursor.fetchall()]
        return vendor_ids

    def load_vendor_data(self):
        self.vendor_tree.delete(*self.vendor_tree.get_children())

        self.cursor.execute('SELECT * FROM Vendors')
        rows = self.cursor.fetchall()

        for row in rows:
            self.vendor_tree.insert('', 'end', values=row)

    def create_vendor_window(self):
        self.extra_window = ctk.CTkToplevel(self.root)  # Use self.root as the parent
        self.extra_window.title('Add Vendor')
        self.extra_window.geometry('600x600')
        self.extra_window.attributes('-topmost', True)

        title_label = ctk.CTkLabel(self.extra_window, text="ADD NEW VENDOR", font=("Helvetica", 14))
        title_label.pack(pady=20)

        # Vendor Name
        name_frame = ctk.CTkFrame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = ctk.CTkLabel(name_frame, text="Vendor Name:")
        name_label.pack(side=tk.LEFT)
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Email
        email_frame = ctk.CTkFrame(self.extra_window)
        email_frame.pack(pady=5, padx=10, fill=tk.X)
        email_label = ctk.CTkLabel(email_frame, text="Email:")
        email_label.pack(side=tk.LEFT)
        self.email_entry = ctk.CTkEntry(email_frame)
        self.email_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Phone Number
        phone_frame = ctk.CTkFrame(self.extra_window)
        phone_frame.pack(pady=5, padx=10, fill=tk.X)
        phone_label = ctk.CTkLabel(phone_frame, text="Phone Number:")
        phone_label.pack(side=tk.LEFT)
        self.phone_entry = ctk.CTkEntry(phone_frame)
        self.phone_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Company
        company_frame = ctk.CTkFrame(self.extra_window)
        company_frame.pack(pady=5, padx=10, fill=tk.X)
        company_label = ctk.CTkLabel(company_frame, text="Company:")
        company_label.pack(side=tk.LEFT)
        self.company_entry = ctk.CTkEntry(company_frame)
        self.company_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        add_button = ctk.CTkButton(self.extra_window, text="Add Vendor", command=self.add_vendor)
        add_button.pack(pady=10)

        clear_button = ctk.CTkButton(self.extra_window, text="Clear", command=self.clear_vendor_entries)
        clear_button.pack(pady=10)

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
            self.load_vendor_data()
            self.add_notification(f'Vendor {name} added.')
            messagebox.showinfo('Success', 'Vendor added successfully!')
            self.extra_window.destroy()
        else:
            messagebox.showwarning('Error', 'Please fill in all fields.')

    def edit_vendor_window(self):
        selected_item = self.vendor_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select a vendor to edit.')
            return

        vendor_id = self.vendor_tree.item(selected_item)['values'][0]
        self.extra_window = ctk.CTkToplevel(self.root)
        self.extra_window.title('Edit Vendor')
        self.extra_window.geometry('600x600')
        self.extra_window.attributes('-topmost', True)

        title_label = ctk.CTkLabel(self.extra_window, text="EDIT VENDOR", font=("Helvetica", 14))
        title_label.pack(pady=20)

        self.cursor.execute('SELECT * FROM Vendors WHERE VENDOR_ID=?', (vendor_id,))
        vendor = self.cursor.fetchone()

        self.edit_vendor_id = vendor[0]

        # Vendor Name
        name_frame = ctk.CTkFrame(self.extra_window)
        name_frame.pack(pady=5, padx=10, fill=tk.X)
        name_label = ctk.CTkLabel(name_frame, text="Vendor Name:")
        name_label.pack(side=tk.LEFT)
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.insert(0, vendor[1])
        self.name_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Email
        email_frame = ctk.CTkFrame(self.extra_window)
        email_frame.pack(pady=5, padx=10, fill=tk.X)
        email_label = ctk.CTkLabel(email_frame, text="Email:")
        email_label.pack(side=tk.LEFT)
        self.email_entry = ctk.CTkEntry(email_frame)
        self.email_entry.insert(0, vendor[2])
        self.email_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Phone Number
        phone_frame = ctk.CTkFrame(self.extra_window)
        phone_frame.pack(pady=5, padx=10, fill=tk.X)
        phone_label = ctk.CTkLabel(phone_frame, text="Phone Number:")
        phone_label.pack(side=tk.LEFT)
        self.phone_entry = ctk.CTkEntry(phone_frame)
        self.phone_entry.insert(0, vendor[3])
        self.phone_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Company
        company_frame = ctk.CTkFrame(self.extra_window)
        company_frame.pack(pady=5, padx=10, fill=tk.X)
        company_label = ctk.CTkLabel(company_frame, text="Company:")
        company_label.pack(side=tk.LEFT)
        self.company_entry = ctk.CTkEntry(company_frame)
        self.company_entry.insert(0, vendor[4])
        self.company_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        save_button = ctk.CTkButton(self.extra_window, text="Save Changes", command=self.save_vendor_changes)
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
                self.load_vendor_data()
                self.add_notification(f'Updated details for Vendor {name}.')
                messagebox.showinfo('Success', 'Vendor updated successfully!')
                self.extra_window.destroy()
            except Exception as e:
                messagebox.showerror('Error', f'Error updating vendor: {str(e)}')
        else:
            messagebox.showwarning('Error', 'Please fill in all fields.')

    def delete_vendor(self):
        selected_item = self.vendor_tree.selection()
        if not selected_item:
            messagebox.showwarning('Error', 'Please select a vendor to delete.')
            return

        confirm = messagebox.askyesno('Confirm Delete', 'Are you sure you want to delete the selected vendor?')
        if not confirm:
            return

        vendor_id = self.vendor_tree.item(selected_item)['values'][0]
        try:
            self.cursor.execute('DELETE FROM Vendors WHERE VENDOR_ID=?', (vendor_id,))
            self.connector.commit()
            self.load_vendor_data()
            self.add_notification(f'Deleted Vendor with ID {vendor_id}.')
            messagebox.showinfo('Success', 'Vendor deleted successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'Error deleting vendor: {str(e)}')

    def clear_vendor_entries(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.company_entry.delete(0, tk.END)

    ################################################NOTIFICAITON FUNCTIONS##############################################
    def add_notification(self, description):
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION) VALUES (?)', (description,))
        self.connector.commit()

    def show_notifications_window(self):
        subprocess.Popen(["python", "Notifications.py"])


if __name__ == "__main__":
    root = ctk.CTk()
    app = VendorApp(root, "Admin")
    root.mainloop()
