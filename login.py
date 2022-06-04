#!/usr/bin/env python3

import getpass
from sqlalchemy import create_engine, MetaData, Table, select, and_
from db_details import *
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = '%(asctime)s %(filename)s: %(message)s'
logging.basicConfig(filename="errors.log", format=log_format)

metadata = MetaData()


engine = create_engine('mysql://'+USER+':'+PW+'@'+HOST+'/bank_project_db')
connection = engine.connect()


def login_to_acct():
    print("Please enter your userid")
    username = input("")
    print("Please enter your password")
    password = getpass.getpass()
    
    employees_table = Table('employees', metadata, autoload=True, autoload_with=engine)
   
    stmt = select([employees_table]).where(and_(employees_table.columns.username == username, employees_table.columns.password == password))


    results = connection.execute(stmt).fetchall()

    if len(results) == 0:
        print("Username or Password is invalid. GoodBye.")
    else:
        #print(results[0].keys())
        #print(results[0].id)
        return results[0].id, results[0].fname, results[0].lname
