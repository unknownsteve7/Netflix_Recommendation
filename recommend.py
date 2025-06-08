import pandas as pd
import ast
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Step 1: Load & merge TMDB datasets
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')
movies = movies.merge(credits, on='title')

# Step 2: Keep essential columns & drop missing data
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

# Step 3: Helper functions to clean & parse JSON-like columns

def convert(text):
    """Convert JSON string to list of names."""
    try:
        return [i['name'] for i in ast.literal_eval(text)]
    except:
        return []

def director(text):
    """Get director name from crew JSON string."""
    try:
        for i in ast.literal_eval(text):
            if i['job'] == 'Director':
                return i['name']
    except:
        return ''
    return ''

def remove_spaces(lst):
    """Remove spaces from each string in a list for consistency."""
    return [i.replace(" ", "") for i in lst]

# Step 4: Data Cleaning & Feature Engineering
movies['genres'] = movies['genres'].apply(convert).apply(remove_spaces)
movies['keywords'] = movies['keywords'].apply(convert).apply(remove_spaces)
movies['cast'] = movies['cast'].apply(lambda x: convert(x)[:3]).apply(remove_spaces)
movies['crew'] = movies['crew'].apply(director).apply(lambda x: x.replace(" ", ""))
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Combine all features into one 'tags' column (list of words)
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew'].apply(lambda x: [x])

# Step 5: Prepare final dataframe for vectorization
new_df = movies[['movie_id', 'title', 'tags']].copy()
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())

# Step 6: Vectorize tags & compute similarity matrix
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
similarity = cosine_similarity(vectors)

# Step 7: Extract all genres for potential filtering
genre_df = pd.read_csv('tmdb_5000_movies.csv')
genre_df['genres'] = genre_df['genres'].apply(convert)
all_genres = set(g for sublist in genre_df['genres'] for g in sublist)

# Step 8: Function to fetch poster from TMDB API by movie_id
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9f83284458280d72500d4f2ebd14f2ef&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

# Step 9: Recommendation function with optional genre filtering
def recommend(movie, genre_filter=None):
    movie = movie.lower()
    if movie not in new_df['title'].str.lower().values:
        return ["Movie not found in dataset."], [], []

    index = new_df[new_df['title'].str.lower() == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:]  # skip itself

    recommended_movies = []
    recommended_posters = []
    recommended_ratings = []

    for i in movie_list:
        movie_data = movies.iloc[i[0]]

        # If genre filter applied, skip movies not matching the genre
        if genre_filter:
            original_row = genre_df[genre_df['title'] == movie_data.title]
            if original_row.empty or genre_filter not in original_row['genres'].values[0]:
                continue

        movie_id = movie_data.movie_id
        recommended_movies.append(movie_data.title)
        recommended_posters.append(fetch_poster(movie_id))

        # Fetch rating dynamically
        try:
            response = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=9f83284458280d72500d4f2ebd14f2ef&language=en-US"
            ).json()
            recommended_ratings.append(response.get('vote_average', "N/A"))
        except:
            recommended_ratings.append("N/A")

        if len(recommended_movies) == 5:
            break

    return recommended_movies, recommended_posters, recommended_ratings
