from eligibility import *
import pymongo
import re
from datetime import date, datetime




def find_user_contacts(user):
    phone = []
    email = []
    contact = []
    for x in user:
        if '@' in x:
            e = re.findall('\S+@\S+', x)
            p = re.findall('[0-9]+', x)[0]
            email.append(e)
            phone.append(p)

    contact.append(phone[-1])
    contact.append(email[-1])
    return contact


def apply_pl(user):
    c = datetime.now()
    applicationTime = (c.hour * 60 * 60) + (c.minute * 60) + c.second
    print("Application Time: ", applicationTime)
    inputlist = eligibility_input(user)
    applicationnum = 'pl' +  str(applicationTime)
    name = inputlist[0]
    gender = inputlist[1]
    dob = inputlist[2]
    income = inputlist[3]
    expenses = inputlist[4]
    company = inputlist[5]
    experience = inputlist[6]

    contact = find_user_contacts(user)
    phone = contact[0]
    email = contact[1]
    todays_date = datetime.now().date()

    DEFAULT_CONNECTION_URL = "mongodb://localhost:27017/"
    DB_NAME = "Personal_Loan"
    client = pymongo.MongoClient(DEFAULT_CONNECTION_URL)
    dataBase = client[DB_NAME]
    COLLECTION_NAME = "Personal_Loan_Applications"
    collection = dataBase[COLLECTION_NAME]
    record = {'ApplicationNo': applicationnum,
              'Application_Date': str(todays_date),
              'Name': name,
              'Gender': gender,
              'Dob': dob,
              'Income': income,
              'Expenses': expenses,
              'CompanyName': company,
              'Experience': experience,
              'Phone': phone,
              'Email': email[0]}
    collection.insert_one(record)
    print("Record 1", record)
    response = "Your personal loan application has been submitted. " \
               "Your application number is {}. " \
               "The information has been sent to your email address {}. " \
               "Just before you leave I would like to inform you that our bank offers you a Accidental Policy " \
               "worth 5 lacs. Would you like to know more about the offer".format(applicationnum, email[0])

    return response
