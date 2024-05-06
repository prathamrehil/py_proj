import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt

movies_data=pd.read_csv('https://raw.githubusercontent.com/danielgrijalva/movie-stats/7c6a562377ab5c91bb80c405be50a0494ae8e582/movies.csv')
movies_data.info()
st.write("""
Average Movie Budget, Grouped by Genre
""")
avg_budget = movies_data.groupby('genre')['budget'].mean().round()
avg_budget = avg_budget.reset_index()
genre = avg_budget['genre']
avg_bud = avg_budget['budget']
fig= plt.figure(figsize=(25,13))
plt.bar(genre, avg_bud, color='green')
plt.xlabel('genre')
plt.ylabel('budget')
plt.title('Average Movie Budget, Grouped by Genre')
# st.pyplot(fig)

# col1,col2 = st.columns([1,5])
# with col1:
#     st.write(genre)
# with col2:
#     st.write(avg_bud)
score_rating=movies_data['score'].unique().tolist()
genre_list=movies_data['genre'].unique().tolist()
year_list=movies_data['year'].unique().tolist()

with st.sidebar:
    st.write("""
    ## Sidebar
    """)
new_score_rating=st.slider(label="Choose a Val: ",
                               min_value=0.0,
                               max_value=10.0,
                               value=(3.0,4.0))
new_genre=st.multiselect(label="Choose a Genre: ",
                                options=genre_list,
                                default=['Animation',\
                                         'Comedy',\
                                         'Drama'
                                         ])
year=st.selectbox('Select a Year: ',year_list,0)

score_info=(movies_data['score'].between(*new_score_rating))
new_genre_year=(movies_data['genre'].isin(new_genre))\
                & (movies_data['year']==year)

col1, col2 = st.columns([2,3])
with col1:
    st.write("""#### Lists of movies filtered by year and Genre """)
    dataframe_genre_year = movies_data[new_genre_year]\
    .groupby(['name','genre'])['year'].sum()
    dataframe_genre_year = dataframe_genre_year.reset_index()
    st.dataframe(dataframe_genre_year, width = 400)

with col2:
    st.write("""#### User score of movies and their genre """)
    rating_count_year = movies_data[score_info]\
    .groupby('genre')['score'].count()
    rating_count_year = rating_count_year.reset_index()
    figpx = px.line(rating_count_year, x = 'genre', y = 'score')
    st.plotly_chart(figpx)
    
df=px.data.tips()
fig=px.pie(df,values='tip',names='day')
st.plotly_chart(fig)
dff=px.data.gapminder()
figg=px.scatter(dff.query("year==2007"),x='gdpPercap',y='lifeExp',size='pop',color='continent',hover_name='country',log_x=True,size_max=60)
st.plotly_chart(figg)
