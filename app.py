import streamlit as st
from recommend import recommend
import streamlit.components.v1 as components

st.title("🎬 Netflix-Like Movie Recommender")
movie_name = st.text_input("Enter a movie name:")

if st.button("Recommend"):
    names, posters = recommend(movie_name)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])
