import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

movies = movies.merge(credits, on='title')

movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

def convert(text):
    return [i['name'] for i in ast.literal_eval(text)]

def director(text):
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            return i['name']
    return ''

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(lambda x: convert(x)[:3])  # Top 3 actors
movies['crew'] = movies['crew'].apply(director)
movies['overview'] = movies['overview'].apply(lambda x: x.split())

def remove_spaces(lst):
    return [i.replace(" ", "") for i in lst]

movies['genres'] = movies['genres'].apply(remove_spaces)
movies['keywords'] = movies['keywords'].apply(remove_spaces)
movies['cast'] = movies['cast'].apply(remove_spaces)
movies['crew'] = movies['crew'].apply(lambda x: x.replace(" ", ""))

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew'].apply(lambda x: [x])

new_df = movies[['movie_id', 'title', 'tags']].copy()

new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

similarity = cosine_similarity(vectors)


import requests

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9f83284458280d72500d4f2ebd14f2ef&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
    return full_path

def recommend(movie):
    movie = movie.lower()
    if movie not in new_df['title'].str.lower().values:
        return ["Movie not found in dataset."], []
    
    index = new_df[new_df['title'].str.lower() == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(new_df.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_posters
def extract_genres(text):
    return [i['name'] for i in ast.literal_eval(text)]

movies['genres'] = movies['genres'].apply(extract_genres)
all_genres = set(g for sublist in movies['genres'] for g in sublist)
