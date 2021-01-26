import nltk
import pickle
from datetime import datetime

from authorization import *
from after_auth_reply import *
from recomm_func import *

filename = './models/model_hotelreviews.pkl'


def predict(query):
    model = pickle.load(open(filename, 'rb'))

    sent = model.predict([query])
    if sent[0] == 0:
        return "Negative"
    else:
        return "Positive"


sent_count = 1


def sentiment_check(query, user):
    global sent_count
    c = datetime.now()
    refTime = (c.hour * 60 * 60) + (c.minute * 60) + c.second
    result = predict(query)
    result1 = auth_input(user)
    customer_id = result1[0]
    print('sent_customer_id: ', customer_id)
    if result == 'Positive':
        res = recommResponse(customer_id)
        response = "Thanks for your feedback. " + res
        return response
    elif result == 'Negative':
        if sent_count == 1:
            response = "I am sorry as I understand that you are not satisfied with the charges, however, " \
                       "I see the charges has been applied as per the terms and conditions you have agreed " \
                       "to get this loan. I would advice you to opt for auto pay facilities to avoid late payments." \
                       "       Does this resolve your query? (Please answer in yes or no)"
            sent_count += 1
            return response
        elif sent_count == 2:
            ref_num = '1000' + str(refTime)
            response = "I am sorry to hear that you are still not satisfied. Hence, I am raising an escalation. " \
                       "Please note that you will receive a call back form a live agent with in 24hrs. " \
                       "Your reference number is {}. " \
                       "Just before you leave I would like to inform you that our bank offers you a" \
                       " Accidental Policy worth 5 lacs. Would you like to know more about the offer".format(ref_num)
            return response

# customerId = 1000055
# result = recomm_product(customerId, df_matrix, loaded_model)
# print(result)
