import yaml
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from difflib import SequenceMatcher

with open(r'data/botprofile.yml') as file:
    botprofile_list = yaml.load(file, Loader=yaml.FullLoader)

lemmatizer = WordNetLemmatizer()


def profile_clean_up(sentence):
    tokenizer = RegexpTokenizer(r'\w+')
    sentence_words = tokenizer.tokenize(str(sentence))
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def profile_response(query):
    global match_perc
    list1 = profile_clean_up(query)
    scr = 0
    response = ''
    result = []

    for item in botprofile_list['conversations']:
        tk_item = profile_clean_up(item[0])
        list2 = tk_item
        # Percentage similarity of lists
        # using "|" operator + "&" operator + set()
        res = len(set(list1) & set(list2)) / float(len(set(list1) | set(list2))) * 100
        if res > scr:
            scr = res
            quest = item[0]
            response = item[1]
            match_perc = SequenceMatcher(None, query, quest).ratio()
            if match_perc > 0.70:
                result.append(response)
                print(match_perc)

    if bool(result):
        return result[-1]
    else:
        return None


# query = "Who ar you"
# res = profile_response(query)
# print(res)
