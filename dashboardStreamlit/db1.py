import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Dashboard")
data=pd.read_csv('https://raw.githubusercontent.com/danielgrijalva/movie-stats/7c6a562377ab5c91bb80c405be50a0494ae8e582/movies.csv')

filter_value=st.sidebar.slider("Filter data by value",
                               min_value=0,
                               max_value=100,
                               value=50)
