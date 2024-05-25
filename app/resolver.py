import pandas as pd

item_fname = "data/movies_final.csv"

def random_items():
    # reads the csv file we specified above into a dataframe
    movies_df = pd.read_csv(item_fname)

    # to fill the blanks
    movies_df = movies_df.fillna("")

    # takes a sample of 10 from the movies_df and convert each row to a dictionary of the header and values
    result_items = movies_df.sample(n = 10).to_dict("records")

    return result_items

def random_genres_items(genre):
    movies_df = pd.read_csv(item_fname)

    # filter results by the genre column using the apply function and lambda expression
    genre_df = movies_df[movies_df["genres"].apply(lambda x: genre in x.lower())]
    genre_df = genre_df.fillna("") # to fill the blanks
    result_items = genre_df.sample(n = 10).to_dict("records")
    return result_items