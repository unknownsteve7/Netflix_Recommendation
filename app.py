import pandas as pd
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from recommend import recommend

st.title("🍿 Netflix-Like Movie Recommender")
movie_name = st.text_input("Enter a movie name:")

if st.button("Recommend"):
    results = recommend(movie_name)
    for i, title in enumerate(results):
        st.write(f"{i+1}. {title}")
