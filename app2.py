import streamlit as st
import pickle
import pandas as pd
import requests
from streamlit_lottie import st_lottie

API_KEY = '86e10d2d94b938f416bb1ac739f6cc78'

def fetch_movie_details(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    )
    data = response.json()
    rating = data.get('vote_average', 'N/A')
    if isinstance(rating, (int, float)):
        rating = round(rating, 1)
    return {
        "poster_url": "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', ''),
        "overview": data.get('overview', 'No overview available.'),
        "rating": rating,
        "release_date": data.get('release_date', 'Unknown'),
        "genre": ", ".join([genre['name'] for genre in data.get('genres', [])])
    }

def fetch_trailer(movie_id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}&language=en-US'
    )
    data = response.json()
    for video in data.get('results', []):
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:8]
    recommendations = []

    for m in movie_list:
        movie_id = movies.iloc[m[0]].movie_id
        details = fetch_movie_details(movie_id)
        details['title'] = movies.iloc[m[0]].title
        details['trailer_url'] = fetch_trailer(movie_id)
        recommendations.append(details)

    return recommendations

# Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

def load_lottie(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

lottie_animation = load_lottie("https://lottie.host/28b808f8-6305-4364-9a98-8a1f44eca52b/fHSZgmt31x.json")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        background-color: #121212;  /* Dark background color */
    }

    .title {
        color: #007BFF; /* Professional blue color */
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 70px;
    }

    .description {
        color: #FFFFFF; /* White color for visibility on black */
        font-size: 19px;
        text-align: center;
        margin-bottom: 30px;
        opacity: 0;
        animation: slide-in 2s forwards;
    }

    @keyframes slide-in {
        0% {
            transform: translateX(-100%);
            opacity: 0;
        }
        100% {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 18px;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .footer {
        text-align: center;
        font-size: 14px;
        color: #666;
        margin-top: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">Movie Recommendation System</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Discover movies tailored to your taste. Choose a movie, and we\'ll handle the rest!</div>', unsafe_allow_html=True)

st_lottie(lottie_animation, speed=1, height=200, key="loading")

st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    'Search for a movie you love:',
    movies['title'].values,
    help="Start typing to search for a movie."
)

st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

if st.button('Recommend'):
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("### Movies you might enjoy 🎥")
    recommendations = recommend(selected_movie_name)

    for details in recommendations:
        with st.expander(f"{details['title']} ({details['rating']}/10)"):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(details["poster_url"], use_container_width=True)
            with col2:
                st.markdown(f"**Genre**: {details['genre']}")
                st.markdown(f"**Release Date**: {details['release_date']}")
                st.markdown(f"**Overview**: {details['overview']}")
                if details['trailer_url']:
                    st.markdown(f"[Watch Trailer]({details['trailer_url']})")

        st.markdown("---")

st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

st.markdown("""<hr style="border:1px solid gray;">""", unsafe_allow_html=True)
st.markdown(
    """
    <div class="footer">Developed with ❤️ using <a href="https://streamlit.io" style="color: #007BFF; text-decoration: none;">Streamlit</a>. Connect with us on <a href="#" style="color: #007BFF; text-decoration: none;">LinkedIn</a> | <a href="#" style="color: #007BFF; text-decoration: none;">GitHub</a></div>
    """,
    unsafe_allow_html=True
)
