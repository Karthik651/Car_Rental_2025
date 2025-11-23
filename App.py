import tkinter as tk
from tkinter import ttk, messagebox

import mysql.connector
import ttkbootstrap as tb


# ==========================
# Database Connection Helper
# ==========================

def connect_db():
    """Create a new MySQL connection."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Toor",
        database="RentalDB"
    )


def run_query(query, tree):
    """Run a SELECT query and render results into a Treeview."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]

        tree.delete(*tree.get_children())
        tree["columns"] = cols
        tree["show"] = "headings"

        for col in cols:
            tree.heading(col, text=col)

        for row in rows:
            tree.insert("", tk.END, values=row)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))


# ==========================
# Customer Functions
# ==========================

def add_customer(first, last, email, phone, tree):
    """Insert a new customer and refresh the given Treeview."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO Customers (first_name, last_name, email, phone)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (first.get(), last.get(), email.get(), phone.get()))
        conn.commit()
        messagebox.showinfo("Success", "Customer added successfully!")

        # Refresh the customer table after adding a new customer
        run_query("SELECT * FROM Customers", tree)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def view_customers(tree):
    """View all customers in the given Treeview."""
    run_query("SELECT * FROM Customers", tree)


# ==========================
# Car / Inventory Functions
# ==========================

def add_car(car_type, car_color, car_price):
    """Insert a new car into the Cars table."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            INSERT INTO Cars (car_type, car_color, car_price)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (car_type.get(), car_color.get(), car_price.get()))
        conn.commit()
        messagebox.showinfo("Success", "Car added successfully!")
        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def view_cars(tree):
    """View all cars in the given Treeview."""
    run_query("SELECT * FROM Cars", tree)


# ==========================
# Main UI Setup
# ==========================

app = tb.Window(themename="superhero")
app.title("Car Rental Management")
app.geometry("1100x750")

notebook = ttk.Notebook(app)
notebook.pack(fill='both', expand=True)

# ==========================
# Customers Tab
# ==========================

cust_tab = ttk.Frame(notebook)
notebook.add(cust_tab, text="Customers")

mode_var = tk.StringVar(value="existing")

mode_frame = ttk.LabelFrame(cust_tab, text="Customer Type")
mode_frame.pack(fill='x', padx=10, pady=5)


def update_mode():
    """Switch between Existing and New customer views."""
    if mode_var.get() == "existing":
        search_container.pack(fill='both', expand=True, padx=10, pady=5)
        add_form_frame.pack_forget()
    else:
        search_container.pack_forget()
        add_form_frame.pack(fill='x', padx=10, pady=5)
        run_query("SELECT * FROM Customers", new_customer_table)


ttk.Radiobutton(
    mode_frame,
    text="Existing",
    variable=mode_var,
    value="existing",
    command=update_mode
).pack(side='left', padx=10)

ttk.Radiobutton(
    mode_frame,
    text="New",
    variable=mode_var,
    value="new",
    command=update_mode
).pack(side='left', padx=10)

search_container = ttk.Frame(cust_tab)

# ----- Left: Search Existing Customer -----

search_frame = ttk.LabelFrame(search_container, text="Search Existing Customer")
search_frame.pack(side='left', fill='y', padx=5, pady=5)

search_field = tk.StringVar()
search_menu = ttk.Combobox(
    search_frame,
    textvariable=search_field,
    values=["customer_id", "first_name", "last_name", "email", "phone"]
)
search_field.set("customer_id")

search_entry = ttk.Entry(search_frame)
search_btn = ttk.Button(search_frame, text="Search")

search_menu.pack(fill='x', padx=5, pady=2)
search_entry.pack(fill='x', padx=5, pady=2)
search_btn.pack(padx=5, pady=5)

# ----- Right: Customer Details & Rental History -----

details_frame = ttk.LabelFrame(
    search_container,
    text="Customer Details and Rental History"
)
details_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

edit_fields = {}
for label in ["First Name", "Last Name", "Email", "Phone"]:
    row = ttk.Frame(details_frame)
    row.pack(fill='x', padx=5, pady=2)
    ttk.Label(row, text=label, width=10).pack(side='left')
    entry = ttk.Entry(row)
    entry.pack(fill='x', expand=True)
    edit_fields[label] = entry

btn_frame = ttk.Frame(details_frame)
btn_frame.pack(pady=5)

update_btn = ttk.Button(btn_frame, text="Update Customer")
delete_btn = ttk.Button(btn_frame, text="Delete Customer")
update_btn.pack(side='left', padx=5)
delete_btn.pack(side='left', padx=5)

cust_info_label = ttk.Label(
    details_frame,
    text="Customer Info:",
    anchor="w",
    justify='left'
)
cust_info_label.pack(fill='x', padx=5, pady=5)

rental_table = ttk.Treeview(details_frame)
rental_table.pack(fill='both', expand=True, padx=5, pady=5)

current_customer_id = tk.IntVar()


def search_customer(search_field_name, search_value_entry, info_label, rental_tree):
    """Search a customer and load their info + rental history."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = f"SELECT * FROM Customers WHERE {search_field_name} LIKE %s"
        cursor.execute(query, (f"%{search_value_entry.get()}%",))
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("Info", "No customer found")
            cursor.close()
            conn.close()
            return

        customer = rows[0]
        current_customer_id.set(customer[0])

        info_label.config(
            text=(
                f"Customer Info:\n"
                f"ID: {customer[0]}\n"
                f"Name: {customer[1]} {customer[2]}\n"
                f"Email: {customer[3]}\n"
                f"Phone: {customer[4]}"
            )
        )

        edit_fields["First Name"].delete(0, tk.END)
        edit_fields["First Name"].insert(0, customer[1])

        edit_fields["Last Name"].delete(0, tk.END)
        edit_fields["Last Name"].insert(0, customer[2])

        edit_fields["Email"].delete(0, tk.END)
        edit_fields["Email"].insert(0, customer[3])

        edit_fields["Phone"].delete(0, tk.END)
        edit_fields["Phone"].insert(0, customer[4])

        rental_query = """
            SELECT
                Rentals.rental_id,
                Cars.car_type,
                Rentals.rental_start_date,
                Rentals.rental_end_date
            FROM Rentals
            JOIN Cars ON Rentals.car_id = Cars.car_id
            WHERE Rentals.customer_id = %s
        """
        cursor.execute(rental_query, (customer[0],))
        rental_rows = cursor.fetchall()

        rental_tree.delete(*rental_tree.get_children())
        rental_tree["columns"] = ["rental_id", "car_type", "start_date", "end_date"]
        rental_tree["show"] = "headings"

        for col in rental_tree["columns"]:
            rental_tree.heading(col, text=col)

        for row in rental_rows:
            rental_tree.insert("", tk.END, values=row)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def update_customer():
    """Update the selected customer's information."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            UPDATE Customers
            SET first_name=%s, last_name=%s, email=%s, phone=%s
            WHERE customer_id=%s
        """
        data = (
            edit_fields["First Name"].get(),
            edit_fields["Last Name"].get(),
            edit_fields["Email"].get(),
            edit_fields["Phone"].get(),
            current_customer_id.get()
        )
        cursor.execute(query, data)
        conn.commit()
        messagebox.showinfo("Success", "Customer updated successfully")
        cursor.close()
        conn.close()

        # Refresh the customer details and rental history
        search_customer(
            search_field.get(),
            search_entry,
            cust_info_label,
            rental_table
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))


def delete_customer():
    """Delete the currently selected customer."""
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this customer?")
    if not confirm:
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Customers WHERE customer_id=%s",
            (current_customer_id.get(),)
        )
        conn.commit()
        messagebox.showinfo("Deleted", "Customer deleted successfully")

        cust_info_label.config(text="Customer Info:")
        for entry in edit_fields.values():
            entry.delete(0, tk.END)
        rental_table.delete(*rental_table.get_children())

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Wire up buttons
search_btn.config(
    command=lambda: search_customer(
        search_field.get(),
        search_entry,
        cust_info_label,
        rental_table
    )
)
update_btn.config(command=update_customer)
delete_btn.config(command=delete_customer)

# ----- Add New Customer Form -----

add_form_frame = ttk.LabelFrame(cust_tab, text="Add New Customer")

form_frame = ttk.Frame(add_form_frame)
form_frame.pack(padx=20, pady=10, fill='x')

f_name = ttk.Entry(form_frame)
l_name = ttk.Entry(form_frame)
email = ttk.Entry(form_frame)
phone = ttk.Entry(form_frame)

fields = [
    ("First Name", f_name),
    ("Last Name", l_name),
    ("Email", email),
    ("Phone", phone)
]

for i, (label_text, entry) in enumerate(fields):
    ttk.Label(form_frame, text=label_text, anchor='w').grid(
        row=i, column=0, sticky='w', padx=5, pady=5
    )
    entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)

form_frame.columnconfigure(1, weight=1)

new_customer_table = ttk.Treeview(add_form_frame)
new_customer_table.pack(fill='both', expand=True, padx=10, pady=10)

ttk.Button(
    add_form_frame,
    text="Add Customer",
    command=lambda: add_customer(
        f_name,
        l_name,
        email,
        phone,
        new_customer_table
    )
).pack(pady=10)

# ==========================
# Inventory (Cars) Tab
# ==========================

inventory_tab = ttk.Frame(notebook)
notebook.add(inventory_tab, text="Inventory")

car_mode_var = tk.StringVar(value="existing")

car_mode_frame = ttk.LabelFrame(inventory_tab, text="Car Type")
car_mode_frame.pack(fill='x', padx=10, pady=5)

current_car_id = tk.IntVar()


def update_car_mode():
    """Switch between Existing and New Car views."""
    if car_mode_var.get() == "existing":
        search_car_container.pack(fill='both', expand=True, padx=10, pady=5)
        add_car_form_frame.pack_forget()
    else:
        search_car_container.pack_forget()
        add_car_form_frame.pack(fill='x', padx=10, pady=5)
        run_query("SELECT * FROM Cars", new_car_table)


ttk.Radiobutton(
    car_mode_frame,
    text="Existing",
    value="existing",
    variable=car_mode_var,
    command=update_car_mode
).pack(side='left', padx=10)

ttk.Radiobutton(
    car_mode_frame,
    text="New",
    value="new",
    variable=car_mode_var,
    command=update_car_mode
).pack(side='left', padx=10)

# ----- Existing Car Search -----

search_car_container = ttk.Frame(inventory_tab)

search_car_frame = ttk.LabelFrame(search_car_container, text="Search Existing Car")
search_car_frame.pack(side='left', fill='y', padx=5, pady=5)

car_search_field = tk.StringVar()
car_search_menu = ttk.Combobox(
    search_car_frame,
    textvariable=car_search_field,
    values=["car_id", "car_type", "car_color"]
)
car_search_field.set("car_id")

car_search_entry = ttk.Entry(search_car_frame)
car_search_btn = ttk.Button(search_car_frame, text="Search")

car_search_menu.pack(fill='x', padx=5, pady=2)
car_search_entry.pack(fill='x', padx=5, pady=2)
car_search_btn.pack(padx=5, pady=5)

car_details_frame = ttk.LabelFrame(search_car_container, text="Car Details")
car_details_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

car_edit_fields = {}
for label in ["Car Type", "Car Color", "Car Price"]:
    row = ttk.Frame(car_details_frame)
    row.pack(fill='x', padx=5, pady=2)
    ttk.Label(row, text=label, width=10).pack(side='left')
    entry = ttk.Entry(row)
    entry.pack(fill='x', expand=True)
    car_edit_fields[label] = entry

car_btn_frame = ttk.Frame(car_details_frame)
car_btn_frame.pack(pady=5)

car_update_btn = ttk.Button(car_btn_frame, text="Update Car")
car_delete_btn = ttk.Button(car_btn_frame, text="Delete Car")
car_update_btn.pack(side='left', padx=5)
car_delete_btn.pack(side='left', padx=5)

car_info_label = ttk.Label(
    car_details_frame,
    text="Car Info:",
    anchor="w",
    justify='left'
)
car_info_label.pack(fill='x', padx=5, pady=5)


def search_car(search_field_name, search_value_entry, info_label):
    """Search a car and populate the details form."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = f"SELECT * FROM Cars WHERE {search_field_name} LIKE %s"
        cursor.execute(query, (f"%{search_value_entry.get()}%",))
        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("Info", "No car found")
            cursor.close()
            conn.close()
            return

        car = rows[0]
        current_car_id.set(car[0])

        info_label.config(
            text=(
                f"Car Info:\n"
                f"ID: {car[0]}\n"
                f"Type: {car[1]}\n"
                f"Color: {car[2]}\n"
                f"Price: ${car[3]}"
            )
        )

        car_edit_fields["Car Type"].delete(0, tk.END)
        car_edit_fields["Car Type"].insert(0, car[1])

        car_edit_fields["Car Color"].delete(0, tk.END)
        car_edit_fields["Car Color"].insert(0, car[2])

        car_edit_fields["Car Price"].delete(0, tk.END)
        car_edit_fields["Car Price"].insert(0, car[3])

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def update_car():
    """Update the selected car."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """
            UPDATE Cars
            SET car_type=%s, car_color=%s, car_price=%s
            WHERE car_id=%s
        """
        data = (
            car_edit_fields["Car Type"].get(),
            car_edit_fields["Car Color"].get(),
            car_edit_fields["Car Price"].get(),
            current_car_id.get()
        )
        cursor.execute(query, data)
        conn.commit()
        messagebox.showinfo("Success", "Car updated successfully")
        cursor.close()
        conn.close()

        # Refresh the car details
        search_car(car_search_field.get(), car_search_entry, car_info_label)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def delete_car():
    """Delete the selected car."""
    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this car?")
    if not confirm:
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Cars WHERE car_id=%s", (current_car_id.get(),))
        conn.commit()
        messagebox.showinfo("Deleted", "Car deleted successfully")

        car_info_label.config(text="Car Info:")
        for entry in car_edit_fields.values():
            entry.delete(0, tk.END)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


car_search_btn.config(
    command=lambda: search_car(
        car_search_field.get(),
        car_search_entry,
        car_info_label
    )
)
car_update_btn.config(command=update_car)
car_delete_btn.config(command=delete_car)

# ----- Add New Car Form -----

add_car_form_frame = ttk.LabelFrame(inventory_tab, text="Add New Car")

car_form_frame = ttk.Frame(add_car_form_frame)
car_form_frame.pack(padx=20, pady=10, fill='x')

car_type_entry = ttk.Entry(car_form_frame)
car_color_entry = ttk.Entry(car_form_frame)
car_price_entry = ttk.Entry(car_form_frame)

car_fields = [
    ("Car Type", car_type_entry),
    ("Car Color", car_color_entry),
    ("Car Price", car_price_entry)
]

for i, (label_text, entry) in enumerate(car_fields):
    ttk.Label(car_form_frame, text=label_text, anchor='w').grid(
        row=i, column=0, sticky='w', padx=5, pady=5
    )
    entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)

car_form_frame.columnconfigure(1, weight=1)

ttk.Button(
    add_car_form_frame,
    text="Add Car",
    command=lambda: add_car(
        car_type_entry,
        car_color_entry,
        car_price_entry
    )
).pack(pady=10)

new_car_table = ttk.Treeview(add_car_form_frame)
new_car_table.pack(fill='both', expand=True, padx=10, pady=10)

# Default to existing car mode view
update_car_mode()

# ==========================
# Rentals Tab
# ==========================

rentals_tab = ttk.Frame(notebook)
notebook.add(rentals_tab, text="Rentals")

rental_mode_var = tk.StringVar(value="existing")

rental_mode_frame = ttk.LabelFrame(rentals_tab, text="Rental Mode")
rental_mode_frame.pack(fill='x', padx=10, pady=5)


def update_rental_mode():
    """Switch between Existing rental management and New rental form."""
    if rental_mode_var.get() == "existing":
        modify_rental_frame.pack(fill='both', expand=True, padx=10, pady=5)
        create_rental_frame.pack_forget()
    else:
        create_rental_frame.pack(fill='x', padx=10, pady=5)
        modify_rental_frame.pack_forget()


ttk.Radiobutton(
    rental_mode_frame,
    text="Existing Rentals",
    variable=rental_mode_var,
    value="existing",
    command=update_rental_mode
).pack(side='left', padx=10)

ttk.Radiobutton(
    rental_mode_frame,
    text="New Rental",
    variable=rental_mode_var,
    value="new",
    command=update_rental_mode
).pack(side='left', padx=10)

# ----- Create New Rental -----

create_rental_frame = ttk.LabelFrame(rentals_tab, text="Create New Rental")

rental_form = ttk.Frame(create_rental_frame)
rental_form.pack(padx=20, pady=10, fill='x')

cust_id_entry = ttk.Entry(rental_form)
car_id_entry = ttk.Entry(rental_form)
start_entry = ttk.Entry(rental_form)
end_entry = ttk.Entry(rental_form)

rental_labels = [
    "Customer ID",
    "Car ID",
    "Start Date (YYYY-MM-DD)",
    "End Date (YYYY-MM-DD)"
]
rental_entries = [cust_id_entry, car_id_entry, start_entry, end_entry]

for i, (label_text, entry) in enumerate(zip(rental_labels, rental_entries)):
    ttk.Label(rental_form, text=label_text, anchor="w").grid(
        row=i, column=0, sticky="w", padx=5, pady=5
    )
    entry.grid(row=i, column=1, sticky="ew", padx=5, pady=5)

rental_form.columnconfigure(1, weight=1)

estimated_price_label = ttk.Label(
    create_rental_frame,
    text="Estimated Invoice: $0.00",
    font=("Helvetica", 10, "bold")
)
estimated_price_label.pack(pady=5)


def estimate_rental():
    """Estimate rental cost for given dates and car."""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT car_price FROM Cars WHERE car_id = %s",
            (car_id_entry.get(),)
        )
        result = cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Invalid Car ID")
            cursor.close()
            conn.close()
            return

        daily_rate = result[0]

        from datetime import datetime
        start_date = datetime.strptime(start_entry.get(), "%Y-%m-%d")
        end_date = datetime.strptime(end_entry.get(), "%Y-%m-%d")
        num_days = (end_date - start_date).days

        if num_days <= 0:
            messagebox.showerror("Error", "End date must be after start date.")
            cursor.close()
            conn.close()
            return

        total = round(num_days * daily_rate, 2)
        estimated_price_label.config(text=f"Estimated Invoice: ${total}")

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


rental_summary_frame = ttk.LabelFrame(create_rental_frame, text="Rental Summary")
rental_summary_frame.pack(fill='x', padx=20, pady=10)
rental_summary_frame.pack_forget()

rental_summary_label = ttk.Label(
    rental_summary_frame,
    text="",
    justify="left",
    font=("Segoe UI", 10, "bold")
)
rental_summary_label.pack(anchor="w", padx=10, pady=5)


def create_rental_after_estimate():
    """Create a rental, commit to DB, and show a summary (invoice via trigger)."""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Rentals (customer_id, car_id, rental_start_date, rental_end_date)
            VALUES (%s, %s, %s, %s)
            """,
            (cust_id_entry.get(), car_id_entry.get(), start_entry.get(), end_entry.get())
        )
        rental_id = cursor.lastrowid  # noqa: F841 (kept for clarity if needed later)

        cursor.execute(
            "SELECT car_price, car_type FROM Cars WHERE car_id = %s",
            (car_id_entry.get(),)
        )
        car_data = cursor.fetchone()
        if not car_data:
            messagebox.showerror("Error", "Car not found.")
            cursor.close()
            conn.close()
            return

        car_price, car_type_str = car_data

        cursor.execute(
            "SELECT first_name, last_name FROM Customers WHERE customer_id = %s",
            (cust_id_entry.get(),)
        )
        cust_data = cursor.fetchone()
        if not cust_data:
            messagebox.showerror("Error", "Customer not found.")
            cursor.close()
            conn.close()
            return

        cust_full_name = f"{cust_data[0]} {cust_data[1]}"

        from datetime import datetime
        days = (
            datetime.strptime(end_entry.get(), "%Y-%m-%d")
            - datetime.strptime(start_entry.get(), "%Y-%m-%d")
        ).days

        if days <= 0:
            messagebox.showerror("Error", "End date must be after start date.")
            cursor.close()
            conn.close()
            return

        total = round(days * car_price, 2)
        conn.commit()

        summary_text = f"""
Customer: {cust_full_name}
Car Type: {car_type_str}
Duration: {days} day(s)
Cost: ${total}
""".strip()

        rental_summary_label.config(text=summary_text)
        rental_summary_frame.pack(fill='x', padx=20, pady=10)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))


rental_btns = ttk.Frame(create_rental_frame)
rental_btns.pack(pady=10)

ttk.Button(rental_btns, text="Estimate Price", command=estimate_rental).pack(
    side="left", padx=10
)
ttk.Button(
    rental_btns,
    text="Create Rental",
    command=create_rental_after_estimate
).pack(side="left", padx=10)

# ----- View & Modify Existing Rentals -----

modify_rental_frame = ttk.LabelFrame(rentals_tab, text="View & Modify Rentals")

rental_table_view = ttk.Treeview(modify_rental_frame)
rental_table_view.pack(fill='both', expand=True, padx=10, pady=10)


def view_all_rentals():
    """Show all rentals with customer and car information."""
    run_query(
        """
        SELECT
            Rentals.rental_id,
            Customers.first_name,
            Customers.last_name,
            Cars.car_type,
            Rentals.rental_start_date,
            Rentals.rental_end_date
        FROM Rentals
        JOIN Customers ON Rentals.customer_id = Customers.customer_id
        JOIN Cars ON Rentals.car_id = Cars.car_id
        """,
        rental_table_view
    )


ttk.Button(
    modify_rental_frame,
    text="View All Rentals",
    command=view_all_rentals
).pack(pady=5)

update_rental_frame = ttk.LabelFrame(modify_rental_frame, text="Modify Rental")
update_rental_frame.pack(fill='x', padx=10, pady=5)

update_fields = {
    "Rental ID": ttk.Entry(update_rental_frame),
    "Start Date": ttk.Entry(update_rental_frame),
    "End Date": ttk.Entry(update_rental_frame)
}

for label_text, entry in update_fields.items():
    row = ttk.Frame(update_rental_frame)
    row.pack(fill='x', padx=5, pady=2)
    ttk.Label(row, text=label_text, width=15).pack(side='left')
    entry.pack(fill='x', expand=True)


def update_rental():
    """Update a rental's dates and recalculate its invoice."""
    try:
        conn = connect_db()
        cursor = conn.cursor()

        rental_id = update_fields["Rental ID"].get()
        new_start = update_fields["Start Date"].get()
        new_end = update_fields["End Date"].get()

        cursor.execute(
            """
            UPDATE Rentals
            SET rental_start_date = %s, rental_end_date = %s
            WHERE rental_id = %s
            """,
            (new_start, new_end, rental_id)
        )

        cursor.execute(
            """
            SELECT car_price
            FROM Cars
            JOIN Rentals ON Rentals.car_id = Cars.car_id
            WHERE Rentals.rental_id = %s
            """,
            (rental_id,)
        )
        daily_rate_row = cursor.fetchone()
        if not daily_rate_row:
            messagebox.showerror("Error", "Rental or car not found.")
            cursor.close()
            conn.close()
            return

        daily_rate = daily_rate_row[0]

        from datetime import datetime
        num_days = (
            datetime.strptime(new_end, "%Y-%m-%d")
            - datetime.strptime(new_start, "%Y-%m-%d")
        ).days

        if num_days <= 0:
            messagebox.showerror("Error", "End date must be after start date.")
            cursor.close()
            conn.close()
            return

        new_total = round(num_days * daily_rate, 2)

        cursor.execute(
            """
            UPDATE Invoices
            SET invoice_amount = %s
            WHERE rental_id = %s
            """,
            (new_total, rental_id)
        )

        conn.commit()
        messagebox.showinfo("Success", f"Rental updated! New Invoice: ${new_total}")

        cursor.close()
        conn.close()
        view_all_rentals()
    except Exception as e:
        messagebox.showerror("Error", str(e))


def delete_rental():
    """Delete a rental and let FK constraints handle invoice removal."""
    rental_id = update_fields["Rental ID"].get()
    if not rental_id:
        messagebox.showerror("Error", "Enter Rental ID to delete.")
        return

    confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this rental?")
    if not confirm:
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Rentals WHERE rental_id = %s", (rental_id,))
        conn.commit()
        messagebox.showinfo("Deleted", "Rental deleted successfully")
        cursor.close()
        conn.close()
        view_all_rentals()
    except Exception as e:
        messagebox.showerror("Error", str(e))


rental_btn_row = ttk.Frame(update_rental_frame)
rental_btn_row.pack(pady=5)

ttk.Button(
    rental_btn_row,
    text="Update Rental",
    command=update_rental
).pack(side='left', padx=5)
ttk.Button(
    rental_btn_row,
    text="Delete Rental",
    command=delete_rental
).pack(side='left', padx=5)

# default mode
update_rental_mode()

# ==========================
# Reports Tab
# ==========================

report_tab = ttk.Frame(notebook)
notebook.add(report_tab, text="Reports")

frame1 = ttk.LabelFrame(report_tab, text="List All Tables")
frame1.pack(fill='x', padx=10, pady=10)

frame2 = ttk.LabelFrame(report_tab, text="Predefined Queries")
frame2.pack(fill='x', padx=10, pady=10)

report_tree = ttk.Treeview(report_tab)
report_tree.pack(fill='both', expand=True, padx=10, pady=10)

queries = {
    "All Customers": "SELECT * FROM Customers",
    "All Cars": "SELECT * FROM Cars",
    "All Rentals": "SELECT * FROM Rentals",
    "All Invoices": "SELECT * FROM Invoices",
    "All Payments": "SELECT * FROM Payments",
    "Total Earnings per Car": """
        SELECT
            Cars.car_id,
            Cars.car_type,
            SUM(Invoices.invoice_amount) AS TotalEarnings
        FROM Cars
        JOIN Rentals  ON Rentals.car_id = Cars.car_id
        JOIN Invoices ON Invoices.rental_id = Rentals.rental_id
        GROUP BY Cars.car_id, Cars.car_type
    """,
    "Total Rentals per Customer": """
        SELECT
            Customers.customer_id,
            Customers.first_name,
            Customers.last_name,
            COUNT(*) AS TotalRentals
        FROM Rentals
        JOIN Customers ON Rentals.customer_id = Customers.customer_id
        GROUP BY Customers.customer_id, Customers.first_name, Customers.last_name
    """,
    "Most Rented Cars": """
        SELECT
            Cars.car_id,
            Cars.car_type,
            COUNT(Rentals.rental_id) AS NumberOfRentals
        FROM Cars
        JOIN Rentals ON Rentals.car_id = Cars.car_id
        GROUP BY Cars.car_id, Cars.car_type
        ORDER BY NumberOfRentals DESC
    """,
    "Invoice Payment Status": """
        SELECT
            i.invoice_id,
            i.rental_id,
            i.invoice_amount,
            IFNULL(SUM(p.amount), 0) AS total_paid,
            i.invoice_amount - IFNULL(SUM(p.amount), 0) AS balance
        FROM Invoices i
        LEFT JOIN Payments p ON p.invoice_id = i.invoice_id
        GROUP BY i.invoice_id, i.rental_id, i.invoice_amount
        ORDER BY i.invoice_id
    """
}


def run_report(label):
    run_query(queries[label], report_tree)


for label in ["All Customers", "All Cars", "All Rentals", "All Invoices", "All Payments"]:
    ttk.Button(
        frame1,
        text=label,
        width=30,
        command=lambda q=label: run_report(q)
    ).pack(side='left', padx=5, pady=5)

for label in [
    "Total Earnings per Car",
    "Total Rentals per Customer",
    "Most Rented Cars",
    "Invoice Payment Status"
]:
    ttk.Button(
        frame2,
        text=label,
        width=35,
        command=lambda q=label: run_report(q)
    ).pack(side='left', padx=5, pady=5)

# ==========================
# Main Loop
# ==========================

app.mainloop()
