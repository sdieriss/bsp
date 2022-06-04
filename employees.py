#!/usr/bin/env python3
import login
import customers
import Account
import services
import logging

from sqlalchemy import create_engine, MetaData, Table, select, and_, insert, update, func, text, exc
from datetime import datetime, timedelta
from db_details import *
from decimal import Decimal, ROUND_HALF_UP

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = '%(asctime)s %(filename)s: %(message)s'
logging.basicConfig(filename="errors.log", format=log_format)

metadata = MetaData()

engine = create_engine('mysql://'+USER+':'+PW+'@'+HOST+'/bank_project_db')
connection = engine.connect()


# Reflect DB tables from the engine
customers_table = Table('customers', metadata, autoload=True, autoload_with=engine)
accounts_table = Table('accounts', metadata, autoload=True, autoload_with=engine)
svc_accounts_table = Table('svc_account_details', metadata, autoload=True, autoload_with=engine)

class Employee:
    '''
    Class to store Bank Employees

    Attributes:
        fname: String with Employee's First Name
        lname: String with Employee's Last Name
        id: Integer with Employee Unique Identification Number
  

    Methods:
        add_customer: creates new customer
        create_account: creates new account
        view_customer: Retrieve Customer
        view_account: Retrieve Account
        service_center: Options to add new loan, add new credit card, make payments an withdraw
        deposit_to_acct: Adds Funds to General Account
        withdraw_from_acct: Deducts Funds from General Account

        
    '''
    def __init__(self, id, first_name, last_name):
        """
            Employee Init

            Args:
                first_name: String First name
                last_name: String Last name
                

        """
        self.fname = first_name
        self.lname = last_name
        self.id = id

    @staticmethod   
    def add_customer():
        """
            creates new customer

            Args:
                None
               
            Returns:
                None    

        """
        print("add_customer")
        first_name = input("Enter Customer's First Name:  ")
        last_name = input("Enter Customer's Last Name:  ")
        phone = input("Enter Customer's Phone:  ")
        email = input("Enter Customer's e-mail:  ")
        address = input("Enter Customer's Address line 1:  ")
        city = input("Enter Customer's City: ")
        state = input("Enter Customer's State:  ")
        zipcode = input("Enter Customer's Zipcode:  ")

        stmt  = insert(customers_table).values(fname=first_name, lname=last_name, phone=phone, email=email, address_line1=address, city=city, state=state, zip=zipcode)
        results = connection.execute(stmt)


    @staticmethod 
    def create_account(acct_entry):
        """
            creates account

            Args:
                acct_entry: Integer 0 for regular accounts, 3 for loans, 4 for credit cards
               
            Returns:
                None    

        """
        print("Getting Ready to Create Account")
        if (acct_entry == 0):
            print('''
            Enter 1 for Checking
            Enter 2 for Savings 
            ''')
            entry = input()
        else: 
            entry = acct_entry
        
        try: 
            if(int(entry) == 1):  
                account_type = "Checking"
            elif (int(entry) == 2):  
                account_type = "Savings"
            elif (int(entry) == 3):  
                account_type = "Loan"
            elif (int(entry) == 4):  
                account_type = "Credit Card"
            else:
                print("Invalid Selection Goodbye.")
                logging.error("Invalid Selection", exc_info=True)

        except Exception:
            print("Exception encountered: ")
            logging.error("Exception encountered", exc_info=True)


        customer_id = input("Enter Customer's ID:  ")
        
        stmt  = insert(accounts_table).values(account_type=account_type, customer_id=customer_id, balance=0)
    
        results = connection.execute(stmt)
      
        curr_customer = customers.Customer.get_customer_by_id(int(customer_id))
     
        print("These are the exisiting accounts {}".format(curr_customer.account_list))
        loan_acct_no = int(results.lastrowid)
        if curr_customer.account_list is None:
            new_account_list = str(results.lastrowid)
        else:
            new_account_list = curr_customer.account_list + ',' + str(results.lastrowid)
        print("new list {}".format(new_account_list))
        print(curr_customer.id)
        stmt = update(customers_table)
        stmt = stmt.where(customers_table.columns.id == customer_id)
        stmt = stmt.values(accounts = new_account_list)
        result_proxy  = connection.execute(stmt)
    
        if (acct_entry == 3):
            print("Add Loan Details")

            print("Enter Loan Amount")
            loan_amt = input()
            print("Enter Length of Loan in Years - Example 1, 3, 5, or 7")
            loan_length = input()
            print("Enter Credit Score")
            credit_score = input()
            
            #arbitrary credit scores and interest_rates can be set as variable instead
            if (int(credit_score) >= 720):
                interest_rate = 5.99
            elif (int(credit_score)  >= 620 and int(credit_score) <= 719):
                interest_rate = 10.99
            else:
                interest_rate = 20.99

          

            #calculate monthly payment ( a(r/n) )
            monthly_payments =  int(loan_amt)*(interest_rate/100)/(12)
            print("Monthly Payment: {}".format(monthly_payments))

            loan_date = "INTERVAL " + loan_length +  " Year"
            print(loan_date)

            loan_days = int(loan_length) * 365
           
            #calculate maturity date
            maturity_date = datetime.now() + timedelta(days=loan_days)

    
            print(str(maturity_date)) 
    

            try:
                
                stmt  = insert(svc_accounts_table).values(account_no=results.lastrowid, monthly_payments=monthly_payments, interest_rate=float(interest_rate), available_balance=0, maturity_date=maturity_date )
                results = connection.execute(stmt)
               
                loan_balance = (Decimal(loan_amt).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)) * -1
                print("This is the amount that will be used {} on {}".format(loan_balance, loan_acct_no ))

                stmt = update(accounts_table)
                stmt = stmt.where(accounts_table.columns.account_no == loan_acct_no )
                stmt = stmt.values(balance =  loan_balance)
                result_proxy  = connection.execute(stmt)
            except exc.SQLAlchemyError as e:
                logging.error("SQLAlchemyError", exc_info=True)


        

        elif (acct_entry == 4):
            print("Add Credit Details")
            print("Credit Limit")
            credit_amt = input()
            print("Enter Credit Score")
            credit_score = input()
            
            #arbitrary credit scores and interest_rates can be set as variable instead
            if (int(credit_score) >= 720):
                interest_rate = 5.99
            elif (int(credit_score)  >= 620 and int(credit_score) <= 719):
                interest_rate = 10.99
            else:
                interest_rate = 20.99

          

            #calculate monthly payment
            monthly_payments =  int(credit_amt)*.01
            print("Monthly Payment: {}".format(monthly_payments))

         

            expiration = 5 * 365
            #calculate maturity date
           
            maturity_date = datetime.now() + timedelta(days=expiration)

    
            print(str(maturity_date)) 
    

            try:
                stmt  = insert(svc_accounts_table).values(account_no=results.lastrowid, monthly_payments=monthly_payments, interest_rate=float(interest_rate), available_balance=float(credit_amt), maturity_date=maturity_date)
                results = connection.execute(stmt)
            except exc.SQLAlchemyError as e:
                print(type(e))

    def view_customer(self):
        """
            Retrieve Customer by The Customer e-mail or id

            Args:
                None
               
            Returns:
                None

        """
        print("view customer")
        print('''
        Enter 1 to search by id
        Enter 2 to search by e-mail
        ''')
        entry = input() 
        
        try: 
            if(int(entry) == 1):  
                print("Enter the ID: ")
                customer_id = input()
                the_customer = customers.Customer.get_customer_by_id(int(customer_id))
                print("Customer retrieved!")
            elif (int(entry) == 2): 
                print("Enter the email: ")
                customer_email = input() 
                the_customer = customers.Customer.get_customer_by_email(customer_email)
            else:
                print("Invalid Selection Goodbye.")
                logging.error("Invalid Selection", exc_info=True)

        except Exception:
            print("Exception Encountered")
            logging.error("Exception Encountered", exc_info=True)

        
        curr_customer_details = vars(the_customer)
        print(curr_customer_details)
      
    

    
 
    def view_account(self):
        """
            Retrieve Customer Account

            Args:
                None
               
            Returns:
                None

        """
       
        print('''
        Enter Account ID
        ''')
        entry = input() 

        
        try: 
            the_acct = Account.Account.get_acct(int(entry))
            
        except Exception:
            print("Exception encountered: ")
            logging.error("Exception encountered", exc_info=True)

        
        curr_acct_details = vars(the_acct)
        print(curr_acct_details)

    def service_center(self):
        """
            Options to add new loan, add new credit card, make payments an withdraw

            Args:
                None
               
            Returns:
                None

        """
        
        print('''
        Enter 1 Add New Loan
        Enter 2 Add New Credit Card
        Enter 3 Make a Payment
        Enter 4 Withdraw
        ''')
        entry = input() 
        
        try: 
            if(int(entry) == 1):  

                #__init__(self, account_type, customer_id, initial_amount, interest_rate)
                
                print("Adding New Loan")
                self.create_account(3)
                

               
            elif (int(entry) == 2): 
                print("Adding New Credit Card")
                self.create_account(4)
               
            elif (int(entry) == 3): 
                print("Make Payment")
                print("Enter Account Number")
                account_no = input()
                service_acct = services.Services.get_acct(account_no)
                print (type(service_acct))
                print("Enter Payment Amount")
                payment_amount = input()
                dec_payment_amount = (Decimal(payment_amount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)) 
                service_acct.deposit(dec_payment_amount)
            
            elif (int(entry) == 4): 
                print("Withdraw")
                #self.create_account(4)
                print("Enter Account Number")
                
                account_no = input()
                service_acct = services.Services.get_acct(account_no)
                print("Enter Amount to Withdraw")
                withdraw_amount = input()
                dec_withdraw_amount = (Decimal(withdraw_amount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)) 
                service_acct.withdrawal(dec_withdraw_amount )
            else:
                print("Invalid Selection Goodbye.")
                logging.error("Invalid Selection", exc_info=True)

        except Exception:
            print("Exception Encountered")
            logging.error("Can not withdraw amount is greater than the balance", exc_info=True)
    
    def deposit_to_acct(self):
        """
            Adds Funds to General Account

            Args:
                None
               
            Returns:
                None

        """
       
        print("Enter Account ID")
        entry = input() 

        
        try: 
            the_acct = Account.Account.get_acct(int(entry))
            print("Current Balance: {} ". format(the_acct.balance))
            print("Enter Amount to Deposit")
            amount = input()
            amount_dec = Decimal(amount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            if the_acct.account_type == 'Checking' or the_acct.account_type == 'Savings':
                the_acct.deposit(amount_dec)
                print("Current Balance: {} ". format(the_acct.balance))

            else:
                print("Please use the service center for non-general accounts")
                logging.error("Attempt to Deposit to non-general account", exc_info=True)
            
        except Exception:
            print("Exception encountered: ")
            logging.error("Exception encountered", exc_info=True)

        
       # curr_acct_details = vars(the_acct)
      #  print(curr_acct_details)

    def withdraw_from_acct(self):
        """
            Deducts Funds from General Account

            Args:
                None
               
            Returns:
                None

        """
       
        print("Enter Account ID")
        entry = input() 

        
        try: 
            the_acct = Account.Account.get_acct(int(entry))
            print("Current Balance: {} ". format(the_acct.balance))
            print("Enter Amount to withdraw")
            amount = input()
            amount_dec = Decimal(amount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            if the_acct.account_type == 'Checking' or the_acct.account_type == 'Savings':
                the_acct.withdrawal(amount_dec)
                print("Current Balance: {} ". format(the_acct.balance))
                #print("what about this: {}".format(str(the_acct.get_balance())))
            else:
                print("Please use the service center for non-general accounts")
                logging.error("Attempt to Withdraw from non-general account", exc_info=True)
            
        except Exception:
            print("Exception encountered: ")
            logging.error("Exception encountered", exc_info=True)

        

        
   
     
def employee_call():
    (employee_id, employee_fname, employee_lname)  = login.login_to_acct()
    #print("*****REturn{},{},{}".format(employee_id, employee_fname, employee_lname))
    employee = Employee(employee_id, employee_fname, employee_lname)
    print("Hello {},  Please select an option from the following menu".format(employee.fname))
    print('''
            Enter 1 Add Customer
            Enter 2 Look up Customer
            Enter 3 Create Account
            Enter 4 View Account
            Enter 5 Service Center
            Enter 6 Add Funds to General Account
            Enter 7 Withdraw Funds to General Account
            ''')
    selection = input("")
    try: 
           
        if (int(selection) == 1): 
            Employee.add_customer()
        elif (int(selection) == 2):  
            employee.view_customer()
        elif (int(selection) == 3):  
            employee.create_account(0)
        elif (int(selection) == 4):  
            employee.view_account()
        elif (int(selection) == 5):  
            employee.service_center()
        elif (int(selection) == 6):
            employee.deposit_to_acct()
        elif (int(selection) == 7):
            employee.withdraw_from_acct()
        else:
            print("Invalid Selection Goodbye.")
            logging.error("Invalid Selection", exc_info=True)

    except Exception:
            print("Exception Encountered: ")
            logging.error("Exception Encountered", exc_info=True)

        
    