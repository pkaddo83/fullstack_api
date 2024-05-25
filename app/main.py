# We pip installed "uvicorn[standard]" in order to run a webserver

# use the typing module - I'm not sure what it does
from typing import List, Optional
# use the fastapi module 
from fastapi import FastAPI, Query
from recommender import item_based_recommendation, user_based_recommendation
# use our resolver file that we created
from resolver import random_items, random_genres_items
# from fastapi.middleware.cors import CORSMiddleware

# instantiate a FastAPI instance
app = FastAPI()

# define an async func called root that's annotated with a FastAPI get() function value parameter and returns a json string 
@app.get("/")
async def root():
    return {"message": "Hello World"}

# define an async func called all_movies that's called when the FastAPI route "/all/" is called
@app.get("/all/")
async def all_movies():
    # call the function that will select a random 10 rows and return a dictionary of columns with values for those rows
    result = random_items()
    # return a json type string with "result" as the key and the dictionary as the "value"
    return {"result": result}

# see how a string type is being specified here for the genre parameter
@app.get("/genres/{genre}")
async def genre_movies(genre: str):
    result = random_genres_items(genre)
    return {"result": result}

# this function is designed to hand this type of call, "http://localhost:8000/user-based/?params=2571:5&params=6365:5"
@app.get("/user-based/")
async def user_based(params: Optional[List[str]] = Query(None)):
    input_ratings_dict = dict((int(x.split(":")[0]), float(x.split(":")[1])) for x in params)
    result = user_based_recommendation(input_ratings_dict)
    return {"result": result}

@app.get("/item-based/{item_id}")
async def item_based(item_id: str):
    result = item_based_recommendation(item_id)
    #return {"message": f"item based: {item_id}"}
    return {"result": result}