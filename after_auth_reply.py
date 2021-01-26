from authorization import *
from datetime import datetime
from recomm_func import *


def lateChargeCheck(user):
    customer_data = cust_data(user)
    # print(customer_data)
    latep_amt = customer_data['Late_payment']
    lastpRevd = customer_data['Last_payrecvd']
    nextDueDate = customer_data['Next_duedate']
    if float(latep_amt) == 0.0:
        resp = "Please be inform that I do not see any late charge in your account, and your next due date is {}. " \
               "Does that answer your query?".format(nextDueDate)
        return resp
    else:
        resp = "I see that the last payment received was on {} and your due date was on {}, and hence there is a " \
               "late fee charged for the amount of {}. The late charge looks valid. " \
               "Please be informed that Accounts not paid within terms are subject to a 20% monthly finance charge. " \
               "Does that satisfy your query?".format(lastpRevd, nextDueDate, latep_amt)
        return resp


def topUpCheck(user):
    global topup_amt
    customer_data = cust_data(user)
    rem_tenure = customer_data['Tenure_rem']
    loan_status = customer_data['Loan_status']
    income = customer_data['Income']
    emi = customer_data['EMI']
    prin_amt = customer_data['Principle_Amount']
    prin_amt = int(prin_amt)
    topup_amt = ((prin_amt * 20)/100) + prin_amt
    if loan_status == 'Active' and (int(rem_tenure) <= 6) and ((float(income) - float(emi)) > float(emi)):
        response = "Congratulations!!, you are eligible for a top-up loan, up to Rupees {}. " \
                   "Would you like to apply for the loan".format(topup_amt)
        return response
    else:
        response = "I regret to inform you that, currently you are not eligible for the top-up loan. " \
                   "However, you may try again after few months. Just before you leave I would like to inform you " \
                   "that our bank offers you a Accidental Policy worth 5 lacs. " \
                   "Would you like to know more about the offer"
        return response


def topup_application(user):
    global topup_amt
    c = datetime.now()
    applicationTime = (c.hour * 60 * 60) + (c.minute * 60) + c.second
    applicationNum = 'tpl' + str(applicationTime)
    result1 = auth_input(user)
    customer_id = result1[0]
    res = recommResponse(customer_id)
    resp = "Your personal loan top-up request has been taken and will be processed with in next 24 hours. " \
               "Your top-up loan application number is {} for the amount of {}. ".format(applicationNum, topup_amt)

    response = resp + res
    return response


def forecloseAmtCheck(user):
    global foreclose_amt
    customer_data = cust_data(user)
    foreclose_amt = customer_data['Foreclosure_amt']
    response = "The foreclosure amount as of today is Rupees {}. " \
               "Do you wish to foreclose the account.".format(foreclose_amt)
    return response


def f_closeRequest(user):
    global foreclose_amt
    c = datetime.now()
    closeTime = (c.hour * 60 * 60) + (c.minute * 60) + c.second
    f_closeRefNum = 'fl' + str(closeTime)
    result2 = auth_input(user)
    customer_id = result2[0]
    res = recommResponse(customer_id)
    resp = "Your request for foreclosure of your personal loan account has been registered. " \
               "Please note your reference number is {}. This request is valid for next 24 hours, " \
               "hence please make the payment of Rupees {} within 24 hours. ".format(f_closeRefNum, foreclose_amt)
    response = resp + res
    return response