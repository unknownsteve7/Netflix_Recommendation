import pandas as pd
import ast
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load and merge datasets
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')
movies = movies.merge(credits, on='title')

# Keep required columns and drop nulls
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

# Helper functions
def convert(text):
    return [i['name'] for i in ast.literal_eval(text)]

def director(text):
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            return i['name']
    return ''

def remove_spaces(lst):
    return [i.replace(" ", "") for i in lst]

# Data Cleaning & Feature Engineering
movies['genres'] = movies['genres'].apply(convert).apply(remove_spaces)
movies['keywords'] = movies['keywords'].apply(convert).apply(remove_spaces)
movies['cast'] = movies['cast'].apply(lambda x: convert(x)[:3]).apply(remove_spaces)
movies['crew'] = movies['crew'].apply(director).apply(lambda x: x.replace(" ", ""))
movies['overview'] = movies['overview'].apply(lambda x: x.split())
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew'].apply(lambda x: [x])

# Final clean dataframe
new_df = movies[['movie_id', 'title', 'tags']].copy()
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())

# Vectorization & Similarity Matrix
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
similarity = cosine_similarity(vectors)

# Genre extraction (for filters in app)
def extract_genres(text):
    return [i['name'] for i in ast.literal_eval(text)]

genre_df = pd.read_csv('tmdb_5000_movies.csv')
genre_df['genres'] = genre_df['genres'].apply(extract_genres)
all_genres = set(g for sublist in genre_df['genres'] for g in sublist)

# TMDB Poster Fetching
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9f83284458280d72500d4f2ebd14f2ef&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

# Final Recommend Function
def recommend(movie, genre_filter=None):
    movie = movie.lower()
    if movie not in new_df['title'].str.lower().values:
        return ["Movie not found in dataset."], [], []

    index = new_df[new_df['title'].str.lower() == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:]

    recommended_movies = []
    recommended_posters = []
    recommended_ratings = []

    for i in movie_list:
        movie_data = movies.iloc[i[0]]
        
        # Genre filter
        if genre_filter:
            original_row = genre_df[genre_df['title'] == movie_data.title]
            if original_row.empty or genre_filter not in original_row['genres'].values[0]:
                continue

        movie_id = movie_data.movie_id
        recommended_movies.append(movie_data.title)
        recommended_posters.append(fetch_poster(movie_id))

        # Fetch rating
        try:
            response = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9f83284458280d72500d4f2ebd14f2ef&language=en-US"
            ).json()
            recommended_ratings.append(response.get('vote_average', 0))
        except:
            recommended_ratings.append("N/A")

        if len(recommended_movies) == 5:
            break

    return recommended_movies, recommended_posters, recommended_ratings
