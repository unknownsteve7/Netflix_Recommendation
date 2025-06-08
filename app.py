import streamlit as st
from recommend import recommend, all_genres

st.set_page_config(page_title="Netflix Recommender", layout="wide")
st.markdown(
    "<h1 style='text-align: center; color: #E50914; font-family: Arial Black, sans-serif;'>🍿 Netflix-Like Movie Recommender</h1>",
    unsafe_allow_html=True,
)

st.write("")  # spacer

# Input: Movie name with placeholder and centered
movie_name = st.text_input(
    "🎬 Enter a movie name:",
    placeholder="Type your favorite movie here...",
)

# Genre filter with multiselect for more freedom
selected_genres = st.multiselect(
    "🎭 Filter by Genre (optional):",
    options=sorted(list(all_genres)),
    default=None,
)

st.write("")  # spacer

# Button with some style
if st.button("🔥 Recommend Me Movies"):
    genre_filter = selected_genres if selected_genres else None
    names, posters, ratings = recommend(movie_name, genre_filter)

    if names[0] == "Movie not found in dataset.":
        st.error("🚫 Movie not found. Please try another.")
    else:
        st.markdown("---")
        st.markdown("### Your Top 5 Recommendations:")
        cols = st.columns(5)

        for i, col in enumerate(cols):
            with col:
                st.image(posters[i], use_column_width='always')
                st.markdown(f"### [{names[i]}](#) ", unsafe_allow_html=True)  # placeholder for clickable link
                stars = "⭐" * int(round(ratings[i]))
                st.markdown(f"<span style='color:#f5c518; font-size: 20px;'>{stars}</span>", unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray; font-size:12px;'>Made with ❤️ by Mohan | Powered by Streamlit</p>",
    unsafe_allow_html=True,
)
