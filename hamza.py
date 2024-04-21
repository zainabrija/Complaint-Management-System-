
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import bcrypt
import mysql.connector
from mysql.connector import Error
# Global variable to track login status
is_user_logged_in = False
current_user = None

def create_users_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(100),
        last_name VARCHAR(100),
        username VARCHAR(50) UNIQUE,
        email VARCHAR(100),
        phone_number VARCHAR(15),
        gender ENUM('Male', 'Female', 'Other'),
        password VARCHAR(255)
    );
    '''
    
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Users table created successfully")
    except Error as e:
        print(f"Error creating table: {e}")

def create_complaints_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS complaints (
        complaint_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50),
        category VARCHAR(100),
        details TEXT,
        submitted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved TINYINT(1) DEFAULT 0,  -- Added column for resolved status (0 for False, 1 for True)
        FOREIGN KEY (username) REFERENCES users(username)
    );
    '''
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        print("Complaints table created successfully with resolved status")
    except Error as e:
        print(f"Error occurred: {e}")


try:
    connection = mysql.connector.connect(
        host='Localhost',
        user='root',
        password='Zainab@123',
        database='cms'
    )

    if connection.is_connected():
        db_info = connection.get_server_info()
        print("Successfully connected to Complaint Management Database", db_info)
        create_users_table() 
        create_complaints_table()
except Error as e:
    print("Error while connecting to MySQL", e)








######## DASHBORD ################




def show_dashboard():
    dashboard_window = Toplevel(root)
    dashboard_window.title("Dashboard")

    ttk.Button(dashboard_window, text="User Dashboard", command=open_user_dashboard).pack(pady=10)
    ttk.Button(dashboard_window, text="Admin Dashboard", command=open_admin_dashboard).pack(pady=10)
    ttk.Button(dashboard_window, text="Pending Complaints", command=view_pending_complaints).pack(pady=10)
    ttk.Button(dashboard_window, text="Completed Complaints", command=view_completed_complaints).pack(pady=10)



# Placeholder functions for button commands

def open_admin_dashboard():
    admin_window = Toplevel(root)
    admin_window.title("Admin Dashboard")
# Button to view user statistics
    ttk.Button(admin_window, text="View User Statistics", command=view_user_statistics).pack(pady=5)

    # Button to manage user accounts
    ttk.Button(admin_window, text="User Accounts", command=user_accounts).pack(pady=5)
    ttk.Button(admin_window, text="Manage Complaints", command=manage_complaints).pack(pady=5)
def view_user_statistics():
    stats_window = Toplevel(root)
    stats_window.title("User Statistics")
    stats_window.geometry("300x200")

    try:
        cursor = connection.cursor()

        # Fetch total number of users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        # Fetch total number of complaints
        cursor.execute("SELECT COUNT(*) FROM complaints")
        total_complaints = cursor.fetchone()[0]

        cursor.close()

        # Display statistics
        ttk.Label(stats_window, text=f"Total Users: {total_users}").pack(pady=5)
        ttk.Label(stats_window, text=f"Total Complaints: {total_complaints}").pack(pady=5)

      

    except Error as e:
        messagebox.showerror("Error", f"Error occurred: {e}")
def user_accounts():
    users_window = Toplevel(root)
    users_window.title("Manage User Accounts")
    users_window.geometry("500x300")

    # Setting up the Treeview for user data
    columns = ('username', 'first_name', 'last_name', 'email')
    user_tree = ttk.Treeview(users_window, columns=columns, show='headings')

    for col in columns:
        user_tree.heading(col, text=col.capitalize())

    user_tree.pack(side=LEFT, fill=BOTH, expand=True)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(users_window, orient=VERTICAL, command=user_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    user_tree.configure(yscrollcommand=scrollbar.set)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT username, first_name, last_name, email FROM users")
        for user in cursor.fetchall():
            user_tree.insert('', END, values=user)
        cursor.close()
    except Error as e:
        messagebox.showerror("Error", f"Error occurred: {e}")

    # Add buttons for editing and deleting users (functionality to be implemented)
    ttk.Button(users_window, text="Edit Selected User", command=lambda: edit_user(user_tree)).pack(pady=5)
    ttk.Button(users_window, text="Delete Selected User", command=lambda: delete_user(user_tree)).pack(pady=5)

def edit_user(user_tree):
    # Implement edit functionality
    pass

def delete_user(user_tree):
    # Implement delete functionality
    pass

def manage_complaints():
    complaints_window = Toplevel(root)
    complaints_window.title("Manage Complaints")
    complaints_window.geometry("600x400")

    # Setting up the Treeview for complaint data
    columns = ('complaint_id', 'username', 'category', 'details','resolved')
    complaints_tree = ttk.Treeview(complaints_window, columns=columns, show='headings')

    for col in columns:
        complaints_tree.heading(col, text=col.capitalize())

    complaints_tree.pack(side=LEFT, fill=BOTH, expand=True)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(complaints_window, orient=VERTICAL, command=complaints_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    complaints_tree.configure(yscrollcommand=scrollbar.set)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT complaint_id, username, category, details,resolved FROM complaints")
        for complaint in cursor.fetchall():
            complaints_tree.insert('', END, values=complaint)
        cursor.close()
    except Error as e:
        messagebox.showerror("Error", f"Error occurred: {e}")

    # Button to delete selected complaint
    ttk.Button(complaints_window, text="Delete Selected Complaint", command=lambda: delete_complaint(complaints_tree)).pack(pady=5)
# Inside manage_complaints function
# Completed complaints 
    ttk.Button(complaints_window, text="Mark Selected Complaint as Completed", command=lambda: update_complaint_status(complaints_tree)).pack(pady=5)
def update_complaint_status(complaints_tree):
    selected_item = complaints_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No complaint selected")
        return

    complaint_id = complaints_tree.item(selected_item, 'values')[0]

    if messagebox.askyesno("Update Status", f"Are you sure you want to mark complaint ID {complaint_id} as completed?"):
        try:
            cursor = connection.cursor()
            update_query = "UPDATE complaints SET resolved = 1 WHERE complaint_id = %s"
            cursor.execute(update_query, (complaint_id,))
            connection.commit()
            messagebox.showinfo("Update", "Complaint marked as completed")
        except Error as e:
            messagebox.showerror("Error", f"Error occurred: {e}")
        finally:
            if cursor:
                cursor.close()
        manage_complaints()




def delete_complaint(complaints_tree):
    selected_item = complaints_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No complaint selected")
        return

    complaint_id = complaints_tree.item(selected_item, 'values')[0]

    if messagebox.askyesno("Delete Complaint", f"Are you sure you want to delete complaint ID {complaint_id}?"):
        try:
            cursor = connection.cursor()
            delete_query = "DELETE FROM complaints WHERE complaint_id = %s"
            cursor.execute(delete_query, (complaint_id,))
            connection.commit()
            messagebox.showinfo("Delete", "Complaint deleted successfully")
        except Error as e:
            messagebox.showerror("Error", f"Error occurred: {e}")
        finally:
            if cursor:
                cursor.close()
        # Refresh complaint list
        manage_complaints()























def open_user_dashboard():
    user_window = Toplevel(root)
    user_window.title("User Dashboard")

    # Display user's complaints
    ttk.Label(user_window, text="Your Complaints:").pack(pady=10)
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM complaints WHERE username = %s"
        cursor.execute(query, (current_user,))
        complaints = cursor.fetchall()

        text_area = Text(user_window, wrap='word', height=10, width=50)
        text_area.pack(pady=10, padx=10)

        for complaint in complaints:
            complaint_id, _, category, details, submitted_on = complaint[:5]
            complaint_text = f"ID: {complaint_id}, Category: {category}, Submitted On: {submitted_on}\nDetails: {details}\n\n"
            text_area.insert(END, complaint_text)

        cursor.close()
    except Error as e:
        messagebox.showerror("Error", f"Error occurred: {e}")

    # Button to open the complaint submission form
    ttk.Button(user_window, text="Submit New Complaint", command=show_complaint_box).pack(pady=10)

def view_pending_complaints():
    pending_window = Toplevel(root)
    pending_window.title("Pending Complaints")
    pending_window.geometry("600x400")

    columns = ('complaint_id', 'username', 'category', 'details')
    pending_tree = ttk.Treeview(pending_window, columns=columns, show='headings')

    for col in columns:
        pending_tree.heading(col, text=col.capitalize())

    pending_tree.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(pending_window, orient=VERTICAL, command=pending_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    pending_tree.configure(yscrollcommand=scrollbar.set)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT complaint_id, username, category, details FROM complaints WHERE resolved = 0")
        for complaint in cursor.fetchall():
            pending_tree.insert('', END, values=complaint)
        cursor.close()
    except Error as e:
        messagebox.showerror("Error", f"Error occurred: {e}")
def view_completed_complaints():
    completed_window = Toplevel(root)
    completed_window.title("Completed Complaints")
    completed_window.geometry("600x400")

    columns = ('complaint_id', 'username', 'category', 'details')
    completed_tree = ttk.Treeview(completed_window, columns=columns, show='headings')

    for col in columns:
        completed_tree.heading(col, text=col.capitalize())

    completed_tree.pack(side=LEFT, fill=BOTH, expand=True)

    scrollbar = ttk.Scrollbar(completed_window, orient=VERTICAL, command=completed_tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    completed_tree.configure(yscrollcommand=scrollbar.set)

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT complaint_id, username, category, details FROM complaints WHERE resolved = 1")
        for complaint in cursor.fetchall():
            completed_tree.insert('', END, values=complaint)
        cursor.close()
    except Error as e:
        messagebox.showerror("Error", f"Error occurred: {e}")





























# Function to register user
def register_user(first_name, last_name, username, email, phone_number, gender, password, confirm_password):
    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match")
        return

    # Hashing the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor = connection.cursor()
        insert_query = """INSERT INTO users (first_name, last_name, username, email, phone_number, gender, password) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(insert_query, (first_name, last_name, username, email, phone_number, gender, hashed_password))
        connection.commit()
        cursor.close()
        messagebox.showinfo("Registration", "Registration Successful for " + username)
    except Error as e:
        messagebox.showerror("Registration Failed", str(e))
        if cursor:
            cursor.close()


def show_complaint_box():
    complaint_window = Toplevel(root)
    complaint_window.title("Submit a Complaint")

    # Displaying the complainant's name
    ttk.Label(complaint_window, text=f"Complainant: {current_user}", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=5)

    # Label at the top
    ttk.Label(complaint_window, text="Make a Complaint", font=("Arial", 16)).grid(row=1, column=0, columnspan=2, pady=10)

    # Category Dropdown Box
    ttk.Label(complaint_window, text="Category").grid(row=2, column=0, padx=10, pady=5)
    category_var = StringVar()
    category_dropdown = ttk.Combobox(complaint_window, textvariable=category_var, state="readonly", values=complaint_categories)
    category_dropdown.grid(row=2, column=1, padx=10, pady=5)
    category_dropdown.current(0)  # Default selection

    # Text area for entering complaint
    ttk.Label(complaint_window, text="Your Complaint").grid(row=3, column=0, padx=10, pady=5)
    complaint_text = Text(complaint_window, height=10, width=50)
    complaint_text.grid(row=3, column=1, padx=10, pady=5)

    # Submit Button
    ttk.Button(complaint_window, text="Submit Complaint", command=lambda: submit_complaint(current_user,category_var.get(), complaint_text.get("1.0", "end-1c"))).grid(row=4, column=1, pady=10)

# Placeholder function for complaint submission logic

def submit_complaint(username, category, details):
    insert_query = '''
    INSERT INTO complaints (username, category, details)
    VALUES (%s, %s, %s)
    '''
    try:
        cursor = connection.cursor()
        cursor.execute(insert_query, (username, category, details))
        connection.commit()
        print("Complaint successfully added to the database")
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        if cursor:
            cursor.close()


def render_complaint_box_or_login():
    global is_user_logged_in, current_user
    if is_user_logged_in:
        # Render the complaint box
        show_complaint_box()
        show_dashboard()
    else:
        # Show login screen
        open_login_window()

def login_user(username, entered_password):
    global is_user_logged_in, current_user
    try:
        cursor = connection.cursor(buffered=True)
        query = "SELECT password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            stored_password = result[0]

            if bcrypt.checkpw(entered_password.encode('utf-8'), stored_password.encode('utf-8')):
                is_user_logged_in = True
                current_user = username
                render_complaint_box_or_login()  # Call to update UI based on login status
                messagebox.showinfo("Login Info", "Login Successful")
            
            else:
                messagebox.showerror("Login Info", "Invalid username or password")
        else:
            messagebox.showerror("Login Info", "Invalid username or password")

        cursor.close()
    except Error as e:
        messagebox.showerror("Error", f"Error occurred: {e}")

import tkinter as tk
from tkinter import ttk

def open_register_window():
    register_window = Toplevel(root)
    register_window.title("Register")

    # First Name
    ttk.Label(register_window, text="First Name").grid(row=0, column=0)
    first_name = ttk.Entry(register_window)
    first_name.grid(row=0, column=1)

    # Last Name
    ttk.Label(register_window, text="Last Name").grid(row=1, column=0)
    last_name = ttk.Entry(register_window)
    last_name.grid(row=1, column=1)

    # Username
    ttk.Label(register_window, text="Username").grid(row=2, column=0)
    username = ttk.Entry(register_window)
    username.grid(row=2, column=1)

    # Email
    ttk.Label(register_window, text="Email").grid(row=3, column=0)
    email = ttk.Entry(register_window)
    email.grid(row=3, column=1)

    # Phone Number
    ttk.Label(register_window, text="Phone Number").grid(row=4, column=0)
    phone_number = ttk.Entry(register_window)
    phone_number.grid(row=4, column=1)

    # Gender
    ttk.Label(register_window, text="Gender").grid(row=5, column=0)
    gender_var = StringVar()
    gender_combobox = ttk.Combobox(register_window, textvariable=gender_var, state="readonly")
    gender_combobox['values'] = ("Male", "Female", "Other")
    gender_combobox.grid(row=5, column=1)
    gender_combobox.current(0)
# User Type (User/Admin)
    ttk.Label(register_window, text="User Type").grid(row=8, column=0)
    user_type_var = StringVar()
    user_type_combobox = ttk.Combobox(register_window, textvariable=user_type_var, state="readonly", values=("User", "Admin"))
    user_type_combobox.grid(row=8, column=1)
    user_type_combobox.current(0)
    # Password
    ttk.Label(register_window, text="Password").grid(row=6, column=0)
    password = ttk.Entry(register_window, show="*")
    password.grid(row=6, column=1)

    # Confirm Password
    ttk.Label(register_window, text="Confirm Password").grid(row=7, column=0)
    confirm_password = ttk.Entry(register_window, show="*")
    confirm_password.grid(row=7, column=1)

    # Register Button
    ttk.Button(register_window, text="Register", command=lambda: register_user(
        first_name.get(), last_name.get(), username.get(), email.get(), phone_number.get(), gender_var.get(), password.get(), confirm_password.get())).grid(row=9, column=1)


    print("Register window opened")

def open_login_window():
    login_window = Toplevel(root)
    login_window.title("Login")

    ttk.Label(login_window, text="Username").grid(row=0, column=0)
    username_login = ttk.Entry(login_window)
    username_login.grid(row=0, column=1)

    ttk.Label(login_window, text="Password").grid(row=1, column=0)
    password_login = ttk.Entry(login_window, show="*")
    password_login.grid(row=1, column=1)
    ttk.Button(login_window, text="Login", command=lambda: login_user(username_login.get(), password_login.get())).grid(row=2, column=1)
complaint_categories = [
    "Academic Issues", "Facility and Infrastructure", "Accommodation/Housing", 
    "Financial Services", "IT and Technical Support", "Health Services", 
    "Campus Safety and Security", "Student Services", "Extracurricular Activities", 
    "Transportation and Parking", "Dining Services", "Administration and Staff", 
    "Environmental/Sustainability Issues", "Harassment or Discrimination", "Miscellaneous/Other"
]
print("Login window opened")

root = tk.Tk()
root.title("Complaint Management System")

# Apply a style that affects all widgets
style = ttk.Style()
style.configure('TFrame', background='black')
style.configure('TLabel', background='black', foreground='white', font=('Helvetica', 24, 'bold'))
style.configure('TButton', font=('Helvetica', 18), padding=10)

frm = ttk.Frame(root, padding=20, style='TFrame')
frm.grid(sticky=(tk.EW, tk.NS))

# Use grid column configuration for equal button widths
frm.columnconfigure(0, weight=1)
frm.columnconfigure(1, weight=1)

ttk.Label(frm, text="Complaint Management System").grid(column=0, row=0, columnspan=2, pady=20)
ttk.Button(frm, text="Register", command=open_register_window).grid(column=0, row=1, sticky=tk.EW, padx=20)
ttk.Button(frm, text="Login", command=open_login_window).grid(column=1, row=1, sticky=tk.EW, padx=20)

# Adjust the main window's size if necessary
root.geometry("600x200")  
root.mainloop()
