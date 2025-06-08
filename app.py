import streamlit as st
from recommend import recommend, all_genres

st.set_page_config(page_title="Netflix Recommender", layout="wide")

# Add slick background color and text color


st.title("🍿 Netflix-Like Movie Recommender")

# Input: Movie name
movie_name = st.text_input("🎬 Enter a movie name:")

# Input: Genre filter
selected_genre = st.selectbox("🎭 Filter by Genre (optional)", ["None"] + sorted(list(all_genres)))

# Button
if st.button("Recommend"):
    genre_filter = None if selected_genre == "None" else selected_genre
    names, posters, ratings = recommend(movie_name, genre_filter)

    if names[0] == "Movie not found in dataset.":
        st.error("🚫 Movie not found. Please try another.")
    else:
        # 5 columns layout
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]

        for i in range(5):
            with cols[i]:
                st.image(posters[i])
                st.markdown(f"**{names[i]}**")
                st.markdown(f"⭐ Rating: {ratings[i]}")
