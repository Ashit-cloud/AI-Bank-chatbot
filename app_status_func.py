import pymongo
import re
import pandas as pd
from pymongo import MongoClient
from datetime import datetime


def status_input(query):
    global app_id
    if "application number" in query:
        app_id = re.findall('[0-9]+', query)
        app_id = 'pl' + str(app_id[0])
        print(app_id)

    stat_dict = {"ApplicationNo": app_id}
    return stat_dict

# pl58995

def pulldata(app_num):
    global res
    db_client = MongoClient()
    db = db_client.Personal_Loan
    db = db.Personal_Loan_Applications
    res = db.find_one(app_num)
    print(res)
    return res

def application_status(query):
    input = status_input(query)
    app_data = pulldata(input)
    app_date = app_data['Application_Date']
    app_date = pd.to_datetime(app_date).date()
    # print(app_date)
    date_today = datetime.now().date()
    # print(date_today)
    days_diff = date_today - app_date
    result = days_diff.days
    if result <= 15:
        response = "Your application is in process. Please wait at least 10 working days. " \
                   "Just before you leave I would like to inform you that our bank offers you a Accidental Policy " \
                   "worth 5 lacs. Would you like to know more about the offer"
        return response
    elif result > 15:
        response = "I regret to inform you that your application has been denied. " \
                   "Please wait at least 60 working days before you apply again. " \
                   "Just before you leave I would like to inform you that our bank offers you a Accidental Policy " \
                   "worth 5 lacs. Would you like to know more about the offer"
        return response

# query = 'application number pl63046'
#
# res = application_status(query)
# print(res)