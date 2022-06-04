#!/usr/bin/env python3

import customers
import employees
import logging



logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_format = '%(asctime)s %(filename)s: %(message)s'
logging.basicConfig(filename="errors.log", format=log_format)


print("Welcome to SD Bank! \n") 

time_to_test = True

while time_to_test:
    print("Enter 1 for Existing Customers")
    print("Enter 2 for Employees")
    entry = input("")
  
    try: 
        if(entry == "1"):  
            customers.customer_call()  
        elif (entry == "2"):  
            employees.employee_call()
        else:
            print("Invalid Selection")
            logging.error("Invalid Selection entered at Menu")
    
        print("\n ***Hit enter to continue OR Type quit to exit")

        quit_check = input("")
        if quit_check == "quit":
            time_to_test = False
    except Exception:
        print("An error was encountered")
        logging.error("Exception occurred", exc_info=True)

    