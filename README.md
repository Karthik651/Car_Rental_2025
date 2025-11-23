# Car_Rental_2025
Car Rentals Management System (CRMS)
Car Rental Management System GitHub Link: [https://github.com/Karthik651/Car_Rental_2025](https://github.com/Karthik651/Car_Rental_2025)Project ID: V574J557,Karthik Garidepalli

General Project Information Project Title: Car Rental Management System

Programming Language: Python

Database Software: MySQL

Purpose: The Car Rental Management System is a desktop-based GUI application developed in Python using the Tkinter and ttkbootstrap libraries for a modern UI experience. It connects to a MySQL backend (CarRentalDB) and enables seamless management of customers, vehicles, rentals, and invoices through CRUD operations. The system is designed to support the operational needs of a car rental business by streamlining processes such as booking management, rental tracking, and financial reporting.

Git Commit Note Note: This project was developed and tested locally on my machine. Git commits were made towards the end of the development cycle due to offline development.

Project Demo YouTube Demo: https://youtu.be/4-K_9BYB4Nc

Database Description The CarRentalDB database is structured to manage a car rental company’s operations efficiently. It enables tracking of customer records, car inventory, rental transactions, and invoice management with referential integrity. By using MySQL Server as the RDBMS, the database ensures reliable storage and access control. This setup supports business insights and data-driven decisions, such as identifying high-performing vehicles and tracking customer rental patterns.

Tables and Structure

Customers Table Attributes: customer_id (PK), first_name, last_name, email, phone
Functional Dependencies: customer_id → all other fields

Normalization: 3NF

Sample Data: (1, 'Alice', 'Walker', 'alice.walker@example.com', '555-102-3344')

Cars Table Attributes: car_id (PK), car_type, car_color, car_price
Functional Dependencies: car_id → all other fields

Normalization: 3NF

Sample Data: (1, 'SUV', 'Black', 75.00)

Rentals Table Attributes: rental_id (PK), customer_id (FK), car_id (FK), rental_start_date, rental_end_date
Foreign Key Constraints: ON DELETE CASCADE on customer_id and car_id

Functional Dependencies: rental_id → all other fields

Normalization: 3NF

Sample Data: (1, 1, 1, '2023-11-01', '2023-11-05')

Invoices Table Attributes: invoice_id (PK), rental_id (FK), invoice_amount
Foreign Key Constraint: ON DELETE CASCADE on rental_id

Functional Dependencies: invoice_id → rental_id, invoice_amount

Normalization: 3NF
