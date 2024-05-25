import pandas as pd
import numpy as np
from scipy.sparse import coo_matrix
from implicit.als import AlternatingLeastSquares
import pickle

saved_model_fname = "model/finalized_model.sav"
data_fname = "data/ratings.csv"
item_fname = "data/movies_final.csv"
weight = 10

def model_train():
    ratings_df = pd.read_csv(data_fname)
    ratings_df["userId"] = ratings_df["userId"].astype("category")
    ratings_df["movieId"] = ratings_df["movieId"].astype("category")

    # a coordinate matrix specifying rows = movies, columns = users and at that coordinate is the rating
    rating_matrix = coo_matrix(
        (
            ratings_df["rating"].astype(np.float32), (
                ratings_df["movieId"].cat.codes.copy(),
                ratings_df["userId"].cat.codes.copy(),
            ),
        )
    )

    # factors = number of standards or tastes taken into account by reviewers. Disadvantage is overfitting
    # regularization = used to prevent overfitting but can cause decreases in accuracy if too large a value
    # dtype = specifies the data format of the rating score
    # iterations = number of times to update the parameters through learning (causes overfitting if large)
    als_model = AlternatingLeastSquares(factors = 50, regularization = 0.01, dtype = np.float64, iterations = 50)

    als_model.fit(weight * rating_matrix)
    pickle.dump(als_model, open(saved_model_fname, "wb"))
    return als_model

def calculate_item_based(item_id, items):
    # loaded_model = pickle.load(open(saved_model_fname, "rb"))
    loaded_model = pd.read_pickle(saved_model_fname)
    recs = loaded_model.similar_item(itemid = int(item_id), N = 11)
    return [str(items[r]) for r in recs[0]]

def item_based_recommendation(item_id):
    ratings_df = pd.read_csv(data_fname)
    ratings_df["userId"] = ratings_df["userId"].astype("category")
    ratings_df["movieId"] = ratings_df["movieId"].astype("category")
    movies_df = pd.read_csv(item_fname)
    items = dict(enumerate(ratings_df["movieId"].cat.categories))

    try:
        parsed_id = ratings_df["movieId"].cat.categories.get_loc(int(item_id))
        result = calculate_item_based(parsed_id, items)
    except KeyError as e:
        result = []
        result = [int(x) for x in result if x != item_id]
        result_items = movies_df[movies_df["movieId"].isin(result)].to_dict("records")
        return result_items

def calculate_user_based(user_items, items):
    loaded_model = pickle.load(open(saved_model_fname, "rb"))
    recs = loaded_model.recommend(userid = 0, user_items = user_items, recalculate_user = True, N = 10)
    return [str(items[r]) for r in recs[0]]

# takes input_ratings_dict = dict{2572:5, 6365:5} (2 movie categories rated 5) and dict of categories {0:1,1:2,2:3,3:4...}
def build_matrix_input(input_rating_dict, items):
    # opening the .sav file in readonly binary format by default to be deserialised into a python object
    # pickle.load(open(saved_model_fname, "rb"))
    model = pd.read_pickle(saved_model_fname) 
    # swap the key, value to become value, key (okay given the movieId values are distinct)
    item_ids = {r: i for i, r in items.items()}
    # loop through the keys (movieIds) in the reversed dict and pick out the movieIds (categories) requested as parameters
    mapped_idx = [item_ids[s] for s in input_rating_dict.keys() if s in item_ids]
    # list comprehension returning movie ratings * weight
    data = [weight * float(x) for x in input_rating_dict.values()]
    rows = [0 for _ in mapped_idx]
    shape = (1, model.item_factors.shape[0])
    return coo_matrix((data, (rows, mapped_idx)), shape=shape).tocsr()

def user_based_recommendation(input_ratings):
    # read in the ratings data: userId,movieId,rating,timestamp
    ratings_df = pd.read_csv(data_fname)
    # convert the column types to type category
    ratings_df["userId"] = ratings_df["userId"].astype("category")
    ratings_df["movieId"] = ratings_df["movieId"].astype("category")
    # read in the movies_final data: movieId,title,genres,imdbId,tmdbId,url,rating_count,rating_avg,poster_path
    movies_df = pd.read_csv(item_fname)
    # get categories, enumerate over to create an array with 0-based index then turn into dictionary with index as keys
    items = dict(enumerate(ratings_df["movieId"].cat.categories))
    # takes input_ratings = dict{2572:5, 6365:5} (2 movie categories rated 5) and dict of categories {0:1,1:2,2:3,3:4...}
    input_matrix = build_matrix_input(input_ratings, items)
    result = calculate_user_based(input_matrix, items)
    result = [int(x) for x in result]
    result_items = movies_df[movies_df["movieId"].isin(result)].to_dict("records")
    return result_items

if __name__ == "__main__":
    model = model_train()
    # model = item_based_recommendation(0)