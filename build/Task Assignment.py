import os
import tkinter as tk
from tkinter import ttk, messagebox, Menu
from PIL import Image, ImageTk
import customtkinter as ctk
from datetime import datetime, timedelta, timezone
import sqlite3
import pytz
from tkcalendar import DateEntry
from fpdf import FPDF
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.widgets.markers import makeMarker
import platform

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
        self.is_filter_active = False
        self.detached_items = []
        self.load_tasks()
        self.schedule_task_status_update()

    def create_main_window(self):
        top_frame = ctk.CTkFrame(self.root, fg_color='#BF2C37')
        top_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ctk.CTkLabel(top_frame, text="WORKER TASK MANAGEMENT", font=("Helvetica", 16, 'bold'),
                                   text_color='white')
        title_label.pack(side=tk.LEFT, padx=20, pady=20)

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

        self.del_task_button = ctk.CTkButton(left_frame, text="DELETE TASK", fg_color='#FFFFFF', text_color='#000000',
                                         command=self.delete_task)
        self.del_task_button.pack(pady=10)

        self.refresh_button = ctk.CTkButton(left_frame, text="REFRESH TASKS", fg_color='#FFFFFF', text_color='#000000',
                                            command=self.load_tasks)
        self.refresh_button.pack(pady=10)

        # self.rate_performance_button = ctk.CTkButton(left_frame, text="RATE PERFORMANCE", fg_color='#FFFFFF',
        #                                              text_color='#000000',
        #                                              command=self.open_rate_performance_window)
        # self.rate_performance_button.pack(pady=10)

        self.generate_report_button = ctk.CTkButton(left_frame, text="GENERATE PERFORMANCE REPORT", fg_color='#FFFFFF',
                                                    text_color='#000000',
                                                    command=self.open_performance_window)
        self.generate_report_button.pack(pady=10)

        self.open_performance_button = ctk.CTkButton(left_frame, text="OPEN PERFORMANCE REPORTS", fg_color='#FFFFFF',
                                                    text_color='#000000',
                                                    command=self.open_performance_folder)
        self.open_performance_button.pack(pady=10)

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

        # Right-click menu for header
        self.header_menu = Menu(self.root, tearoff=0)
        self.header_menu.add_command(label="Filter", command=self.filter_by_column)

        # Bind right-click to show context menu
        self.task_tree.bind("<Button-3>", self.show_header_menu)

    def adjust_column_widths(self):
        # Calculate available width for remaining columns
        total_width = self.task_frame.winfo_width()
        visible_columns = [col for col in self.task_tree["columns"] if col != "PRODUCT_REAL_ID"]
        column_count = len(visible_columns)

        if column_count > 0 and total_width > 0:
            equal_width = total_width // column_count

            for col in visible_columns:
                self.task_tree.column(col, width=equal_width)

    def show_header_menu(self, event):
        if not self.is_filter_active:  # Check if filtering is active
            # Find the column heading that was clicked
            region = self.task_tree.identify("region", event.x, event.y)
            if region == "heading":
                col = self.task_tree.identify_column(event.x)
                self.selected_column = self.task_tree.heading(col)["text"]
                self.update_header_menu(col)
                self.header_menu.post(event.x_root, event.y_root)
        else:
            # Only show the "Show All" option
            self.header_menu.delete(0, tk.END)
            self.header_menu.add_command(label="Show All", command=self.show_all)
            self.header_menu.post(event.x_root, event.y_root)

    def update_header_menu(self, col):
        # Clear previous menu items
        self.header_menu.delete(0, tk.END)

        if not self.is_filter_active:
            # Add submenu for unique items
            unique_items_menu = Menu(self.header_menu, tearoff=0)
            unique_items = self.get_unique_items(col)

            for item in unique_items:
                unique_items_menu.add_command(label=item, command=lambda value=item: self.filter_by_column(value))

            self.header_menu.add_cascade(label="Filter by", menu=unique_items_menu)

    def get_unique_items(self, col):
        # Get unique items in the specified column
        col_index = int(col.replace('#', '')) - 1
        items = set()

        for child in self.task_tree.get_children():
            item = self.task_tree.item(child, 'values')[col_index]
            items.add(item)

        return sorted(items)

    def filter_by_column(self, filter_value):
        col_index = self.task_tree["columns"].index(self.selected_column)

        self.detached_items = []  # Clear the detached items list

        for item in self.task_tree.get_children():
            values = self.task_tree.item(item, 'values')
            if values[col_index] != filter_value:
                self.detached_items.append(item)
                self.task_tree.detach(item)

        self.is_filter_active = True  # Set filtering active

    def show_all(self):
        for item in self.detached_items:
            self.task_tree.reattach(item, '', 'end')
        self.detached_items = []  # Clear the detached items list
        self.is_filter_active = False  # Set filtering inactive

    def load_tasks(self):
        for i in self.task_tree.get_children():
            self.task_tree.delete(i)

        self.cursor.execute("SELECT * FROM tasks")
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

    def open_assign_task_window(self):
        # Create a new Toplevel window for assigning tasks
        self.assign_task_window = ctk.CTkToplevel(self.root)
        self.assign_task_window.title("Assign Task")
        self.assign_task_window.attributes('-topmost', True)

        # Add a red heading
        ctk.CTkLabel(self.assign_task_window, text="ASSIGN TASK", font=('Helvetica', 16, 'bold'),
                     text_color='red').grid(row=0, columnspan=2, padx=10, pady=10)

        # Setup Task Name Widgets
        ctk.CTkLabel(self.assign_task_window, text="Task Name:", font=('Gill Sans MT', 13)).grid(row=1, column=0,
                                                                                                 padx=10, pady=10)
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
        self.task_name_combobox = ctk.CTkComboBox(self.assign_task_window, values=task_names)
        self.task_name_combobox.grid(row=1, column=1, padx=10, pady=10)

        # Setup Task Description Widgets
        ctk.CTkLabel(self.assign_task_window, text="Task Description:", font=('Gill Sans MT', 13)).grid(row=2, column=0,
                                                                                                        padx=10,
                                                                                                        pady=10)
        self.task_description_entry = ctk.CTkEntry(self.assign_task_window, font=('Gill Sans MT', 13), width=200)
        self.task_description_entry.grid(row=2, column=1, padx=10, pady=10)

        # Setup Assign To Widgets
        ctk.CTkLabel(self.assign_task_window, text="Assign To (User ID):", font=('Gill Sans MT', 13)).grid(row=3,
                                                                                                           column=0,
                                                                                                           padx=10,
                                                                                                           pady=10)
        self.cursor.execute("SELECT username FROM workers")
        usernames = [row[0] for row in self.cursor.fetchall()]
        self.assign_to_combobox = ttk.Combobox(self.assign_task_window, values=usernames)
        self.assign_to_combobox.grid(row=3, column=1, padx=10, pady=10)

        # Setup Deadline Widgets
        ctk.CTkLabel(self.assign_task_window, text="Deadline Date and Time (Date HH:MM AM/PM):",
                     font=('Gill Sans MT', 13)).grid(row=4, column=0, padx=10, pady=10)
        deadline_frame = ctk.CTkFrame(self.assign_task_window)
        deadline_frame.grid(row=4, column=1, padx=10, pady=10, sticky='ew')

        self.deadline_date_entry = DateEntry(deadline_frame, date_pattern='y-mm-dd')
        self.deadline_date_entry.pack(side=tk.LEFT, padx=5)
        self.hour_spinbox = tk.Spinbox(deadline_frame, from_=1, to=12, width=2)
        self.hour_spinbox.pack(side=tk.LEFT, padx=5)
        self.minute_spinbox = tk.Spinbox(deadline_frame, from_=0, to=59, width=2)
        self.minute_spinbox.pack(side=tk.LEFT, padx=5)
        self.am_pm_combobox = ttk.Combobox(deadline_frame, values=["AM", "PM"])
        self.am_pm_combobox.pack(side=tk.LEFT, padx=5)

        # Add buttons for Assign Task and Clear
        ctk.CTkButton(self.assign_task_window, text="Assign Task", font=('Helvetica', 13, 'bold'),
                      fg_color='SpringGreen4', command=self.assign_task).grid(row=5, column=0, padx=10, pady=10)
        ctk.CTkButton(self.assign_task_window, text="Clear", font=('Helvetica', 13, 'bold'), fg_color='red',
                      command=self.clear_assign_task_entries).grid(row=5, column=1, padx=10, pady=10)

    def create_labeled_frame(self, parent, label_text, widget_name, combobox_values=None):
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=5, padx=10, fill=tk.X)
        label = ctk.CTkLabel(frame, text=label_text)
        label.pack(side=tk.LEFT)
        if combobox_values:
            setattr(self, widget_name, ctk.CTkComboBox(frame, values=combobox_values))
        else:
            setattr(self, widget_name, ctk.CTkEntry(frame))
        widget = getattr(self, widget_name)
        widget.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def convert_to_24_hour_format(self, hour, minute, am_pm):
        if am_pm == 'PM' and hour != 12:
            hour += 12
        elif am_pm == 'AM' and hour == 12:
            hour = 0
        return hour, minute

    def convert_to_local_time(self, date, hour, minute):
        local_tz = pytz.timezone('Asia/Singapore')
        deadline_naive = datetime(date.year, date.month, date.day, hour, minute)
        deadline_local = local_tz.localize(deadline_naive)
        return deadline_local

    def assign_task(self):
        try:
            task_name = self.task_name_combobox.get()
            task_description = self.task_description_entry.get()
            assigned_to = self.assign_to_combobox.get()
            hour = self.hour_spinbox.get()
            minute = self.minute_spinbox.get()
            am_pm = self.am_pm_combobox.get()
            deadline_date = self.deadline_date_entry.get_date()

            if not task_name:
                raise ValueError("Task name cannot be empty.")
            if not task_description:
                raise ValueError("Task description cannot be empty.")
            if not assigned_to:
                raise ValueError("Assigned to field cannot be empty.")
            if not hour or not minute or not am_pm:
                raise ValueError("Time cannot be empty.")
            if not deadline_date:
                raise ValueError("Deadline date cannot be empty.")

            hour = int(hour)
            minute = int(minute)
            hour, minute = self.convert_to_24_hour_format(hour, minute, am_pm)
            deadline_local = self.convert_to_local_time(deadline_date, hour, minute)
            deadline_gmt8_str = deadline_local.strftime('%Y-%m-%d %H:%M:%S')

            self.cursor.execute('''
                INSERT INTO tasks (task_name, task_description, assigned_to, status, deadline)
                VALUES (?, ?, ?, ?, ?)
            ''', (task_name, task_description, assigned_to, 'Pending', deadline_gmt8_str))
            self.connector.commit()

            self.add_notification(f'Task "{task_name}" has been assigned to {assigned_to} due by {deadline_gmt8_str}')
            messagebox.showinfo("Success", "Task assigned successfully.")

            self.assign_task_window.destroy()
            self.load_tasks()
            self.clear_assign_task_entries()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a task to delete.")
            return

        task_id = self.task_tree.item(selected_item)['values'][0]

        # Ask for confirmation
        confirm = messagebox.askokcancel("Confirm Deletion",
                                         f"Are you sure you want to delete task ID {task_id}?")

        if confirm:
            self.cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
            self.connector.commit()

            self.load_tasks()

    def clear_assign_task_entries(self):
        self.task_name_combobox.set('')
        self.task_description_entry.delete(0, tk.END)
        self.assign_to_combobox.set('')
        self.deadline_date_entry.set_date(datetime.now())
        self.hour_spinbox.delete(0, tk.END)
        self.minute_spinbox.delete(0, tk.END)
        self.am_pm_combobox.set('AM')

    def close_subpanel(self):
        self.root.destroy()  # Close the main window and all associated frames

    def add_notification(self, description):
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('INSERT INTO Notifications (DESCRIPTION, TIMESTAMP) VALUES (?, ?)',
                            (description, timestamp))
        self.connector.commit()

    def show_notifications_window(self):
        subprocess.Popen(["python", "Notifications.py"])

    def update_task_statuses(self):
        current_time = datetime.now(pytz.timezone('Asia/Singapore'))
        self.cursor.execute("SELECT task_id, deadline FROM tasks WHERE status != 'Completed'")
        tasks = self.cursor.fetchall()

        for task in tasks:
            task_id, deadline_str = task
            # Parsing the deadline string to a datetime object with timezone information
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
                deadline = pytz.timezone('Asia/Singapore').localize(deadline)

                if current_time > deadline:
                    self.cursor.execute("UPDATE tasks SET status = 'Overdue' WHERE task_id = ?", (task_id,))
            except ValueError as e:
                print(f"Error parsing date for task {task_id}: {e}")

        self.connector.commit()
        self.load_tasks()  # Refresh the task list to show updated statuses

    def open_performance_window(self):
        # Create a new Toplevel window for managing performance
        self.performance_window = ctk.CTkToplevel(self.root)
        self.performance_window.title("Performance Management")
        self.performance_window.attributes('-topmost', True)

        # Add a red heading
        ctk.CTkLabel(self.performance_window, text="Manage Performance", font=('Helvetica', 16, 'bold'),
                     text_color='red').grid(row=0, columnspan=2, padx=10, pady=10)

        # Setup Select Worker Widgets
        ctk.CTkLabel(self.performance_window, text="Select Worker:", font=('Gill Sans MT', 13)).grid(row=1, column=0,
                                                                                                     padx=10, pady=10)
        self.cursor.execute("SELECT username FROM workers")
        usernames = [row[0] for row in self.cursor.fetchall()]
        self.assign_to_combobox = ttk.Combobox(self.performance_window, values=usernames)
        self.assign_to_combobox.grid(row=1, column=1, padx=10, pady=10)

        # Setup Performance Rating Widgets
        ctk.CTkLabel(self.performance_window, text="Performance Rating (0-10):", font=('Gill Sans MT', 13)).grid(row=2,
                                                                                                                 column=0,
                                                                                                                 padx=10,
                                                                                                                 pady=10)
        self.rating_entry = ctk.CTkEntry(self.performance_window, font=('Gill Sans MT', 13), width=200)
        self.rating_entry.grid(row=2, column=1, padx=10, pady=10)

        # Add buttons for Rate and Generate Performance and Cancel
        ctk.CTkButton(self.performance_window, text="Rate and Generate Performance", font=('Helvetica', 13, 'bold'),
                      fg_color='SpringGreen4', command=self.rate_and_generate_report).grid(row=3, column=0, padx=10,
                                                                                           pady=10)
        ctk.CTkButton(self.performance_window, text="Cancel", font=('Helvetica', 13, 'bold'), fg_color='red',
                      command=self.performance_window.destroy).grid(row=3, column=1, padx=10, pady=10)

    def rate_and_generate_report(self):
        assigned_to = self.assign_to_combobox.get()
        rating = int(self.rating_entry.get())

        if rating < 1 or rating > 10:
            messagebox.showwarning("Warning", f"Rating is out of range.")
            return

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

        # Generate performance report
        try:
            self.cursor.execute('''
                SELECT w.username, w.performance_rating,
                       COUNT(t.task_id) AS total_tasks,
                       SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) AS completed_tasks,
                       SUM(CASE WHEN t.status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_tasks
                FROM workers w
                LEFT JOIN tasks t ON w.username = t.assigned_to
                WHERE w.username = ?
                GROUP BY w.username, w.performance_rating
            ''', (assigned_to,))
            row = self.cursor.fetchone()

            if row:
                username, performance_rating, total_tasks, completed_tasks, overdue_tasks = row

                if performance_rating is None:
                    messagebox.showerror("Error", "The supervisor has not yet rated this worker.")
                    return

                date_str = datetime.now().strftime("%Y-%m-%d")

                if not os.path.exists('Worker Performance Reports'):
                    os.makedirs('Worker Performance Reports')

                doc = SimpleDocTemplate(f"Worker Performance Reports/performance_report_{username}_{date_str}.pdf", pagesize=letter)
                styles = getSampleStyleSheet()

                report_elements = []

                title_style = styles["Title"]
                title_style.textColor = colors.red
                report_elements.append(Paragraph("Worker's Performance Report", title_style))
                report_elements.append(Spacer(1, 12))

                header_style = ParagraphStyle('header_style', fontSize=14, textColor=colors.black)
                report_elements.append(Paragraph(f"Username: {username}", header_style))
                report_elements.append(Paragraph(f"Performance Rating: {performance_rating}", header_style))
                report_elements.append(Paragraph(f"Date: {date_str}", header_style))
                report_elements.append(Spacer(1, 12))

                data = [
                    ["Metric", "Value"],
                    ["Total Tasks", total_tasks],
                    ["Completed Tasks", completed_tasks],
                    ["Overdue Tasks", overdue_tasks]
                ]

                table = Table(data, colWidths=[200, 200])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                report_elements.append(table)
                report_elements.append(Spacer(1, 12))

                # Bar Chart
                drawing = Drawing(400, 200)

                data = [(completed_tasks, overdue_tasks)]
                bc = VerticalBarChart()
                bc.x = 50
                bc.y = 50
                bc.height = 125
                bc.width = 300
                bc.data = data
                bc.strokeColor = colors.black
                bc.valueAxis.valueMin = 0
                bc.valueAxis.valueMax = max(completed_tasks, overdue_tasks) + 1
                bc.valueAxis.valueStep = 1
                bc.categoryAxis.labels.boxAnchor = 'ne'
                bc.categoryAxis.labels.dx = 8
                bc.categoryAxis.labels.dy = -2
                bc.categoryAxis.labels.angle = 30
                bc.categoryAxis.categoryNames = ['Completed', 'Overdue']

                bar_colors = [colors.green, colors.red]
                for i, color in enumerate(bar_colors):
                    bc.bars[i].fillColor = color

                drawing.add(bc)

                legend = Legend()
                legend.x = 370
                legend.y = 150
                legend.dx = 8
                legend.dy = 8
                legend.fontName = 'Helvetica'
                legend.fontSize = 10
                legend.boxAnchor = 'nw'
                legend.columnMaximum = 10
                legend.strokeWidth = 1
                legend.strokeColor = colors.black
                legend.deltax = 75
                legend.deltay = 10
                legend.autoXPadding = 5
                legend.yGap = 0
                legend.dxTextSpace = 5
                legend.alignment = 'right'
                legend.dividerLines = 1 | 2 | 4
                legend.dividerOffsY = 4.5
                legend.subCols.rpad = 30

                legend.colorNamePairs = [(colors.green, 'Completed Tasks'), (colors.red, 'Overdue Tasks')]
                drawing.add(legend)

                report_elements.append(drawing)

                doc.build(report_elements)
                messagebox.showinfo("Success", "Performance report generated successfully!")
            else:
                messagebox.showerror("Error", "No details found for the selected worker.")

        except Exception as e:
            messagebox.showerror("Error", f"Error generating performance report: {str(e)}")

        self.performance_window.destroy()

    def get_worker_usernames(self):
        self.cursor.execute("SELECT username FROM workers")
        return [row[0] for row in self.cursor.fetchall()]

    def schedule_task_status_update(self):
        self.update_task_statuses()
        # Schedule the function to run every 5 minutes
        self.root.after(60000, self.schedule_task_status_update)  # 300000 milliseconds = 5 minutes

    def open_performance_folder(self):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Define the path to the "Purchase Order" folder
        perf_path = os.path.join(script_dir, 'Worker Performance Reports')

        # Check the operating system and open the folder accordingly
        if platform.system() == 'Windows':
            os.startfile(perf_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', perf_path])
        else:  # Linux
            subprocess.Popen(['xdg-open', perf_path])

if __name__ == "__main__":
    root = ctk.CTk()
    app = AssignmentApp(root, "admin")
    root.mainloop()
