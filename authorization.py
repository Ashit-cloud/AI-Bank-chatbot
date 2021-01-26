import re
import pymongo
import pandas as pd
from pprint import pprint
from pymongo import MongoClient
from datetime import datetime


def clublistitems1(list1):
    str1: str = ''
    for x in list1:
        str1 += str(x)
    result = str1
    return result


def auth_input(user):
    aut_input = []
    cust_id = []
    cust_dob = []
    cust_name = []

    for i in user:
        i = i.lower()
        if "customer id" in i:
            cs_id = re.findall('[0-9]+', i)
            cs_id = clublistitems1(cs_id)
            cust_id.append(cs_id)
        elif "first name" in i:
            nam = i.replace("first name is ", '')
            nam = nam.capitalize()
            cust_name.append(nam)
        elif "date of birth is" in i:
            dob = re.search(r'\d{2}-\d{2}-\d{4}', i)
            date = datetime.strptime(dob.group(), '%d-%m-%Y')
            date = date.strftime("%d-%m-%Y")
            cust_dob.append(date)

    # print(cust_id)
    # print(cust_name)
    # print(cust_dob)
    aut_input.append(cust_id[-1])
    aut_input.append(cust_name[-1])
    aut_input.append(cust_dob[-1])
    print("aut_input: ", aut_input)
    return aut_input


def processing(user):
    inpt = auth_input(user)
    customer_id = inpt[0]     # [ we should feed the input to Chatbot sequence wise like customer_id, name, and dob ]
    name = inpt[1]
    dob = inpt[2]
    in_dict = {"Customer_id": customer_id, "First_name": name, "Date_of_birth": dob}
    print('in_dict: ', in_dict)
    return in_dict

# "Customer_id": customer_id , "First_name": name, "Date_of_birth": dob
# "Customer_id": '1001436' , "First_name": 'Mohdkhalid', "Date_of_birth": '05-03-1967'
# in_dict = {"Customer_id": '1000040', "First_name": 'Pradeep', "Date_of_birth": '08-10-1968'}
# in_dict = {"Customer_id": '1001436' , "First_name": 'Mohdkhalid', "Date_of_birth": '05-03-1967'}

def main(in_dict):
    global res
    db_client = MongoClient()
    db = db_client.Personal_Loan
    db = db.Personal_Loan_Customers
    res = db.find_one(in_dict)
    # pprint(res)
    return res


auth_count = 1
def auth_result(user):
    global auth_count
    dict = processing(user)
    res = main(dict)
    if res is None:
        if auth_count == 1:
            response = "not_auth"
            auth_count += 1
            return response
        elif auth_count == 2:
            response = "not_auth1"
            auth_count = 1
            return response
    else:
        response = "Thank you for the authentication. "
        return response


def cust_data(user):
    dict = processing(user)
    res = main(dict)
    return res

