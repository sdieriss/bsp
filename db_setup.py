#!/usr/bin/env python3

#Create Database
#Create Tables with Sample Users
import random 
import mysql.connector
from db_details import *


def create_new_database():
    try:
        print("Connecting to DB")
        project_db = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PW)
        
        cursor = project_db.cursor()
        cursor.execute("CREATE DATABASE bank_project_db")
        print("Creating Database")
    except Exception as db_error:
        print("Error creating new Database {}".format(db_error))
    
    #create Customers
    cursor.execute("USE bank_project_db;")
    cursor.execute(
        """CREATE TABLE customers (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            password VARCHAR(255), 
            fname VARCHAR(255),
            lname VARCHAR(255),
            phone VARCHAR(255),
            email VARCHAR(255),
            address_line1 VARCHAR(255),
            address_line2 VARCHAR(255),
            city VARCHAR(255),
            state VARCHAR(255),
            zip VARCHAR(255),
            country VARCHAR(255),
            member_since DATETIME DEFAULT CURRENT_TIMESTAMP,
            accounts VARCHAR(255)    
            )""")

    #Create Sample User
    cursor.execute(
        """INSERT INTO 
            customers(username, password, fname, lname, phone, email) 
            VALUES ("testUser", "testUser!", "Test", "User", "555-555-5555", "testuser@gmail.com"
            );""")

    #create Employees
    cursor.execute(
        """CREATE TABLE employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            password VARCHAR(255), 
            fname VARCHAR(255),
            lname VARCHAR(255),
            phone VARCHAR(255),
            email VARCHAR(255),
            title VARCHAR(255),
            department VARCHAR(255),
            manager INT
            )""")
    #Create Sample User
    cursor.execute(
        """INSERT INTO 
            employees(username, password, fname, lname, phone, email,title) 
            VALUES ("testEmployee", "testEmployee!", "Test", "Employee", "555-555-5555", "testemployee@gmail.com", "VP"
            );""")
    
    #create Accounts
    cursor.execute(
        """CREATE TABLE accounts (
            account_no BIGINT AUTO_INCREMENT PRIMARY KEY,
            account_type VARCHAR(255),
            customer_id BIGINT,
            date_opened DATETIME DEFAULT CURRENT_TIMESTAMP,
            balance DECIMAL(10,2)
            )""")

    cursor.execute(
        """INSERT INTO 
            accounts(account_type, customer_id, balance) 
            VALUES ("Checking", "1", "1000.000"
            );""")

    cursor.execute(
        """INSERT INTO 
            accounts(account_type, customer_id, balance) 
            VALUES ("Savings", "1", "1000.000"
            );""")
    
    cursor.execute(
        """CREATE TABLE svc_account_details (
            account_no BIGINT PRIMARY KEY,
            monthly payments DECIMAL(10,2)),
            interest_rate DECIMAL(4,2),
			available_balance  DECIMAL(10,2)
			maturity_date DATETIME
            )""")
    #create Transactions
    cursor.execute(
        """CREATE TABLE transactions (
            transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            account_no BIGINT,
            description VARCHAR(255),
            amount DECIMAL(10,2)
            )""")

    cursor.close()
    project_db.close()

if __name__ == '__main__':
    print("Getting Ready to create new Database")
    create_new_database()
    print("All Done")
    
    