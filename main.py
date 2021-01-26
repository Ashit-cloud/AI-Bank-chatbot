# import nltk
# import pandas as pd
# from datetime import date, datetime
# from nltk.corpus import stopwords
# import json
# import pickle
# import numpy as np
import datetime
# from time import sleep
import pyttsx3 as pp
import speech_recognition as sp
import threading
import pymongo
from tkinter import *
from func import *
# import sys
# import time
from eligibility import *
from model import *


data_file = open('data/intents.json').read()
intents = json.loads(data_file)

data_file1 = open('data/faq_data.json').read()
faqs = json.loads(data_file1)

for intent in faqs['intents']:
  intents['intents'].append(intent)

train_x, train_y = training_data(intents)
model_creation(train_x, train_y)

global lastReplyTime, user
user = []
bot = []
response = ''
customerId = 0
StartTime = 0
c = datetime.now()
lastReplyTime = (c.hour * 60 * 60) + (c.minute * 60) + c.second  # lastreplytime is set on current time
print("No_Conversation: ", lastReplyTime)


def enterquery_in_entrybox(query):
    global EntryBox
    EntryBox.delete(0, END)
    EntryBox.insert(0, query)


def getquery():
    query = EntryBox.get().strip()
    EntryBox.delete(0, END)
    return query


def enterquery(query):
    global ChatLog, user
    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "You: " + query + '\n\n')
    ChatLog.config(state=DISABLED)
    ChatLog.yview(END)
    EntryBox.delete(0, END)
    user.append(query)  # Recording user response


def enterresponse(msg):
    global ChatLog
    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "AssistBot: " + msg + '\n\n')
    ChatLog.config(state=DISABLED)
    ChatLog.yview(END)


def exitpg():  # to exit the program
    global stop_repeatl
    try:
        push_to_mongodb(uniqueSessionId)
        print("Closed")
        stop_repeatl = True
        main.destroy()
    except Exception as e:
        print(e)
        print("Closed")
        stop_repeatl = True
        main.destroy()


def getResponse(query, ints, userID, intents, user):
    tag = getTag(query, ints, userID)
    response = contextResponse(query, tag, userID, intents, user)
    return response


def enter_proper_response(query):
    global response, bot, user, intents
    userID = '123'
    ints = predict_class(query, model)
    if ints[0]['intent'] == "goodbye":  # or "anything_else_no"
        tag = "goodbye"
        response = contextResponse(query, tag, userID, intents, user)
        enterresponse(response)
        speak(response)
        bot.append(response)  # Recording bot response
        exitpg()
    else:
        response = getResponse(query, ints, userID, intents, user)
        if response == "calc_eli":
            response = eligibility_response(user)
        else:
            response = response
        enterresponse(response)
        speak(response)
        bot.append(response)  # Recording bot response


def chatbot_response():
    query = getquery()
    enterquery(query)
    global lastReplyTime

    def replytime():
        global lastReplyTime, user, bot
        # Session Recording
        # Resetting lastReplyTime
        c = datetime.now()
        current_time = (c.hour * 60 * 60) + (c.minute * 60) + c.second
        lastReplyTime = current_time
        print("chat_response: ", lastReplyTime)
        print(user)
        print(bot)
        return lastReplyTime

    if query != '':
        lastReplyTime = replytime()
        enter_proper_response(query)
    else:
        lastReplyTime = replytime()
        emptymsg = "Please text or say your query. I'll be glad to help you."
        enterresponse(emptymsg)
        speak(emptymsg)


def push_to_mongodb(uniqueSessionId):
    global StartTime, customerId, user, bot
    DEFAULT_CONNECTION_URL = "mongodb://localhost:27017/"
    DB_NAME = "Metadata"
    client = pymongo.MongoClient(DEFAULT_CONNECTION_URL)
    dataBase = client[DB_NAME]
    COLLECTION_NAME = "Session_Info"
    collection = dataBase[COLLECTION_NAME]
    record = {'SessionId': uniqueSessionId,
              'StartTime': StartTime,
              'EndTime': datetime.now(),
              'CustomerId': customerId,
              'CustomerStatus': 'Active',
              'DataFileName': 'abc.txt'}
    collection.insert_one(record)
    print("Record 1", record)
    COLLECTION_NAME = "Session_Data"
    collection = dataBase[COLLECTION_NAME]
    record2 = {'SessionId': uniqueSessionId,
               'CustomerId': customerId,
               'UserConv': user,
               'BotResp': bot,
               }
    collection.insert_one(record2)
    print("Record 2", record2)


def ideal(uniqueSessionId):
    global lastReplyTime, customerId, user, bot, StartTime, stop_repeatl
    customerId = random.random()
    c = datetime.now()
    StartTime = c
    print("uniqueSessionId : ", uniqueSessionId)
    while True:
        c = datetime.now()
        current_time = (c.hour * 60 * 60) + (c.minute * 60) + c.second
        print("While lastReplyTime: ", int(lastReplyTime), " ", current_time)
        sleep(1)
        if (lastReplyTime + 30) == current_time:
            print("ideal")
            endmsg = '''Since there is no response from your end, I will have to end this conversation now.
                      I appreciate your time and patients. Please text or speak to me if you need my help. Goodbye'''
            enterresponse(endmsg)
            speak(endmsg)
        if (lastReplyTime + 50) == current_time:
            exitpg()


def session():
    global uniqueSessionId
    c = datetime.now()
    current_time = (c.hour * 60 * 60) + (c.minute * 60) + c.second + c.microsecond
    uniqueSessionId = current_time
    t1 = threading.Thread(target=ideal, args=(uniqueSessionId,))
    t1.daemon = True
    t1.start()


session()  # Initializing session

# ---------------------------------- For Voice -------------------------------- ##
# global engine
engine = pp.init()

voices = engine.getProperty('voices')  # get all voices
engine.setProperty('voice', voices[1].id)


def speak(word):
    global sr
    store = sr.energy_threshold
    sr.energy_threshold = 9001  # note I'm not sure what the maximum value is
    engine.say(word)
    engine.runAndWait()
    sr.energy_threshold = store


def speech_query():
    global sr
    sr = sp.Recognizer()
    sr.pause_threshold = 1
    with sp.Microphone() as m:
        sr.adjust_for_ambient_noise(m, duration=0.2)
        try:
            audio = sr.listen(m)
            query = sr.recognize_google(audio, language="eng-in")
            enterquery_in_entrybox(query)
            # enterquery()
            chatbot_response()
        except Exception as e:
            print(e)
            print("not recognize")


# -----------------------------GUI------------------------------------- #

main = Tk()
main.geometry("350x600")
main.resizable(width=True, height=True)
main.title("AssistBot")


img = PhotoImage(file="images.png")
photoL = Label(main, image=img)
photoL.pack(pady=5)

frame = Frame(main)
frame.pack()

# Creating a message box in frame
ChatLog = Text(frame, bd=0, bg="white", height="13", width="35", font=("Bahnschrift", 15), wrap=WORD)
ChatLog.pack(side=LEFT, fill=BOTH, pady=10)
ChatLog.config(state=DISABLED)

# Creating scrollbar in frame
sc = Scrollbar(frame, command=ChatLog.yview)
ChatLog['yscrollcommand'] = sc.set
sc.pack(side=RIGHT, fill=Y)

# Creating text field
EntryBox = Entry(main, width="23", font=("Bahnschrift", 20))
EntryBox.pack(pady=10)

# Creating button
btn = Button(main, text="Send", width="30", font=("Bahnschrift", 15), command=chatbot_response)
btn.pack()


def enter_function(event):
    btn.invoke()


# going to bind main window with enter key
main.bind('<Return>', enter_function)


def intro():
    print('intro thread running')
    intromsg = "Hi, I am AssistBot. Your customer service agent. How may I help you?"
    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "AssistBot: " + intromsg + '\n\n')
    ChatLog.config(state=DISABLED)
    speak(intromsg)


global stop_repeatl
stop_repeatl = False


def repeatl():
    global stop_repeatl
    while stop_repeatl == False:
        speech_query()
        print('speech thread running')
    else:
        print("threads killed")


r = threading.Thread(target = repeatl)
r.daemon = True
r.start()


n = threading.Thread(target=intro)
n.daemon = True
n.start()

main.mainloop()

