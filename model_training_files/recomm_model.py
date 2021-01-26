import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import pickle


df_matrix = pd.read_csv('../data/Personal_recomm.csv')

# df_bankingProducts_matrix = csr_matrix(df_matrix)

model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
model_knn.fit(df_matrix)

filename = '../models/recommend_bankproducts.sav'
pickle.dump(model_knn, open(filename, 'wb'))

# load the model from disk
loaded_model = pickle.load(open(filename, 'rb'))

customerId = 1003805
indexValue = df_matrix.index[df_matrix['Customer_id'] == customerId]
query_index = indexValue[0]
distances, indices = loaded_model.kneighbors(df_matrix.loc[query_index,:].values.reshape(1, -1), n_neighbors = 11)
top_10_match_bestscore = []
for x in indices.flatten():
  if x != customerId:
    b = df_matrix.iloc[x]
    c = b.sort_values(ascending=False)
    # print(c.index[1], c[1])
    top_10_match_bestscore.append([c.index[1], c[1]])

# to sort the max value from top 10
df_tosort = pd.DataFrame(top_10_match_bestscore, columns=['Product', 'Score'])
sorted_df = df_tosort.sort_values(by=['Score'], ascending=False)
result = sorted_df.Product[0]
print(result)