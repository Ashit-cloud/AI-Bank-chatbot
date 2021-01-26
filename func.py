import numpy as np
import json
from model_resp import *
from after_auth_reply import *
from sent_func import *
from main_model_func import *
from smalltalks import *
from bot_profile import *
from faq import *

intents = json.loads(open('data/intents.json').read())

story_conv_file = open('data/story_conv.json').read()
story_conv = json.loads(story_conv_file)

yes = ["yes", "ok", "yep", "okay", "fine", "cool", "sure", "all right", "right", "yes please", "go ahead", "positive",
       "ok man", "of course", "correct", "yes of course"]
no = ["no", "nope", "never", "na", "naa", "I do not", "you cannot", "No please", "stop", "no man", "wrong",
      "of course not", "I don't think so", "not ok", "not okay", "obviously no"]

contextForAuth = ["charges", "top_up", "foreclose"]

topics = {
    "charges": "discussing about the late charge",
    "authenticate": "the authentication",
    "auth": "the authentication",
    "anything_else": "the conversation.",
    "top_up": "checking on top-up loan eligibility",
    "foreclose": "checking on foreclosure amount",
    "application_status": "checking on your application status",
    "personal_loan": "checking your loan eligibility",
    "personal_loan_apply": "checking your loan eligibility",
    "ploan_apply": "applying for personal loan",
    "ploan_apply_contact": "applying for personal loan"
}

contextToCheckPath = ''

endTag = ['goodbye', 'anything_else_no']

contextLateAct = []
context = {}

all_conv_tags = []
recheck_tag = []

next_context = []

recheck_tag_yes = ["personal_loan_apply_yes", "ploan_apply_contact_yes", "auth_yes", "charges_yes",
                   "top_up_yes", "foreclose_yes", "application_status_yes"]
recheck_tag_no = ["personal_loan_apply_no", "ploan_apply_contact_no", "auth_no", "charges_no",
                  "top_up_no", "foreclose_no", "application_status_no"]


def reconfirm(query):
    response = "You have mentioned {}. Is this information correct, please confirm in yes or no.".format(query)
    return response


def getTag(query, ints, cTag):
    global all_conv_tags, context
    if bool(context):
        if query in yes:
            con = context[cTag][0]
            tag = con + "_yes"
        elif query in no:
            con = context[cTag][0]
            tag = con + "_no"
        else:
            tag = ints[0]['intent']
        print('getTag1: ', tag)
    else:
        tag = ints[0]['intent']
    print('getTag1: ', tag)
    # ------------------------------
    if tag in endTag:
        tag = 'goodbye'
    elif tag == 'user_name':
        if "my name is" in query:
            tag = tag
        else:
            tag = 'defaultfallback'
    # ------------------------------
    if tag in recheck_tag_yes:
        tag = recheck_tag[-1]
    elif tag in recheck_tag_no:
        tag = all_conv_tags[-2]
    elif tag == 'context_change_yes':
        tag = 'start_again'
    elif tag == 'context_change_no':
        tag = all_conv_tags[-1]
        context[cTag] = ['auth']
    else:
        tag = tag

    print('getTag2: ', tag)
    all_conv_tags.append(tag)
    print("all_conv_tags: ", all_conv_tags)
    print('recheck_tag: ', recheck_tag)
    return tag


count = 1

def contextChangeAlertMsg(bot, cTag):
    global count, topics
    print('count: ', count)
    if count == 1:
        msg1 = "Invalid answer. Please try again. "
        msg2 = bot[-1]
        response = msg1 + msg2
        next_context.append(all_conv_tags[-1])
        all_conv_tags.pop()
        bot.pop(-1)
        count += 1
        return response
    elif count == 2:
        topic = context[cTag][0]
        contextNext = topics[topic]
        response = "Are you sure you want to discontinue with {}. (Please answer in yes or no.)".format(contextNext)
        next_context.append(all_conv_tags[-1])
        all_conv_tags.pop()
        count = 1
        context[cTag] = ['context_change']
        return response



def contextResponseGen(query, tag, intents_json, cTag):
    global count, contextToCheckPath, contextLateAct
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            if "recheck" in i and (bool(context) == True):
                count = 1
                if query == 'no':
                    response = random.choice(i['responses'])
                    recheck_tag.append(tag)
                    print('context1: ', context)
                    return response
                elif query in yes:
                    if 'context_set' in i:
                        context[cTag] = i['context_set']
                        contextToCheckPath = i['context_set'][0]
                        response = random.choice(i['responses'])
                        print('context2.1: ', context)
                        return response
                    elif 'context_filter' not in i or (
                            cTag in context and 'context_filter' in i and i['context_filter'] == context[cTag]):
                        response = random.choice(i['responses'])
                        print('context2.2: ', context)
                        return response
                else:
                    response = reconfirm(query)
                    recheck_tag.append(tag)
                    print('context3: ', context)
                    return response
            elif 'context_set' in i:
                count = 1
                context[cTag] = i['context_set']
                contextToCheckPath = i['context_set'][0]
                if context[cTag][0] in contextForAuth:
                    contextLateAct.append(context[cTag][0])
                    print('contextLateAct', contextLateAct)
                response = random.choice(i['responses'])
                print('context4: ', context)
                # print(response)
                return response
            elif 'context_filter' not in i or \
                    (cTag in context and 'context_filter' in i and i['context_filter'] == context[cTag]):
                count = 1
                response = random.choice(i['responses'])
                print('context5: ', context)
                # print(response)
                return response


def predict_Tag(tag):
    global contextToCheckPath
    print('contextToCheckPath: ', contextToCheckPath)
    if contextToCheckPath in story_conv:
        if all_conv_tags[-2] in story_conv[contextToCheckPath]:
            predTag = story_conv[contextToCheckPath][all_conv_tags[-2]]
            return predTag
        else:
            return tag
    else:
        return tag




def contextResponseGen2(query, tag, intents_json, cTag, user, bot):
    global senti_count
    if bool(context):
        if context[cTag][0] != 'satisfaction':
            if len(all_conv_tags) > 2:
                predTag = predict_Tag(tag)
                print('predTag: ', predTag)
                print('all_conv_tags[-2]: ', all_conv_tags[-2])
                if 'yes or no' in bot[-1]:
                    if query in yes or query in no:
                        response = contextResponseGen(query, tag, intents_json, cTag)
                        return response
                    else:
                        response = contextChangeAlertMsg(bot, cTag)
                        return response
                elif tag == predTag or tag == all_conv_tags[-2] or tag == all_conv_tags[-3]:
                    response = contextResponseGen(query, tag, intents_json, cTag)
                    print('context6: ', context)
                    # print(response)
                    return response
                elif tag == 'start_again':
                    response = contextResponseGen(query, tag, intents_json, cTag)
                    print('context6.1: ', context)
                    # print(response)
                    return response
                else:
                    response = contextChangeAlertMsg(bot, cTag)
                    print('context7: ', context)
                    # print(response)
                    return response
            else:
                response = contextResponseGen(query, tag, intents_json, cTag)
                print('context8: ', context)
                # print(response)
                return response
        else:
            response = sentiment_check(query, user)
            print('context9: ', context)
            # print(response)
            if "Thanks for your feedback" in response:
                context[cTag] = ['recommend']
                return response
            else:
                if 'Just before you leave' in response:
                    context[cTag] = ['upselling']
                    return response
                else:
                    return response
    else:
        response = contextResponseGen(query, tag, intents_json, cTag)
        print('context10: ', context)
        # print(response)
        return response


def topicResponse(topic, cTag, user):
    if topic == 'charges':
        response = lateChargeCheck(user)
        context[cTag] = ['satisfaction']
        return response
    elif topic == 'top_up':
        response = topUpCheck(user)
        if 'Congratulations!!' in response:
            context[cTag] = ['topup_apply']
            return response
        else:
            context[cTag] = ['upselling']
            return response
    elif topic == "foreclose":
        response = forecloseAmtCheck(user)
        context[cTag] = ['fore_close']
        return response


def auth_done(bot):
    result = ''
    for x in bot:
        if "Thank you for the authentication. " in x:
            result = 'Yes'

    return result


def yesORno_check(query, response, bot, cTag):
    if 'yes or no' in bot[-1]:
        if query in yes or query in no:
            return response
        else:
            response = contextChangeAlertMsg(bot, cTag)
            return response
    else:
        return response


def contextResponse1(query, tag, intents_json, cTag, user, bot):
    global topic
    topic = ''
    response = contextResponseGen2(query, tag, intents_json, cTag, user, bot)
    # print('CRG2: ', response)
    response = responseBased(response, user, query)
    # print('RB: ', response)
    if len(contextLateAct) > 0:
        topic = contextLateAct[-1]  # check what was the context topic that should be continued after auth
        print('topic: ', topic)
    auth_pos_resp = "Thank you for the authentication. "  # if the response from auth_result()
    if response == auth_pos_resp:
        resp = topicResponse(topic, cTag, user)
        response = auth_pos_resp + resp
        return response
    elif response == "not_auth":
        neg_msg = "Sorry, I could not find you in my database. Would you like to try again."
        response = neg_msg
        context[cTag] = ['authagain']
        return response
    elif response == "not_auth1":
        neg_msg = "Sorry, I still could not find you in my database. " \
                  "Please check your credentials and try again after sometime or call on 1800 123 456. " \
                  "It was nice chatting with you. Goodbye."
        if topic in contextForAuth:
            response = neg_msg
            return response
    elif bool(context):
        if context[cTag][0] in contextForAuth:
            print(user)
            result = auth_done(bot)
            if result == 'Yes':
                response = topicResponse(topic, cTag, user)
                return response
            else:
                return response
        else:
            print('context11: ', context)
            # print(response)
            return response
    elif 'Is there anything else I may help you with.' in response:
        context[cTag] = ['anything_else']
    elif 'I see that you are eligible for' in response:
        context[cTag] = ['recommend']
    elif 'I regret to inform you that' in response:
        context[cTag] = ['upselling']
    elif "Thank you for your decision" in response:
        context[cTag] = ['upselling']
    else:
        print('context12: ', context)
        # print(response)
        return response

def contextResponse(query, tag, intents_json, cTag, user, bot):
    global list_of_response
    list_of_intents = intents_json['intents']
    response = contextResponse1(query, tag, intents_json, cTag, user, bot)
    for i in list_of_intents:
        if i['tag'] == 'defaultfallback':
            list_of_response = i['responses']
    if response not in list_of_response:
        return response
    else:
        response = profile_response(query)
        if not response:
            response = faq_response(query)
            if not response:
                response = smalltalks_response(query)
                if not response:
                    for i in list_of_intents:
                        if i['tag'] == tag:
                            response = random.choice(i['responses'])
                            return response
                return response
            else:
                return response
        else:
            return response
