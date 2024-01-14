import pandas as pd
import requests
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


@st.cache_data
def load_data(api_key):
    url = 'https://github.com/tjwaterman99/boxofficemojo-scraper/releases/latest/download/revenues_per_day.csv.gz'
    revenue_df = pd.read_csv(url, parse_dates=['date'], index_col='id')
    revenue_df.sort_values(by='date', inplace=True)

    # Fetch trending movies data
    trending_movies = fetch_all_pages(api_key, 'trending/all/week')
    trending_df = pd.DataFrame(trending_movies)
    trending_df["common_name"] = trending_df.apply(lambda row: row["name"] if pd.notnull(row["name"]) else row["title"], axis=1)

    # Fetch providers for each trending movie
    providers = fetch_providers_for_trending_movies(trending_df, api_key)

    providers_dict = {}
    for provider in providers:
        providers_dict[provider["id"]] = provider


    return revenue_df, trending_df, providers_dict


def fetch_providers_for_trending_movies(trending_df, api_key):
    providers = []
    for _, row in trending_df.iterrows():
        id = row["id"]
        type = row["media_type"]
        try:
            movie_providers = fetch_all_pages(api_key, f'{type}/{id}/watch/providers')
            if "PL" in movie_providers:
                movie_providers["PL"]["id"] = id
                providers.append(movie_providers["PL"])
        except:
            pass
    return providers

def fetch_all_pages(api_key, endpoint, max_pages=1):
    url = f'https://api.themoviedb.org/3/{endpoint}'
    params = {'api_key': api_key, 'page': 1}
    response = requests.get(url, params=params)
    data = response.json()
    total_pages = 1
    if 'total_pages' in data:
        total_pages = min(data['total_pages'], max_pages)


    all_results = data['results']

    for page in range(2, total_pages + 1):
        params['page'] = page
        response = requests.get(url, params=params)
        data = response.json()
        all_results.extend(data['results'])

    return all_results

def display_providers(providers, media_details):
    st.subheader("Available providers in Poland")
    st.markdown("<h5>Rent</h5>", unsafe_allow_html=True)
    print_platforms("rent", providers, media_details)
    st.markdown("<h5>Flatrate</h5>", unsafe_allow_html=True)
    print_platforms("flatrate", providers, media_details)
    st.markdown("<h5>Buy</h5>", unsafe_allow_html=True)
    print_platforms("buy", providers, media_details)

def print_platforms(type, providers, media_details):
    platforms = []
    if media_details["id"] not in providers:
        return
    if type in providers[media_details["id"]]:
        for provider in providers[media_details["id"]][type]:
            if provider["provider_name"] == "Apple TV":
                #st.image('images/apple_tv_icon.png', width=100)
                platforms.append('images/apple_tv_icon.jpg')
            if provider["provider_name"] == "Amazon Video":
                #st.image('images/amznprime_icon.png', width=100)
                platforms.append('images/amznprime_icon.png')
            if provider["provider_name"] == "YouTube":
                #st.image('images/youtube_icon.png', width=100)
                platforms.append('images/youtube_icon.png')
            if provider["provider_name"] == "Google Play Movies":
                #st.image('images/google_icon.png', width=100)
                platforms.append('images/google_icon.png')
            if provider["provider_name"] == "Netflix":
                #st.image('images/netflix_icon.png', width=100)
                platforms.append('images/netflix_icon.png')
            if provider["provider_name"] == "HBO Max":
                #st.image('images/hbo_icon.png', width=100)
                platforms.append('images/hbo_icon.png')
    st.image(platforms, width=40)

def display_media_details(media_details):
    
    # Check if adult content and add Oppenheimer for presenting purpose
    #if media_details['adult'] or media_details['common_name'] == 'Oppenheimer':
       # st.markdown("<span style='color: red;'>**This movie is for adults only!**", unsafe_allow_html=True)
       # st.image('adult.jpg')

    # Check if adult content and add Oppenheimer for presenting purpose
    if media_details['adult'] or media_details['common_name'] == 'Oppenheimer':
        st.markdown("<p style='color: red; text-align: center; <div style='text-align: center;'>**This movie is for adults only!**</p>", unsafe_allow_html=True)
        #st.image('adult.jpg', caption="Adult Content", use_column_width=True, output_format='auto', width=200)
        st.image('images/adult.jpg', caption="Adult Content", width=200)
        

    # Display description
    
    st.write(media_details['overview'])

    # Gauge chart
    st.subheader("Rating")
    vote_color_ranges = {
        (0, 4.99): "#E85E5E",
        (5, 7.99): "#F3E55B",
        (8, 10): "#96DC45"
    }

    def get_color_for_vote(vote_average):
        for range, color in vote_color_ranges.items():
            if range[0] <= vote_average <= range[1]:
                return color
        return "grey"

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = media_details['vote_average'],
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Average Vote"},
        gauge = {'axis': {'range': [None, 10]},
                 'bar': {'color': get_color_for_vote(media_details['vote_average'])}}))

    st.plotly_chart(fig)

    # Show vote count
    st.write(f"Vote Count: {media_details['vote_count']}")

def display_popularity(popularity_df, selected_media):
    print("selected")
    print(selected_media)
    print(popularity_df)
    st.write(f"{popularity_df[popularity_df['common_name'] == selected_media]['popularity'].iloc[0]}")
    # Filter top 10 popular movies
    top_10_popular = popularity_df.nlargest(10, 'popularity')

    # Extend the popular df 
    if selected_media not in top_10_popular['common_name'].values:
         selected_media_row = popularity_df[popularity_df["common_name"] == selected_media].iloc[0]
         top_10_popular.loc[len(top_10_popular)] = selected_media_row

    # Create bar chart
    fig = px.bar(top_10_popular, x='common_name', y='popularity', text='popularity')

    # Customize the appearance of the selected movie
    fig.add_annotation(
        x=selected_media,
        y=top_10_popular[top_10_popular['common_name'] == selected_media]['popularity'].iloc[0],
        text='Selected Movie',
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40
    )

    # Apply underlining style or color change to the selected movie
    fig.update_traces(marker_color=np.where(top_10_popular['common_name'] == selected_media, '#E85E5E', '#7C9FE4'))

    # Show the chart
    st.plotly_chart(fig)

def display_total_revenues(revenue_df, selected_movie):
    print(selected_movie)
    aggregated_revenues = revenue_df[['title','revenue']].groupby(['title'], as_index=False).sum().sort_values(by=['revenue'], ascending=False)
    print("title")
    print(selected_movie)
    print(aggregated_revenues)
    index = np.where(aggregated_revenues["title"] == selected_movie)
    st.write(f"{aggregated_revenues[aggregated_revenues['title'] == selected_movie]['title'].iloc[0]}")
    # Filter top 10 popular movies
    n = len(aggregated_revenues)
    top_popular = aggregated_revenues.iloc[:3]
    print("wtf")
    print(index)
    less_popular = aggregated_revenues.iloc[index[0][0]+1:index[0][0]+11]
    
    result = None
    if selected_movie not in top_popular['title'].values and selected_movie not in less_popular['title'].values:
        selected_media_row = aggregated_revenues.iloc[index]
        result = pd.concat([top_popular, selected_media_row, less_popular])
    else:
        result = pd.concat([top_popular, less_popular])

    # # Extend the popular df 
    # if selected_media not in top_10_popular['common_name'].values:
    #      selected_media_row = popularity_df[popularity_df["common_name"] == selected_media].iloc[0]
    #      top_10_popular.loc[len(top_10_popular)] = selected_media_row

    # Create bar chart
    fig = px.bar(result, x='title', y='revenue', text='revenue')

    # Customize the appearance of the selected movie
    fig.add_annotation(
        x=selected_movie,
        y=result[result['title'] == selected_movie]['revenue'].iloc[0],
        text='Selected Movie',
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40
    )

    # Apply underlining style or color change to the selected movie
    fig.update_traces(marker_color=np.where(result['title'] == selected_movie, '#E85E5E', '#7C9FE4'))

    # Show the chart
    st.plotly_chart(fig)


def display_movie_revenue(revenue_df, selected_movie):
    st.subheader("Select Date Range to analyze the revenue")
    min_date = revenue_df[revenue_df['title']==selected_movie]['date'].min().to_pydatetime()
    max_date = revenue_df[revenue_df['title']==selected_movie]['date'].max().to_pydatetime()
    if not (pd.isna(min_date) and pd.isna(max_date)):
        date_range = st.slider("Select Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))
        filtered_data = revenue_df[(revenue_df['date'] >= date_range[0]) & (revenue_df['date'] <= date_range[1])]
        movie_revenue = filtered_data[filtered_data['title'] == selected_movie]

        if not movie_revenue.empty:
            fig = px.bar(movie_revenue, x='date', y='revenue', color_discrete_sequence=['#7C9FE4'])
            st.plotly_chart(fig)
        else:
            st.warning("No revenue data available for the selected movie.")
    else:
        st.error(f"Date range is not available. Probably {selected_movie} didn't have premier yet")


