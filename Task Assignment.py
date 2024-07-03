import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
from datetime import datetime
import sqlite3
import pytz
from tkcalendar import DateEntry
from fpdf import FPDF

class AssignmentApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect("AcrePliances.db")
        self.cursor = self.connector.cursor()

        self.username = username
        self.root = root
        self.root.title("TASK ASSIGNMENT")
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')
        self.root.resizable(0, 0)

        self.create_main_window()
        self.load_tasks()

    def create_main_window(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="WORKER TASK MANAGEMENT", font=("Helvetica", 16, 'bold'),
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

        self.task_button = ctk.CTkButton(left_frame, text="ASSIGN TASK", fg_color='#FFFFFF', text_color='#000000',
                                         command=self.open_assign_task_window)
        self.task_button.pack(pady=10)

        self.refresh_button = ctk.CTkButton(left_frame, text="REFRESH TASKS", fg_color='#FFFFFF', text_color='#000000',
                                            command=self.load_tasks)
        self.refresh_button.pack(pady=10)

        self.rate_performance_button = ctk.CTkButton(left_frame, text="RATE PERFORMANCE", fg_color='#FFFFFF', text_color='#000000',
                                         command=self.open_rate_performance_window)
        self.rate_performance_button.pack(pady=10)

        self.generate_report_button = ctk.CTkButton(left_frame, text="GENERATE REPORT", fg_color='#FFFFFF', text_color='#000000',
                                            command=self.generate_performance_report)
        self.generate_report_button.pack(pady=10)

        self.back_button = ctk.CTkButton(left_frame, text="BACK", command=self.close_subpanel)
        self.back_button.pack(side=tk.BOTTOM, pady=20)

        main_frame = ctk.CTkFrame(self.root, fg_color='white')
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.task_frame = ctk.CTkFrame(main_frame, fg_color='white')
        self.task_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        task_details_label = ctk.CTkLabel(self.task_frame, text="Task Details:", font=("Helvetica", 20, 'bold'),
                                          text_color='black')
        task_details_label.pack(anchor=tk.NW, pady=0)

        self.task_tree = ttk.Treeview(self.task_frame,
                                      columns=("Task ID", "Task Name", "Description", "Assigned To", "Status",
                                               "Deadline"),
                                      show='headings')
        self.task_tree.heading("Task ID", text="Task ID")
        self.task_tree.heading("Task Name", text="Task Name")
        self.task_tree.heading("Description", text="Description")
        self.task_tree.heading("Assigned To", text="Assigned To")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.heading("Deadline", text="Deadline")
        self.task_tree.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Adjust column widths
        self.adjust_column_widths()

    def adjust_column_widths(self):
        # Calculate available width for remaining columns
        total_width = self.task_frame.winfo_width()
        visible_columns = [col for col in self.task_tree["columns"] if col != "PRODUCT_REAL_ID"]
        column_count = len(visible_columns)

        if column_count > 0 and total_width > 0:
            equal_width = total_width // column_count

            for col in visible_columns:
                self.task_tree.column(col, width=equal_width)

    def load_tasks(self):
        for i in self.task_tree.get_children():
            self.task_tree.delete(i)
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        for row in rows:
            self.task_tree.insert("", tk.END, values=row)

    def open_assign_task_window(self):
        self.assign_task_window = ctk.CTkToplevel(self.root)
        self.assign_task_window.title("Assign Task")
        self.assign_task_window.geometry('600x500')
        self.assign_task_window.attributes('-topmost', True)

        title_label = ctk.CTkLabel(self.assign_task_window, text="ASSIGN TASK", font=("Helvetica", 14))
        title_label.pack(pady=20)

        # Task Name Frame
        task_name_frame = ctk.CTkFrame(self.assign_task_window)
        task_name_frame.pack(pady=5, padx=10, fill=tk.X)
        task_name_label = ctk.CTkLabel(task_name_frame, text="Task Name:")
        task_name_label.pack(side=tk.LEFT)

        # Task Name Options
        task_names = [
            "Product Allocation",
            "Delivery Product to Staging Area",
            "Delivery Product to Storage Area",
            "Delivery Product to Shipping Area",
            "Quality Check",
            "Inventory Update",
            "Order Processing",
            "Packaging",
            "Dispatch"
        ]

        self.task_name_combobox = ctk.CTkComboBox(task_name_frame, values=task_names)
        self.task_name_combobox.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Task Description
        task_description_frame = ctk.CTkFrame(self.assign_task_window)
        task_description_frame.pack(pady=5, padx=10, fill=tk.X)
        task_description_label = ctk.CTkLabel(task_description_frame, text="Task Description:")
        task_description_label.pack(side=tk.LEFT)
        self.task_description_entry = ctk.CTkEntry(task_description_frame)
        self.task_description_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Assign To (User ID)
        assign_to_frame = ctk.CTkFrame(self.assign_task_window)
        assign_to_frame.pack(pady=5, padx=10, fill=tk.X)
        assign_to_label = ctk.CTkLabel(assign_to_frame, text="Assign To (User ID):")
        assign_to_label.pack(side=tk.LEFT)

        # Create dropdown list for usernames
        self.cursor.execute("SELECT username FROM workers")
        usernames = [row[0] for row in self.cursor.fetchall()]
        self.assign_to_combobox = ttk.Combobox(assign_to_frame, values=usernames)
        self.assign_to_combobox.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Deadline
        deadline_frame = ctk.CTkFrame(self.assign_task_window)
        deadline_frame.pack(pady=5, padx=10, fill=tk.X)
        deadline_label = ctk.CTkLabel(deadline_frame, text="Deadline:")
        deadline_label.pack(side=tk.LEFT)
        self.deadline_entry = DateEntry(deadline_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2)
        self.deadline_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        assign_button = ctk.CTkButton(self.assign_task_window, text="Assign Task", command=self.assign_task)
        assign_button.pack(pady=10)

        clear_button = ctk.CTkButton(self.assign_task_window, text="Clear", command=self.clear_assign_task_entries)
        clear_button.pack(pady=10)

    def assign_task(self):
        task_name = self.task_name_combobox.get()
        task_description = self.task_description_entry.get()
        assigned_to = self.assign_to_combobox.get()
        deadline = self.deadline_entry.get_date()

        self.cursor.execute('''
            INSERT INTO tasks (task_name, task_description, assigned_to, status, deadline)
            VALUES (?, ?, ?, ?, ?)
        ''', (task_name, task_description, assigned_to, "Pending", deadline))
        self.connector.commit()

        # Add notification for the new task assignment
        self.add_notification(f'Task "{task_name}" has been assigned to {assigned_to}')

        messagebox.showinfo("Success", "Task assigned successfully!")
        self.assign_task_window.destroy()
        self.load_tasks()

    def clear_assign_task_entries(self):
        self.task_name_combobox.set('')
        self.task_description_entry.delete(0, tk.END)
        self.assign_to_combobox.set('')
        self.deadline_entry.set_date(datetime.now().date())

    def close_subpanel(self):
        self.root.destroy()  # Close the main window and all associated frames

    def add_notification(self, description):
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION) VALUES (?)', (description,))
        self.connector.commit()

    def show_notifications_window(self):
        notification_window = ctk.CTkToplevel(self.root)
        notification_window.title('Notifications')
        notification_window.geometry('500x400')
        notification_window.resizable(0, 0)

        # Set the notification window to be on top of the main root window
        notification_window.attributes('-topmost', 'true')

        notification_label = ctk.CTkLabel(notification_window, text="Notifications", font=("Helvetica", 14))
        notification_label.pack(pady=20)

        self.NOTIFICATION_LIST = tk.Listbox(notification_window)
        self.NOTIFICATION_LIST.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.load_notifications()

        delete_button = ctk.CTkButton(notification_window, text="Delete Selected",
                                      command=self.delete_selected_notification)
        delete_button.pack(pady=10)

    def delete_selected_notification(self):
        # Get selected indices from the notification list
        selected_indices = self.NOTIFICATION_LIST.curselection()

        # Check if any notification is selected
        if not selected_indices:
            messagebox.showwarning('No notification selected!', 'Please select a notification to delete.')
            return

        # Ask for confirmation before deleting the selected notification(s)
        confirm_delete = messagebox.askyesno('Confirm Delete',
                                             'Are you sure you want to delete the selected notification(s)?')
        if not confirm_delete:
            return

        # Loop through selected indices and delete the corresponding notifications
        for index in selected_indices:
            try:
                # Fetch the notification ID using the index
                notification_id = self.notification_ids[index]
                # Execute the SQL delete command
                self.cursor.execute('DELETE FROM Notifications WHERE NOTIFICATION_ID=?', (notification_id,))
                self.connector.commit()
            except sqlite3.Error as e:
                # Show error message if there is an issue with deletion
                messagebox.showerror('Error', f'Error deleting notification: {str(e)}')
                return

        # Reload notifications after deletion
        self.load_notifications()

    def load_notifications(self):
        try:
            self.NOTIFICATION_LIST.delete(0, tk.END)  # Clear the list first
            self.notification_ids = {}  # Dictionary to store index to ID mapping
            self.cursor.execute("SELECT * FROM Notifications")
            notifications = self.cursor.fetchall()

            for idx, notification in enumerate(notifications):
                timestamp = datetime.strptime(notification[2],
                                              '%Y-%m-%d %H:%M:%S')  # Assuming the timestamp is in the third column
                utc_timezone = pytz.utc
                local_timezone = pytz.timezone('Asia/Singapore')  # GMT+8 timezone
                utc_timestamp = utc_timezone.localize(timestamp)
                local_timestamp = utc_timestamp.astimezone(local_timezone)
                formatted_timestamp = local_timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format the timestamp as desired
                message_with_timestamp = f"{formatted_timestamp} - {notification[1]}"
                self.NOTIFICATION_LIST.insert(tk.END, message_with_timestamp)
                self.notification_ids[idx] = notification[0]  # Store the ID with the index as the key
        except sqlite3.Error as e:
            messagebox.showerror('Error', f'Error loading notifications: {str(e)}')

    def open_rate_performance_window(self):
        self.rate_performance_window = ctk.CTkToplevel(self.root)
        self.rate_performance_window.title("Rate Performance")
        self.rate_performance_window.geometry('400x300')
        self.rate_performance_window.attributes('-topmost', True)

        title_label = ctk.CTkLabel(self.rate_performance_window, text="Rate Performance", font=("Helvetica", 14))
        title_label.pack(pady=20)

        # Assign To (User ID)
        assign_to_frame = ctk.CTkFrame(self.rate_performance_window)
        assign_to_frame.pack(pady=5, padx=10, fill=tk.X)
        assign_to_label = ctk.CTkLabel(assign_to_frame, text="Assign To (User ID):")
        assign_to_label.pack(side=tk.LEFT)

        self.cursor.execute("SELECT username FROM workers")
        usernames = [row[0] for row in self.cursor.fetchall()]
        self.assign_to_combobox = ttk.Combobox(assign_to_frame, values=usernames)
        self.assign_to_combobox.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Performance Rating
        rating_frame = ctk.CTkFrame(self.rate_performance_window)
        rating_frame.pack(pady=5, padx=10, fill=tk.X)
        rating_label = ctk.CTkLabel(rating_frame, text="Performance Rating (0-10):")
        rating_label.pack(side=tk.LEFT)
        self.rating_entry = ctk.CTkEntry(rating_frame)
        self.rating_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        rate_button = ctk.CTkButton(self.rate_performance_window, text="Rate", command=self.rate_performance)
        rate_button.pack(pady=10)

    def rate_performance(self):
        assigned_to = self.assign_to_combobox.get()
        rating = self.rating_entry.get()

        # Check if the worker has completed their task
        self.cursor.execute('''
            SELECT status
            FROM tasks
            WHERE assigned_to = ? AND status = 'Completed'
        ''', (assigned_to,))
        completed_tasks = self.cursor.fetchall()

        if not completed_tasks:
            messagebox.showwarning("Warning", f"{assigned_to} has not completed any tasks.")
            return

        # Update the performance rating if there is at least one completed task
        self.cursor.execute('''
            UPDATE workers
            SET performance_rating = ?
            WHERE username = ?
        ''', (rating, assigned_to))
        self.connector.commit()

        messagebox.showinfo("Success", "Performance rated successfully!")
        self.rate_performance_window.destroy()

    def generate_performance_report(self):
        # Get the selected task from the task tree
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a task to generate the report.")
            return

        selected_task = self.task_tree.item(selected_item)["values"]
        task_id = selected_task[0]  # Assuming the first column is the task ID

        try:
            # Fetch detailed data for the selected task from the database
            self.cursor.execute('''
                SELECT w.username, w.performance_rating, t.task_id, t.task_name, t.deadline, t.task_description, t.status
                FROM workers w
                LEFT JOIN tasks t ON w.username = t.assigned_to
                WHERE t.task_id = ?
            ''', (task_id,))
            row = self.cursor.fetchone()

            if row:
                username, performance_rating, task_id, task_name, deadline, task_description, status = row

                # Format the date
                date_str = datetime.now().strftime("%Y-%m-%d")

                # Create a new PDF document
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                # Add title
                pdf.set_font("Arial", 'B', size=16)
                pdf.cell(200, 10, txt="Worker's Performance Report", ln=True, align='C')

                # Add worker and task information
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Username: {username}", ln=True)
                pdf.cell(200, 10, txt=f"Performance Rating: {performance_rating}", ln=True)
                pdf.cell(200, 10, txt=f"Task ID: {task_id}", ln=True)
                pdf.cell(200, 10, txt=f"Task Name: {task_name}", ln=True)
                pdf.cell(200, 10, txt=f"Deadline: {deadline}", ln=True)
                pdf.cell(200, 10, txt=f"Task Description: {task_description}", ln=True)
                pdf.cell(200, 10, txt=f"Status: {status}", ln=True)
                pdf.cell(200, 10, txt=f"Date: {date_str}", ln=True)

                # Save the PDF with the name containing the username and date
                file_name = f"performance_report_{username}_{date_str}.pdf"
                pdf.output(file_name)

                messagebox.showinfo("Success", "Performance report generated successfully!")
            else:
                messagebox.showerror("Error", "No details found for the selected task.")

        except Exception as e:
            messagebox.showerror("Error", f"Error generating performance report: {str(e)}")


if __name__ == "__main__":
    root = ctk.CTk()
    app = AssignmentApp(root, "admin")
    root.mainloop()
