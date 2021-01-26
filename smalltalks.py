import yaml
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from difflib import SequenceMatcher

with open(r'data/smalltalks.yaml') as file:
    smalltalks_list = yaml.load(file, Loader=yaml.FullLoader)

lemmatizer = WordNetLemmatizer()


def smalltalks_clean_up(sentence):
    tokenizer = RegexpTokenizer(r'\w+')
    sentence_words = tokenizer.tokenize(str(sentence))
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


def smalltalks_response(query):
    global match_perc2
    list1 = smalltalks_clean_up(query)
    scr = 0
    quest = ''
    result = []

    for item in smalltalks_list['conversations']:
        tk_item = smalltalks_clean_up(item[0])
        list2 = tk_item
        # Percentage similarity of lists
        # using "|" operator + "&" operator + set()
        res = len(set(list1) & set(list2)) / float(len(set(list1) | set(list2))) * 100
        if res > scr:
            scr = res
            quest = item[0]
            response = item[1]
            match_perc2 = SequenceMatcher(None, query, quest).ratio()
            if match_perc2 > 0.80:
                result.append(response)
                print(match_perc2)

    if bool(result):
        return result[-1]
    else:
        return None

# query = "what is AI"
# res = smalltalks_response(query)
# print(res)

