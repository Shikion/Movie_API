from fastapi import FastAPI
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib

app = FastAPI()

@app.get("/")
def index():
    return "Hello World"

#Funcion para encontrar la pelicula con mas duracion segun año, plataforma y duration_type
@app.get('/get_max_duration/{year}/{platform}/{duration_type}')
def get_max_duration(year: int, platform: str, duration_type: str):
    data = pd.read_csv('datasets/datos_limpios.csv')
    movies = data[data['type'] == 'movie']

    movies = movies[movies['release_year'] == year]
    movies = movies[movies['platform'] == platform]

    if duration_type == 'min':
        movies = movies[movies['duration_type'].str.contains('min')]
    elif duration_type == 'season':
        return "Intente ingresando 'min'"

    movies = movies.sort_values(by='duration_int', ascending=False)
    movie =  movies['title'].iloc[0]

    return {"pelicula": movie}

#Funcion para recibir todas las peliculas con puntuacion mayor a la indicada segun plataforma y año
@app.get('/get_score_count/{platform}/{scored}/{year}')
def get_score_count(platform: str, scored: float, year: int):
    data = pd.read_csv('datasets/datos_limpios.csv')

    filtered_df = data[(data["platform"] == platform) & (data["release_year"] == float(year))]
    filtered_df = filtered_df[filtered_df["score"] > float(scored)]

    count = len(filtered_df)

    return {
        'plataforma': platform,
        'cantidad': count,
        'anio': year,
        'score': scored
    }

#Funcion que devuelve un int con el numero de peliculas segun su plataforma
@app.get('/get_count_platform/{platform}')
def get_count_platform(platform: str):
    data = pd.read_csv('datasets/datos_limpios.csv')

    filtered_df = data[(data["platform"] == platform)]
    count = len(filtered_df)

    return {'plataforma': platform, 'peliculas': count}

#Funcion que devuelve el actor que mas se repite filtrado por plataforma y año
@app.get('/get_actor/{platform}/{year}')
def get_actor(platform: str, year: int):
    data = pd.read_csv('datasets/datos_limpios.csv')

    filtro = (data["platform"] == platform) & (data["release_year"] == float(year))
    filtered_df = data[filtro]

    actors_count = {}
    for cast in filtered_df["cast"]:
        if pd.notna(cast):
            actors = cast.split(",")
            for actor in actors:
                actor = actor.strip()
                if actor in actors_count:
                    actors_count[actor] += 1
                else:
                    actors_count[actor] = 1

    max_actor = max(actors_count, key=actors_count.get)

    return {
        'plataforma': platform,
        'anio': year,
        'actor': max_actor,
        'apariciones': actors_count[max_actor]
    }

#Funcion que toma un tipo de show, un pais y un año y devuelve la cantidad de producciones de ese año
#en ese pais que sean de ese tipo
@app.get('/prod_per_county/{type}/{country}/{year}')
def prod_per_county(type: str, country: str, year: int):
    data = pd.read_csv('datasets/datos_limpios.csv')

    df_filtrado = data[(data['type'] == type) & (data['country'] == country) & (data["release_year"] == float(year))]
    
    count = len(df_filtrado)
    
    return {'pais': country, 'anio': year, 'peliculas': count}

#Funcion que toma el rating del show y devuelve la cantidad de contenido que posee ese rating
@app.get('/get_contents/{rating}')
def get_contents(rating: str):
    data = pd.read_csv('datasets/datos_limpios.csv')

    filtered_data = data[data['rating'] == rating]
    count = len(filtered_data)

    return {'rating': rating, 'contenido': count}

@app.get('/get_recommendation/{title}')
def get_recommendation(title: str):
    data = pd.read_csv('datasets/datos_limpios.csv')

    X = joblib.load('model.pkl')
    similarity_matrix = cosine_similarity(X)

    # Obtener la fila correspondiente a la película de entrada
    movie_idx = data[data['title'] == title].index[0]
    # Obtener la similitud de la película de entrada con todas las demás películas
    movie_similarities = similarity_matrix[movie_idx]
    # Ordenar las películas según su similitud con la película de entrada y devolver las 5 películas más similares
    similar_movie_indices = movie_similarities.argsort()[::-1][1:6]
    similar_movies = data.iloc[similar_movie_indices]['title'].tolist()


    return {"recomendacion": similar_movies}