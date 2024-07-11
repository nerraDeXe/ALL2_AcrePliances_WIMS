import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
from datetime import datetime, timezone, timedelta
import sqlite3
import pytz
import sys
import subprocess


class WorkerApp:
    def __init__(self, root, username):
        self.connector = sqlite3.connect("AcrePliances.db")
        self.cursor = self.connector.cursor()
        self.create_notifications_table()

        self.username = username
        self.root = root
        self.root.title("Worker Application")
        self.root.geometry('1280x850')
        self.root.configure(bg='#BF2C37')
        self.root.resizable(0, 0)

        self.create_main_window()
        self.load_tasks()

        # Schedule the periodic task check
        self.check_upcoming_tasks()

    def create_main_window(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="WORKER TASK UPDATE", font=("Helvetica", 16, 'bold'),
                                   text_color='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        self.notification_image = ImageTk.PhotoImage(Image.open("nored.png"))

        self.notification_button = tk.Button(top_frame, image=self.notification_image, bg='white',
                                             activebackground='darkred', command=self.show_notifications_window)
        self.notification_button.pack(side=tk.RIGHT, padx=20, pady=20)

        left_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=20)

        self.update_button = ctk.CTkButton(left_frame, text="UPDATE TASK STATUS", fg_color='#FFFFFF',
                                           text_color='#000000', command=self.open_update_task_window)
        self.update_button.pack(pady=10)

        self.refresh_button = ctk.CTkButton(left_frame, text="REFRESH TASKS", fg_color='#FFFFFF', text_color='#000000',
                                            command=self.load_tasks)
        self.refresh_button.pack(pady=10)

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

        self.cursor.execute("SELECT * FROM tasks WHERE assigned_to=?", (self.username,))
        rows = self.cursor.fetchall()

        # Define tags for different status colors
        self.task_tree.tag_configure('completed', background='lightgreen')
        self.task_tree.tag_configure('overdue', background='lightcoral')

        now = datetime.now(timezone.utc)

        for row in rows:
            task_id, task_name, description, assigned_to, status, deadline = row
            deadline_dt = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S').astimezone(timezone.utc)

            if status.lower() == 'completed':
                tag = 'completed'
            elif deadline_dt < now and status.lower() != 'completed':
                tag = 'overdue'
            else:
                tag = ''

            self.task_tree.insert("", tk.END, values=row, tags=(tag,))

    def close_subpanel(self):
        self.root.destroy()

    ################################################NOTIFICATION FUNCTIONS#################################

    def create_notifications_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS TaskNotifications (
                notification_id INTEGER PRIMARY KEY,
                task_id INTEGER,
                deadline DATETIME,
                sent_1h INTEGER DEFAULT 0,
                sent_30m INTEGER DEFAULT 0,
                sent_10m INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                FOREIGN KEY (deadline) REFERENCES tasks (deadline)
            )
        ''')
        self.connector.commit()

    def add_notification(self, description):
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION, TIMESTAMP) VALUES (?, ?)',
                            (description, timestamp))
        self.connector.commit()

    def show_notifications_window(self):
        subprocess.Popen(["python", "Notifications.py"])

    def open_update_task_window(self):
        selected_item = self.task_tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select a task to update.")
            return

        task_id = self.task_tree.item(selected_item)['values'][0]
        task_status = self.task_tree.item(selected_item)['values'][4]

        if task_status.lower() == 'completed':
            messagebox.showerror("Error", "Cannot update status of a completed task.")
            return

        self.update_task_window = ctk.CTkToplevel(self.root)
        self.update_task_window.title("Update Task Status")
        self.update_task_window.geometry('400x300')
        self.update_task_window.attributes('-topmost', True)

        ctk.CTkLabel(self.update_task_window, text=f"Task ID: {task_id}", font=("Helvetica", 12)).pack(pady=10)

        ctk.CTkLabel(self.update_task_window, text="New Status:", font=("Helvetica", 12)).pack(pady=10)
        status_options = ["Pending", "In Progress", "Completed", "Cancelled", "On Hold"]
        self.new_status_combobox = ctk.CTkComboBox(self.update_task_window, values=status_options)
        self.new_status_combobox.pack(pady=5, padx=20, fill=tk.X)

        ctk.CTkButton(self.update_task_window, text="Update Status",
                      command=lambda: self.update_task_status(task_id)).pack(pady=20)

    def update_task_status(self, task_id):
        new_status = self.new_status_combobox.get()

        if not new_status:
            messagebox.showerror("Error", "New Status must be selected!")
            return

        allowed_statuses = ["Pending", "In Progress", "Completed", "Cancelled", "On Hold"]

        if new_status not in allowed_statuses:
            messagebox.showerror("Error",
                                 f"Invalid status selected. Please select one from: {', '.join(allowed_statuses)}")
            return

        try:
            self.cursor.execute('''
                UPDATE tasks
                SET status = ?
                WHERE task_id = ?
            ''', (new_status, task_id))
            self.connector.commit()

            self.add_notification(f'Task ID "{task_id}" status updated to "{new_status}" by {self.username}')

            messagebox.showinfo("Success", "Task status updated successfully!")
            self.update_task_window.destroy()
            self.load_tasks()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    ################################################ UPCOMING TASK CHECK #################################

    def check_upcoming_tasks(self):
        now = datetime.now(timezone.utc)
        warning_times = {
            '1h': now + timedelta(hours=1),
            '30m': now + timedelta(minutes=30),
            '10m': now + timedelta(minutes=10),
        }

        self.cursor.execute(
            "SELECT task_id, task_name, deadline FROM tasks WHERE assigned_to=? AND status != 'Completed'",
            (self.username,))
        tasks = self.cursor.fetchall()

        for task in tasks:
            task_id, task_name, deadline = task
            deadline_dt = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S').astimezone(timezone.utc)

            for key, warning_time in warning_times.items():
                if now < deadline_dt <= warning_time:
                    self.cursor.execute(
                        "SELECT sent_1h, sent_30m, sent_10m FROM TaskNotifications WHERE task_id=? AND deadline=?",
                        (task_id, deadline))
                    notification_status = self.cursor.fetchone()

                    if notification_status:
                        sent_1h, sent_30m, sent_10m = notification_status
                    else:
                        sent_1h = sent_30m = sent_10m = 0

                    if key == '1h' and not sent_1h:
                        self.add_notification(f'Task "{task_name}" (ID: {task_id}) is due in 1 hour.')
                        self.cursor.execute(
                            "INSERT OR REPLACE INTO TaskNotifications (task_id, deadline, sent_1h) VALUES (?, ?, ?)",
                            (task_id, deadline, 1))
                    elif key == '30m' and not sent_30m:
                        self.add_notification(f'Task "{task_name}" (ID: {task_id}) is due in 30 minutes.')
                        self.cursor.execute(
                            "INSERT OR REPLACE INTO TaskNotifications (task_id, deadline, sent_30m) VALUES (?, ?, ?)",
                            (task_id, deadline, 1))
                    elif key == '10m' and not sent_10m:
                        self.add_notification(f'Task "{task_name}" (ID: {task_id}) is due in 10 minutes.')
                        self.cursor.execute(
                            "INSERT OR REPLACE INTO TaskNotifications (task_id, deadline, sent_10m) VALUES (?, ?, ?)",
                            (task_id, deadline, 1))

        self.connector.commit()

        # Schedule this function to run again after 5 minutes
        self.root.after(60000, self.check_upcoming_tasks)


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    root = ctk.CTk()
    app = WorkerApp(root, username)
    root.mainloop()
