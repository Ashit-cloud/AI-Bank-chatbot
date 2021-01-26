import numpy as np
import pandas as pd 
import re
import nltk
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import pickle
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score


data = pd.read_csv('../data/hotel_reviews10000.csv')


data.drop(columns = ['User_ID', 'Browser_Used', 'Device_Used'], inplace = True)


def encode(x):
    if x == 'not happy':
        return 0
    else:
        return 1
data.Is_Response = data.Is_Response.apply(encode)
# 1 for happy
#0 for unhappy



def cleaning(df):
    all_reviews = list()
    lines = df["Description"].values.tolist()
    for text in lines:
        text = text.lower() # converting the text to lower case
        pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        text = pattern.sub('', text) # removes URL'S
        text = re.sub(r"[,.\"!@#$%^&*(){}?/;`~:<>+=-]", "", text) #removes punctuation
        tokens = nltk.word_tokenize(text) #tokenizing
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        words = [word for word in stripped if word.isalpha()] #filtering only text data
        stop_words = set(stopwords.words("english"))
        stop_words.discard("not") #removing "not" from stopwords as it is sentimental analysis
        PS = PorterStemmer()
        words = [PS.stem(w) for w in words if not w in stop_words] #stemming and removing stopwords
        words = ' '.join(words) #joining strings 
        all_reviews.append(words)
    return all_reviews

reviews = cleaning(data)

data['cleaned_reviews'] = reviews

X = data['cleaned_reviews']
y = data["Is_Response"]
#Splitting Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)


tvec = TfidfVectorizer() #TF-IDF

mul = MultinomialNB()
model = Pipeline([('vectorizer', tvec),('classifier', mul)])
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Accuracy : ", accuracy_score(y_pred, y_test))
print('train score: ', model.score(X_train, y_train))
print('test score: ', model.score(X_test, y_test))
print('pred score: ', model.score(X_test, y_pred))
print("classification: ", classification_report(y_pred, y_test))

filename = '../models/model_hotelreviews.pkl'
pickle.dump(model, open(filename, 'wb'))
 
loaded_model = pickle.load(open(filename, 'rb'))
result = loaded_model.score(X_test, y_test)
print(result)




