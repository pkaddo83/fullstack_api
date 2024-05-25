# use the panel datas module
import pandas as pd

# use the python http module
import requests

# use the progress bar display module
from tqdm import tqdm

# use the time module
import time

# function to take in the imdbid and returns the corresponding url
def add_url(row):
    return f"http://www.imdb.com/title/tt{row}/"

# function to add ratings data to the original dataset passed in
def add_rating(df):
    # read the ratings data from csv file into a dataframe
    ratings_df = pd.read_csv("data/ratings.csv")

    # convert the movieId column in the dataframe to a string type
    ratings_df["movieId"] = ratings_df["movieId"].astype(str)

    # group the ratings_df dataframe by the movieId column and calculate the count and average (assign then to vars)
    agg_df = ratings_df.groupby("movieId").agg(
        rating_count = ("rating", "count"),
        rating_avg = ("rating", "mean")
    ).reset_index()

    # attach the ratings statistics to the original dataframe passed in based on the movieId as key
    rating_added_df = df.merge(agg_df, on="movieId")

    return rating_added_df

# function to add links to from themoviedb.org site to our original dataframe passed in
def add_poster(df):
    # initialise enumerable for-loop to iterate over the dataframe rows, and also specifying the total as the number of rows
    for i, row in tqdm(df.iterrows(), total=df.shape[0]):
        # in each row, get the value in the tmbdId column
        tmdb_id = row["tmdbId"]
        # use this id to retrieve the appropriate url
        tmdb_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key=[b9a0e43e129dea3551ab7d9ade3aac9c]"
        # submit the url to the request module's get function and assign the response to the result variable
        result = requests.get(tmdb_url)

        # try/catch
        try:
            # specify the cell in the dataframe with the .at attribute and assign poster_path part the json response
            df.at[i, "poster_path"] = "http://image.tmdb.org/t/p/original" + result.json()["poster_path"]

            # sleep for 0.1 seconds
            time.sleep(0.1)
        except(TypeError, KeyError) as e:
            # in the event of a type of key error just use the image url for Toy Story
            df.at[i, "poster_path"] = "https://image.tmdb.org/t/p/original/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg"
            
    return df

# entry point for this script
if __name__ == "__main__":
    # read the movies.csv file into a dataframe
    movies_df = pd.read_csv("data/movies.csv")

    # convert the movieId column to a string and reassign it back to the original column
    movies_df["movieId"] = movies_df["movieId"].astype(str)

    # read the links.csv file into a dataframe
    links_df = pd.read_csv("data/links.csv", dtype=str)

    # left join the movies and links dataframes on the movieId column
    merged_df = movies_df.merge(links_df, on="movieId", how="left")
    
    # create a new url column in merged dataframe and assign to it the output of the imdbId column pass ti the add_url func
    merged_df["url"] = merged_df["imdbId"].apply(lambda x: add_url(x))

    # pass in the merged dataframe and have the ratings count and mean added
    result_df = add_rating(merged_df)

    # add a new column called poster_path
    result_df["poster_path"] = "None"

    # pass the result_df dataframe to the add_poster func and pass the result back to result_df
    result_df = add_poster(result_df)

    # write the dataframe to a csv file
    result_df.to_csv("data/movies_final.csv", index = None)