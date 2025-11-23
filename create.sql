-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS RentalDB;

-- Use the created database
USE RentalDB;

-- Customers table
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name  VARCHAR(50)  NOT NULL,
    last_name   VARCHAR(50)  NOT NULL,
    email       VARCHAR(100) NOT NULL,
    phone       VARCHAR(15)
    -- FD: customer_id -> first_name, last_name, email, phone
);

-- Cars table
CREATE TABLE IF NOT EXISTS Cars (
    car_id     INT AUTO_INCREMENT PRIMARY KEY,
    car_type   VARCHAR(50)   NOT NULL,
    car_color  VARCHAR(30)   NOT NULL,
    car_price  DECIMAL(10,2) NOT NULL
    -- FD: car_id -> car_type, car_color, car_price
);

-- Rentals table
CREATE TABLE IF NOT EXISTS Rentals (
    rental_id         INT AUTO_INCREMENT PRIMARY KEY,
    customer_id       INT NOT NULL,
    car_id            INT NOT NULL,
    rental_start_date DATE NOT NULL,
    rental_end_date   DATE NOT NULL,
    -- FD: rental_id -> customer_id, car_id, rental_start_date, rental_end_date
    CONSTRAINT fk_rentals_customer
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_rentals_car
        FOREIGN KEY (car_id) REFERENCES Cars(car_id)
        ON DELETE CASCADE
);

-- Invoices table
CREATE TABLE IF NOT EXISTS Invoices (
    invoice_id     INT AUTO_INCREMENT PRIMARY KEY,
    rental_id      INT NOT NULL,
    invoice_amount DECIMAL(10,2) NOT NULL,
    -- FD: invoice_id -> rental_id, invoice_amount
    CONSTRAINT fk_invoices_rental
        FOREIGN KEY (rental_id) REFERENCES Rentals(rental_id)
        ON DELETE CASCADE
);

-- Payments table (5th table)
CREATE TABLE IF NOT EXISTS Payments (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id     INT NOT NULL,
    payment_date   DATE NOT NULL,
    amount         DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20)   NOT NULL,
    -- FD: payment_id -> invoice_id, payment_date, amount, payment_method
    CONSTRAINT fk_payments_invoice
        FOREIGN KEY (invoice_id) REFERENCES Invoices(invoice_id)
        ON DELETE CASCADE
);

-- Trigger to auto-generate invoice after inserting a rental
DELIMITER //

CREATE TRIGGER trg_after_rental_insert
AFTER INSERT ON Rentals
FOR EACH ROW
BEGIN
    DECLARE daily_rate DECIMAL(10,2);
    DECLARE num_days   INT;
    DECLARE total      DECIMAL(10,2);

    -- Get the daily rate for the rented car
    SELECT car_price
      INTO daily_rate
      FROM Cars
     WHERE car_id = NEW.car_id;

    -- Calculate number of days (at least 1 day)
    SET num_days = DATEDIFF(NEW.rental_end_date, NEW.rental_start_date);
    IF num_days <= 0 THEN
        SET num_days = 1;
    END IF;

    -- Calculate total invoice amount
    SET total = daily_rate * num_days;

    -- Insert invoice row
    INSERT INTO Invoices (rental_id, invoice_amount)
    VALUES (NEW.rental_id, total);
END;
//

DELIMITER ;
