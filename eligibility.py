import pandas as pd
from datetime import date, datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
import pickle
from time import sleep
import re


# load the model from disk
file_name = './models/eligibility_model.sav'
model_eli = pickle.load(open(file_name, 'rb'))


def clublistitems(list1):
    str1 = ''
    for x in list1:
        str1 += str(x)
    result = str1
    return result


def eligibility_input(user):
    eli_inputs = []
    name_inputs = []
    gen_inputs = []
    dob_inputs =[]
    income_inputs =[]
    expense_inputs = []
    company_inputs = []
    experience_inputs = []

    for x in user:
        x = x.lower()
        if "my name is" in x:
            name = x.replace("my name is ", '')
            name_inputs.append([name])
            gen = gender_code(name)
            gen_inputs.append([gen])
        elif "date of birth is" in x or "date is" in x:
            dob = re.findall('[0-9]+', x)
            dob = clublistitems(dob)
            dob_inputs.append(dob)
        elif "net income" in x:
            net_income = re.findall('[0-9]+', x)
            netin = clublistitems(net_income)
            income_inputs.append([netin])
        elif "total expenses" in x:
            total_exp = re.findall('[0-9]+', x)
            totalexp = clublistitems(total_exp)
            expense_inputs.append([totalexp])
        elif "company name" in x or "business name" in x:
            if "company name" in x:
                company_name = x.replace('company name ', '')
                company_inputs.append([company_name])
            else:
                company_name = x.replace('business name ', '')
                company_inputs.append([company_name])
        elif "total experience" in x:
            exp = [int(s) for s in x.split() if s.isdigit()]
            experience_inputs.append(exp)

    eli_inputs.append(name_inputs[-1])
    eli_inputs.append(gen_inputs[-1])
    eli_inputs.append(dob_inputs[-1])
    eli_inputs.append(income_inputs[-1])
    eli_inputs.append(expense_inputs[-1])
    eli_inputs.append(company_inputs[-1])
    eli_inputs.append(experience_inputs[-1])
    print("Inputs -", eli_inputs)
    return eli_inputs


def calculateAge(birthDate):
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
    print("Age: ", age)
    return age


df_company = pd.read_csv('./data/Company_list.csv')
def company_rank(name):
    name = name.lower()
    if name in df_company['Company_name']:
        rank = df_company['Rank']
        return rank
    else:
        rank = 3
        return rank


df_name = pd.read_csv('./data/Indian-Male-Names.csv')
def gender_code(name):
    name.lower()
    name = name.split(' ')
    if any(name[0]) in df_name['name']:
        gen = 1
    else:
        gen = 0
    return gen


def inputs_processing(user):
    global savings
    inputs = eligibility_input(user)
    gen = inputs[1][0]
    dob = inputs[2]
    c_date = datetime.strptime(dob, '%d%m%Y').strftime('%Y-%m-%d')
    db = pd.to_datetime(c_date)  # convert into datetime
    age = calculateAge(db)
    income = inputs[3][0]
    expenses = inputs[4][0]
    savings = int(income) - int(expenses)
    company_name = inputs[5][0]
    rank = company_rank(company_name)
    exp = inputs[6][0]
    exp = int(exp)
    user_input_dict = {"Age":int(age), "Income": int(income), "Expenses": int(expenses),
                       "Company": int(rank), "Experience": int(exp), "Gender_m": int(gen)}

    print("Input_dict: ", user_input_dict)
    input_df = pd.DataFrame(user_input_dict, index=[0])
    print('Input_df: ', input_df)
    return input_df


def find_eligibility(input):
    pred = model_eli.predict(input)
    print("Eligibility_score: ", pred[0])
    return pred[0]

def eligibility_response(user):
    global savings
    sleep(2)
    inputs_df = inputs_processing(user)
    result = find_eligibility(inputs_df)
    if result == 0:
        response = "I regret to inform you that, currently you are not eligible for the loan. " \
                   "However, you may try again after few months. Just before you leave I would like to inform you " \
                   "that our bank offers you a Accidental Policy worth 5 lacs. " \
                   "Would you like to know more about the offer"
    else:
        amount = (int(savings)*12)*3
        formatted_currency = "{}".format(amount)
        response = "Congratulations!!, you are eligible for a loan, up to Rupees {}. " \
                   "Would you like to apply for the loan".format(formatted_currency)
    return response
