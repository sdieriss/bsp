#!/usr/bin/env python3
from db_details import *
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import create_engine, MetaData, Table, select, and_, insert, update

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = '%(asctime)s %(filename)s: %(message)s'
logging.basicConfig(filename="errors.log", format=log_format)

metadata = MetaData()

engine = create_engine('mysql://'+USER+':'+PW+'@'+HOST+'/bank_project_db')
connection = engine.connect()

# Reflect transactions and accounts table from the engine
transactions = Table('transactions', metadata, autoload=True, autoload_with=engine)
accts_table = Table('accounts', metadata, autoload=True, autoload_with=engine)

class Account:
    '''
    Class to store Bank Accounts

    Attributes:
        account_type: String with the Type of Account
        account_number: String The unique identification number of account
        customer_id: Integer with The Customer identifier linked to account
        balance: Decimal with The Account's Balance

    Methods:
        get_acct: Retrieve Account by Customer Id
        deposit: Adds amount to account
        withdrawal: Deducts amount from account
        get_balance: Returns the balance of the account
    '''
    def __init__(self, account_type, customer_id, initial_amount, account_number):
        """
            Account Init

            Args:
                account_type: String account_type
                customer_id: String Customer id
                initial_amount: Decimal initial amount
                account_number: Integer Acount Number

        """
        self.account_type = account_type
        self.account_number = account_number
        self.customer_id = customer_id
        self.balance = initial_amount 
    
    @classmethod
    def get_acct (cls, id):

        """
            Retrieve Account by The Account ID

            Args:
                id: Integer Account id
               
            Returns:
                Customer Class

        """
    

        stmt = select([accts_table]).where(and_(accts_table.columns.account_no == id))
        results = connection.execute(stmt).fetchall()

        if len(results) == 0:
            print("Username or Password is invalid. GoodBye.")
            logging.error("Invalid Credentials", exc_info=True)

        else:
            if results[0].balance is None:
                str_balance  = "0"
            else:
                str_balance  = str(results[0].balance)
            
            cls.balance = float(str_balance)
            cls.account_number = results[0].account_no
            cls.account_type = results[0].account_type
            cls.customer_id = results[0].customer_id

            balance_dec = Decimal(str_balance).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
            return cls(results[0].account_type, results[0].customer_id, balance_dec, results[0].account_no)    
        

    def deposit (self, deposit_amount):
        """
            Adds amount to account

            Args:
                deposit_amount: Decimal amount to be deposited
               
        """
    
        self.transacation_number = 0
        self.balance += deposit_amount
        stmt  = insert(transactions).values(account_no=self.account_number,description="Deposit", amount=deposit_amount)
        result_proxy = connection.execute(stmt)
        stmt = update(accts_table)
        stmt = stmt.where(accts_table.columns.account_no == self.account_number)
        stmt = stmt.values(balance =self.balance)
        result_proxy  = connection.execute(stmt)

    def withdrawal (self, withdrawal_amount):
        """
            Deducts amount from account

            Args:
                withdrawal_amount: Decimal amount to be deducted
               
        """
        if (withdrawal_amount > self.balance) and (self.account_type == "Checking" or self.account_type == "Savings"):
            print("***Can not withdraw. Withdrawal Amount is greater than the balance.")
            logging.error("Can not withdraw amount is greater than the balance", exc_info=True)

      
        else: 
            self.balance -= withdrawal_amount          
            stmt  = insert(transactions).values(account_no=self.account_number,description="Withdrawal", amount=withdrawal_amount)
            result_proxy = connection.execute(stmt)
       
            stmt = update(accts_table)
            stmt = stmt.where(accts_table.columns.account_no == self.account_number)
            stmt = stmt.values(balance = self.balance)
            result_proxy  = connection.execute(stmt)
            print("Transactions completed")
    
    def get_balance(self):
        """
            Return the Account balance

            Args:
                None
               
            Returns:
                Decimal balance
        """
        return self.balance


