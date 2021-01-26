from after_auth_reply import *
from app_status_func import *
from eligibility import *
from pl_apply import *
import random


def responseBased(resp, user, query):
    if resp == "calc_eli":
        response = eligibility_response(user)  # to calculate eligibility
        print('ELE: ', response)
    elif resp == 'apply_pl':
        response = apply_pl(user)  # to apply for personal loan (at end ask anything else)
        print('PLAP: ', response)
    elif resp == 'auth':
        response = auth_result(user)  # to authenticate before entering into the loan account (at end add the concern answer)
        print('AUT: ', response)
    elif resp == 'app_status':
        response = application_status(query)  # to check the loan application status (at end ask anything else)
        print('APST: ', response)
    elif resp == 'f_close':
        response = f_closeRequest(user)  # takes forclosure request
    elif resp == 'topup_request':
        response = topup_application(user)
    elif resp == 'recom':
        response = recommResponse1()
    else:
        response = resp
    return response


def errorResponse():
    resp = [
        "Sorry, I did not understand. How may I help you?",
        "Sorry, I dint get that. Can i help you with something.",
        "Are you looking for assistance."
    ]
    response = random.choice(resp)
    return response