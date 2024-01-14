import streamlit as st
import pandas as pd
from utils import load_data
from utils import display_media_details
from utils import display_movie_revenue
from utils import display_popularity
from utils import display_providers
from utils import display_total_revenues
from utils import print_platforms

# TODO: add total revenue for trending movies and sort it. --> Maciek

# TODO: add total revenue for . --> Maciek

# TODO: Add providers (e.g. Netflix) --> Maciek

# TODO: Add movie/tv image

#theme
base="light"
primaryColor="#100f0f"
secondaryBackgroundColor="#7c9fe4"


# Streamlit title
st.title('Interactive Movie Data Dashboard')









api_key = st.text_input("Enter your API key", type="password")
# api_key = '44f6c761b9c0466960bf14796a06db32'
if api_key:
    data_load_state = st.text('Loading data...')
    revenue_df, trending_df, providers = load_data(api_key)
    revenue_df['date'] = pd.to_datetime(revenue_df['date'].values).to_pydatetime()
    trending_df['release_date'] = pd.to_datetime(trending_df['release_date'].values).to_pydatetime()
    data_load_state.text('Loading data...done!')

    media_type = st.sidebar.radio("Select Media Type", trending_df['media_type'].unique())
    selected_media = st.sidebar.selectbox('Select Media', options=trending_df[trending_df['media_type'] == media_type]['common_name'].unique())
    media_details = trending_df[trending_df['common_name'] == selected_media].iloc[0]
    #display_media_details(media_details)
    #display_popularity(trending_df[trending_df['media_type'] == media_type][['popularity','common_name']], selected_media)
    

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Description", "Popularity", "Historical revenue", "Total revenue", "Providers"])
    # Display common media details
    with tab1:
        st.header("Description")
        #st.display_media_details
        display_media_details(media_details)

        
    with tab2:
        st.header("Popularity")
        #st.display_popularity
        display_popularity(trending_df[trending_df['media_type'] == media_type][['popularity','common_name']], selected_media)

    with tab3:
        st.header("Historical revenue")
        if media_type == 'movie':
            display_movie_revenue(revenue_df, selected_media)
        elif media_type == 'tv':
            st.warning("No revenue data for tv series")
        else:
            st.warning("Please enter your API key to proceed.")

    with tab4:
        st.header("Total revenue")
        if media_type == 'movie':
            display_total_revenues(revenue_df, selected_media)
        elif media_type == 'tv':
            st.warning("No revenue data for tv series")
        else:
            st.warning("Please enter your API key to proceed.")

    with tab5:
        st.header("Providers")
        display_providers(providers, media_details)
        
    


    #print_platforms(providers, media_details)

    #tab1.display_media_details
    #tab2.display_popularity
    #tab3.display_movie_revenue
        
