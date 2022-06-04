#!/usr/bin/env python3

import random 
import getpass
import Account
import sys
import logging
from db_details import *
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import create_engine, MetaData, Table, select, and_



logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = '%(asctime)s %(filename)s: %(message)s'
logging.basicConfig(filename="errors.log", format=log_format)

metadata = MetaData()
engine = create_engine('mysql://'+USER+':'+PW+'@'+HOST+'/bank_project_db')

stmt = 'SELECT * FROM customers'
connection = engine.connect()

# Reflect customers table from the engine
customers_table = Table('customers', metadata, autoload=True, autoload_with=engine)

class Customer:
    '''
    Class to store Bank Customers

    Attributes:
        fname: A String with Customer's First Name
        lname: A String with Customer's Last Name
        id: Integer with Customer Unique Identification Number
        account_list: A String listing all the accounts linked to customer seperated by commas

    Methods:
        get_customer_by_id: Retrieve Customer by The Customer ID
        get_customer_by_email: Retrieve Customer by e-mail
        get_accounts: Return the Customer's Account List
        list_accounts: Lists All Acounts and Prompts User to Select One. Returns Selected.
        get_transactions: Displays All Transactions of an Account
        make_transfer: Allows Transfers between Customer Accounts
    '''
    def __init__(self, first_name, last_name, id, accounts):
        """
            Customer Init

            Args:
                first_name: String First name
                last_name: String Last name
                id: Integer Customer id
                accounts: String Acount List

        """
        self.fname = first_name
        self.lname = last_name
        self.id = id
        self.account_list = accounts      

    @classmethod
    def get_customer_by_id(cls, id):
        """
            Retrieve Customer by The Customer ID

            Args:
                id: Integer Customer  id
               
            Returns:
                Customer Class

        """
    
        # Add a where clause to filter the results by customer id
        stmt = select([customers_table]).where(and_(customers_table.columns.id == id))
        
        results = connection.execute(stmt).fetchall()
        if len(results) == 0:
            print("Username or Password is invalid. GoodBye.")
            logging.error("Username or Password is invalid", exc_info=True)

        else:
            print(results[0].accounts)
        return cls(results[0].fname, results[0].lname, results[0].id, results[0].accounts)
    
    
    @classmethod
    def get_customer_by_email(cls, email):

        """
            Retrieve Customer by The Customer e-mail

            Args:
                e-mail: String Customer e-mail
               
            Returns:
                Customer Class

        """
     
        # Add a where clause to filter the results by customer email
        stmt = select([customers_table]).where(and_(customers_table.columns.email == email))
        results = connection.execute(stmt).fetchall()
        return cls(results[0].fname, results[0].lname, results[0].id, results[0].accounts)
    
    def get_accounts(self):
        """
            Return the Customer's Account List

            Args:
                None
               
            Returns:
                String listing all the accounts

        """
        return self.account_list 
  
    def get_customer_id(self):
        """
            Return the Customer's Id

            Args:
                None
               
            Returns:
                String Id
        """
        return self.id

    def list_accounts(self):
      
        """
            Lists All Acounts and Prompts User to Select One

            Args:
                None
               
            Returns:
                Account Selected

        """
        available_accts = self.account_list.split(',')
     
        all_accts = []
        for option, acct in enumerate(available_accts, start = 1):
           
            
            all_accts.append(Account.Account.get_acct(acct))
            
            print("{} - {} Account # {} Available Balance: ${:.2f}".format(option, all_accts[option-1].account_type, acct, all_accts[option-1].balance))
           
        print("Please select an account")
        from_account = input()
        print("You selected {}".format(from_account))
       

        return all_accts[int(from_account)-1].account_number

    
    def get_transactions(self):

        """
            Displays All Transactions of an Account

            Args:
                None
               
            Returns:
                None

        """
        
        transactions = Table('transactions', metadata, autoload=True, autoload_with=engine)
        acct = self.list_accounts()
        
         # Add a where clause to filter the results by account
        stmt = select([transactions]).where((transactions.columns.account_no == acct))

        results = connection.execute(stmt).fetchall()
        if len(results) == 0:
            print("No recent transactions found.")
            logging.error("No transactions found", exc_info=True)

        else:
            print("Transactions" + "\n-----------------------------")
            for items in results:
             print(items.transaction_date, items.description, items.amount)
           
    def make_transfer(self):

        """
            Allows Transfers between Customer Accounts

            Args:
                None
               
            Returns:
                None

        """
        
        print("Please select FROM account")
       
        available_accts = self.account_list.split(',')


        all_accts = []
        #Get All Available Accounts for Customer
        for option, acct in enumerate(available_accts, start = 1):
   
            all_accts.append(Account.Account.get_acct(acct))
     
            print("{} - {} Account # {} Available Balance: ${:.2f}".format(option, all_accts[option-1].account_type, acct, all_accts[option-1].balance))
          
        
        from_account = input()

        print("Please select TO account")
       

        for option, acct in enumerate(available_accts, start = 1):
            if (option == int(from_account)):
                continue
            print("{} - {} Account # {} Available Balance: ${:.2f}".format(option, all_accts[option-1].account_type, acct, all_accts[option-1].balance))
        
        to_account = input()

        print("Amount to Transfer: ")
        amount = input()
        amount_rounded = Decimal(amount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
      

        #Check if amount exceeds balance
        if (amount_rounded > all_accts[int(from_account)-1].balance):
            print("Can not proceed with transaction")
            logging.error("Exception occurred amount is greater than balance", exc_info=True)

        else:
            all_accts[int(from_account)-1].withdrawal(amount_rounded)
            all_accts[int(to_account)-1].deposit(amount_rounded) 
       
        
        
        print("Updated Balances: ")
        print("{} Account # {} Available Balance: ${:.2f}".format(all_accts[int(from_account)-1].account_type, all_accts[int(from_account)-1].account_number, all_accts[int(from_account)-1].balance))
        print("{} Account # {} Available Balance: ${:.2f}".format(all_accts[int(to_account)-1].account_type, all_accts[int(to_account)-1].account_number, all_accts[int(to_account)-1].balance))

        
        
def customer_call():

    """
            Menu Options for Customer. Allows customer to make transfers and view transactions

            Args:
                None
               
            Returns:
                None

    """
    
    print("Please enter your userid")
    username = input("")
    print("Please enter your password")
    password = getpass.getpass()
  

    # Add a where clause to filter the results by username and password
    stmt = select([customers_table]).where(and_(customers_table.columns.username == username, customers_table.columns.password == password))

   
    results = connection.execute(stmt).fetchall()
    if len(results) == 0:
        print("Username or Password is invalid. GoodBye.")
        logging.error("Invalid Credentials", exc_info=True)

    else:
        print(results[0].accounts)
        currentCustomer = Customer(results[0].fname, results[0].lname, results[0].id, results[0].accounts)
       
        print("Welcome back " +  currentCustomer.fname)
        
        customer_test = True
        while customer_test:
            print("Please select an option from the following menu")
            print('''
            Enter 1 to Make a Transfer
            Enter 2 to View Transactions
            ''')
            selection = input("")
       
            try: 
            
                if(int(selection) == 1): 
                    currentCustomer.make_transfer()
                elif (int(selection) == 2):  
                    currentCustomer.get_transactions()
                else:
                    print("Invalid Selection Goodbye.")
                    logging.error("Invalid Selection Entered", exc_info=True)

            except Exception:
                print("Exception has been enecountered please view logs at - " + logging.getLoggerClass().root.handlers[0].baseFilename)
                logging.error("exception occurred", exc_info=True)

            
            print("\n ***Hit enter to continue OR Type quit to return to Main Menu")
            quit_check = input("")
            if quit_check == "quit":
                customer_test = False

        



        

    