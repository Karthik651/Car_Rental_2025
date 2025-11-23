-- Use the correct database
USE RentalDB;

-- ================= BASIC CRUD EXAMPLES =================

-- READ: View all customers
SELECT * FROM Customers;

-- READ: View all cars
SELECT * FROM Cars;

-- READ: View all rentals
SELECT * FROM Rentals;

-- READ: View all invoices
SELECT * FROM Invoices;

-- READ: View all payments
SELECT * FROM Payments;

-- UPDATE: Change rental end date for a specific rental
UPDATE Rentals
SET rental_end_date = '2023-04-07'
WHERE rental_id = 1;

-- UPDATE: Correct the payment method for a payment
UPDATE Payments
SET payment_method = 'card'
WHERE payment_id = 1;

-- DELETE: Remove invoices with small amounts (example)
DELETE FROM Invoices
WHERE invoice_amount < 100;

-- DELETE: Remove a payment record
DELETE FROM Payments
WHERE payment_id = 3;

-- =============== AGGREGATE / REPORTING QUERIES ===============

-- TOTAL EARNINGS per car (based on invoices)
SELECT
    Cars.car_id,
    Cars.car_type,
    SUM(Invoices.invoice_amount) AS TotalEarnings
FROM Cars
JOIN Rentals  ON Rentals.car_id = Cars.car_id
JOIN Invoices ON Invoices.rental_id = Rentals.rental_id
GROUP BY Cars.car_id, Cars.car_type;

-- TOTAL RENTALS per customer
SELECT
    Customers.customer_id,
    Customers.first_name,
    Customers.last_name,
    COUNT(*) AS TotalRentals
FROM Rentals
JOIN Customers ON Rentals.customer_id = Customers.customer_id
GROUP BY Customers.customer_id, Customers.first_name, Customers.last_name;

-- MOST RENTED CARS
SELECT
    Cars.car_id,
    Cars.car_type,
    COUNT(Rentals.rental_id) AS NumberOfRentals
FROM Cars
JOIN Rentals ON Rentals.car_id = Cars.car_id
GROUP BY Cars.car_id, Cars.car_type
ORDER BY NumberOfRentals DESC;

-- INVOICE PAYMENT STATUS: amount invoiced vs amount paid vs balance
SELECT
    i.invoice_id,
    i.rental_id,
    i.invoice_amount,
    IFNULL(SUM(p.amount), 0) AS total_paid,
    i.invoice_amount - IFNULL(SUM(p.amount), 0) AS balance
FROM Invoices i
LEFT JOIN Payments p ON p.invoice_id = i.invoice_id
GROUP BY i.invoice_id, i.rental_id, i.invoice_amount
ORDER BY i.invoice_id;
