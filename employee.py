import csv
import os
import sys
import logging
EMPLOYEE_FILE = 'employees.csv'
 
 
def add_employee(first_name, last_name):
    with open(EMPLOYEE_FILE, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow([first_name, last_name])
 
 
def list_employees():
    employees_list = []
    if os.path.exists(EMPLOYEE_FILE):
        with open(EMPLOYEE_FILE, newline='') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='"')
 
            for row in reader:
                employees_list.append(' '.join(row))
 
    print(employees_list)
 
 
def remove_all_employees():
    if os.path.exists(EMPLOYEE_FILE):
        os.remove(EMPLOYEE_FILE)
    else:
        print("The file does not exist")
 
 
if __name__ == '__main__':
    actions = {'add_employee': add_employee,
               'list_employees': list_employees,
               'remove_all_employees': remove_all_employees}
 
    action = sys.argv[1]
    args = sys.argv[2:]
    actions[action](*args)