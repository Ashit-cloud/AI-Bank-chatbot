import nltk
import pickle
import random
import numpy as np
import json
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
from keras.optimizers import RMSprop
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


lemmatizer = WordNetLemmatizer()


def word_cleaning(intents_json):
    words = []
    classes = []
    documents = []
    ignore_words = ['?', '!']
    for intent in intents_json['intents']:
        for pattern in intent['patterns']:
            # take each word and tokenize it
            text_token = nltk.word_tokenize(pattern)
            token_without_sw = [word for word in text_token if word not in stopwords.words()]
            words.extend(token_without_sw)
            # adding documents
            documents.append((token_without_sw, intent['tag']))
            # adding classes to our class list
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
    words = sorted(list(set(words)))
    classes = sorted(list(set(classes)))
    print(len(documents), "documents")
    print(len(classes), "classes", classes)
    print(len(words), "unique lemmatized words", words)
    pickle.dump(words, open('./api/model/words.pkl', 'wb'))
    pickle.dump(classes, open('./api/model/classes.pkl', 'wb'))
    return documents, classes, words


def training_data(intents_json):
    documents, classes, words = word_cleaning(intents_json)
    # initializing training data, Creating X and y data (bag and output row)
    training = []
    output_empty = [0] * len(classes)
    for doc in documents:
        bag = []  # initializing bag of words
        pattern_words = doc[0]  # list of tokenized words for the pattern
        # lemmatize each word - create base word, in attempt to represent related words
        pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
        for w in words:
            # create our bag of words array with 1, if word match found in current pattern
            bag.append(1) if w in pattern_words else bag.append(0)

        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1
        training.append([bag, output_row])

    # shuffle our features and turn into np.array
    random.shuffle(training)
    training = np.array(training)
    # create train and test lists. X - patterns, Y - intents
    train_x = list(training[:, 0])
    train_y = list(training[:, 1])
    print("Training data created")
    return train_x, train_y


def model_creation(train_x, train_y):
    # Create model - 3 layers.
    # First layer 128 neurons, second layer 64 neurons and 3rd output layer contains number of neurons
    # equal to number of intents to predict output intent with softmax
    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(train_y[0]), activation='softmax'))
    # Compile model. Stochastic gradient descent with Nesterov accelerated gradient gives good results for this model
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    rms = RMSprop(learning_rate=0.001, rho=0.9, momentum=0.9, epsilon=1e-06, centered=False, name="RMSprop")
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    # fitting and saving the model
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
    model.save('./models/chatbot_model.h5', hist)
    print("model created")


# data_file1 = open('../data/botprofile_data.json').read()
# botprofile = json.loads(data_file1)
#
# train_x, train_y = training_data(botprofile)
# model_creation(train_x, train_y)