import pandas as pd
from sklearn.neighbors import NearestNeighbors


def recomm_product(customer_id):
    df_matrix = pd.read_csv('./data/Personal_recomm.csv')
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(df_matrix)
    # print(df_matrix.head())
    indexValue = df_matrix.index[df_matrix['Customer_id'] == int(customer_id)]
    # print('indexValue: ', indexValue)
    query_index = indexValue[0]
    # print('query_index: ', query_index)
    distances, indices = model_knn.kneighbors(df_matrix.loc[query_index, :].values.reshape(1, -1), n_neighbors=11)
    # print('indices: ',indices)
    top_10_match_bestscore = []
    for x in indices.flatten():
        if x != customer_id:
            b = df_matrix.iloc[x]
            c = b.sort_values(ascending=False)
            # print(c.index[1], c[1])
            top_10_match_bestscore.append([c.index[1], c[1]])
    # to sort the max value from top 10
    df_tosort = pd.DataFrame(top_10_match_bestscore, columns=['Product', 'Score'])
    sorted_df = df_tosort.sort_values(by=['Score'], ascending=False)
    # print('sorted_df: ', sorted_df.head(15))
    result = sorted_df.Product[0]
    print('rec_result: ', result)
    return result


recommend_dict = {
    "pl_score": "top-up loan",
    "hl_score": "home loan",
    "cl_score": "consumer loan",
    "twl_score": "two-wheeler loan",
    "cc_score": "platinum credit card"
}

def recommResponse(customer_id):
    global recommend_dict
    res = recomm_product(customer_id)
    result  = recommend_dict[res]
    response = "Now, based on your prior banking history, I see that you are eligible for a {}. " \
               "Would you like to apply. (please answer in Yes or No.)".format(result)
    return response


def recommResponse1():
    response = "Thank you for your decision, I have forwarded your details to the concern department. " \
              "You will get a call from one of the officers to take this deal further.  Just before you leave " \
               "I would like to inform you that our bank offers you a Accidental Policy worth 5 lacs. " \
               "Would you like to know more about the offer"
    return response


# customerId = 1003805
# result = recomm_product(customerId)
# print(result)

