import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from datetime import datetime
from model_training_files.model import *
from flask import Flask, render_template, request
import json
from main_model_func import *
from func import *
from model_resp import *

data_file = open('data/intents.json').read()
intents = json.loads(data_file)

# train_x, train_y = training_data(intents)
# model_creation(train_x, train_y)


app = Flask(__name__)

global result, voice_query, lastReplyTime, c, userID

c = datetime.now()

##initializing variables
response = ''
customerId = 0
StartTime = 0
user = ['hi']
bot = []
result = []
currentTag = ''


# --- User Interface ---
@app.route('/')
def home():
    global userID
    userID = str(random.randint(1, 198))
    result.append([('', ''), ("Bot", "Hi, I am AssistBot. Your customer service agent. How may I help you?")])
    mike_status = "no"
    resp = "Hi, I am AssistBot. Your customer service agent. How may I help you?"
    bot.append(resp)
    killSession = "no"
    return render_template('index.html', user_input=result, mike_status=mike_status, botResp=resp, userID=userID,
                           killSession=killSession)


@app.route('/process', methods=['POST'])
def process():  # called when user input is given and submit button is pressed
    global userID, user
    print("Process Called")
    query = request.form["user_input"]
    print("user_input : ", query)
    killSession = request.form["killSession"]
    # print("killSession : ", killSession)
    if query == "TimeOut":
        query = ''
        resp = bot_insert_sql()
        bot.append(resp)
    elif query != "TimeOut" and killSession == 'yes':
        killSession = 'no'
        resp = enter_proper_response(query)
        bot.append(resp)
        print("Bot resp2 : ", resp)
    else:
        resp = enter_proper_response(query)
        bot.append(resp)
        print("Bot resp3 : ", resp)
    if currentTag == 'goodbye':
        killSession = 'yes'
    user.append(query)
    result.append([("You", query), ("Bot", resp)])
    mike_status = "yes" if request.form["mic_status"] == "on" else "no"
    # print("mike_status : ", mike_status,request.form["mic_status"])
    userID = request.form["userID"]

    if killSession == "yes":
        pushconv_to_mongodb(userID, result)
    return render_template("index.html", user_input=result, mike_status=mike_status, botResp=resp, userID=userID,
                           killSession=killSession)


def bot_insert_sql():  # inserting user inputs, bot outputs and time into database
    global userID, result
    resp = '''Since there is no response from your end, I will have to end this conversation now. I appreciate your time and patients. Please text or speak to me if you need my help. GoodBye'''
    try:
        pushconv_to_mongodb(userID, result)
        result.clear()
    except:
        print("Some error in the tables, check if table does exist and its inputs")
    return resp


def getResponse(query, ints, intents, user, bot):
    cTag = 'context'
    tag = getTag(query, ints, cTag)
    response = contextResponse(query, tag, intents, cTag, user, bot)
    return response


def enter_proper_response(query):
    global response, bot, user, intents, userID
    try:
        if query != '':
            ints = predict_class(query, words, model)
            # print(bot[-1])
            response = getResponse(query, ints, intents, user, bot)
            return response
        else:
            response = "Please text or say your query. I will be glad to help you."
            # print("Bot_resp1 : ", response)
            return response
    except  Exception as e:
        print('error: ', e)
        response = errorResponse()
        return response


# --- Write session Convo to database
def pushconv_to_mongodb(userID, result):
    global StartTime, customerId, user, bot
    DEFAULT_CONNECTION_URL = "mongodb://localhost:27017/"
    DB_NAME = "Metadata"
    client = pymongo.MongoClient(DEFAULT_CONNECTION_URL)
    dataBase = client[DB_NAME]
    COLLECTION_NAME = "Session_Info"
    collection = dataBase[COLLECTION_NAME]
    record = {'SessionId': userID,
              'StartTime': StartTime,
              'EndTime': datetime.now(),
              'CustomerId': userID,
              'CustomerStatus': 'Active',
              'Convo': result}
    collection.insert_one(record)


if __name__ == "__main__":
    app.run(threaded=True, debug=True, use_reloader=False)