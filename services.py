#!/usr/bin/env python3

import logging
from Account import Account
from db_details import *
from sqlalchemy import create_engine, MetaData, Table, select, and_, insert, update

logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = '%(asctime)s %(filename)s: %(message)s'
logging.basicConfig(filename="errors.log", format=log_format)

metadata = MetaData()
engine = create_engine('mysql://'+USER+':'+PW+'@'+HOST+'/bank_project_db')
connection = engine.connect()


# Reflect svc_account_details table from the engine
svc_acct = Table('svc_account_details', metadata, autoload=True, autoload_with=engine)

class Services(Account):
    '''
    Class to store Services for Credit Cards and Loans

    Attributes:
        account_type: String with the Type of Account
        account_number: String The unique identification number of account
        customer_id: Integer with The Customer identifier linked to account
        balance: Decimal with The Account's Balance

    Methods:
        get_acct: Retrieve Account by Account Number
        deposit: Adds amount to account
        withdrawal: Deducts amount from account
  
    '''

    def __init__(self, account_type, customer_id, initial_amount, account_number):
        """
            Services Init

            Args:
                account_type: String account_type
                customer_id: String Customer id
                initial_amount: Decimal initial amount
                account_number: Integer Acount Number

        """

        self.account_type = account_type
        self.customer_id = customer_id
        self.balance = initial_amount
        self.account_number = account_number
        print("Initializing Services init")
        print("--account type {}".format(account_type))
        print("--customer_id {}".format(customer_id))
        print("--initial_amount {}".format(initial_amount))
        print("--account_number {}".format(account_number))   

        stmt = select([svc_acct]).where(and_(svc_acct.columns.account_no == account_number))
        results = connection.execute(stmt).fetchall()
        self.available_balance = results[0].available_balance
        
    @classmethod
    def get_acct(cls, account_no):
      """
            Retrieve Account by The Account Number

            Args:
                account_no: Integer Account Number
               
            Returns:
                Customer Class

      """
      the_account = Account.get_acct(account_no)
       

      stmt = select([svc_acct]).where(and_(svc_acct.columns.account_no == account_no))
       
      results = connection.execute(stmt).fetchall()
      
      cls.available_balance = results[0].available_balance
      print(vars( the_account))
      return cls(the_account.account_type, the_account.customer_id, the_account.balance, the_account.account_number)

        
    
    def withdrawal(self, withdrawal_amount):
        """
            Deducts amount from account

            Args:
                withdrawal_amount: Decimal amount to be deducted
               
        """
        if (self.account_type == 'Loan'):
          print("No additional withdrawals can be made")
          logging.error("Can not withdraw on loans", exc_info=True)     
        elif (self.account_type == 'Credit Card' and withdrawal_amount> self.balance + self.available_balance):
          print("No additional withdrawals can be made")
          logging.error("Can not withdraw on credit cards if withdrawal amounts exceeds balance", exc_info=True)     
        else:
          print("This is the available_balance {}".format(self.available_balance))
          print("This is the account type {}".format(self.account_type))
          print("This is the withdrawal amount {}".format(withdrawal_amount))
          print("This is the balance {}".format(self.balance))
          print("This is the available_balance {}".format(self.available_balance))

          super().withdrawal(withdrawal_amount)
    
    def deposit (self, deposit_amount):
      """
            Adds amount to account

            Args:
                deposit_amount: Decimal amount to be deposited
               
      """
      print("Making a Payment in the amount of ${}".format(deposit_amount))
      super().deposit(deposit_amount)
 
  

   

