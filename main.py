from fastapi import FastAPI
import pandas as pd
from sklearn.metrics import pairwise_distances
import joblib

app = FastAPI()

data = pd.read_csv('datasets/datos_limpios.csv')

#Funcion para encontrar la pelicula con mas duracion segun año, plataforma y duration_type
@app.get('/get_max_duration/{year}/{platform}/{duration_type}')
def get_max_duration(year: int, platform: str, duration_type: str):
    global data
    #Filtramos para obtener solo las peliculas
    movies = data[data['type'] == 'movie']

    #Luego filtramos en base a los imputs deceados
    movies = movies[movies['release_year'] == year]
    movies = movies[movies['platform'] == platform]

    #Advertimos que la duracion solo puede ser "min"
    if duration_type == 'min':
        movies = movies[movies['duration_type'].str.contains('min')]
    elif duration_type == 'season':
        return "Intente ingresando 'min'"
    
    #Ordenamos segun la duraccion y seleccionamos la de mayor duracion
    movies = movies.sort_values(by='duration_int', ascending=False)
    movie =  movies['title'].iloc[0]

    return {"pelicula": movie}

#Funcion para recibir todas las peliculas con puntuacion mayor a la indicada segun plataforma y año
@app.get('/get_score_count/{platform}/{scored}/{year}')
def get_score_count(platform: str, scored: float, year: int):
    global data

    #Filtramos en base a los imputs deceados
    filtered_df = data[(data["platform"] == platform) & (data["release_year"] == float(year)) & (data['type'] == 'movie')]
    filtered_df = filtered_df[filtered_df["score"] > float(scored)]

    #Contamos la cantidad de peliculas que posee una calificacion mayor a la dada
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
    global data

    #Filtramos las peliculas en base a su plataforma y contamos cuantas hay en total
    filtered_df = data[(data["platform"] == platform) & (data["type"] == "movie")]
    count = len(filtered_df)

    return {'plataforma': platform, 'peliculas': count}

#Funcion que devuelve el actor que mas se repite filtrado por plataforma y año
@app.get('/get_actor/{platform}/{year}')
def get_actor(platform: str, year: int):
    global data

    #Filtramos plataforma y año de lanzamiento
    filtro = (data["platform"] == platform) & (data["release_year"] == float(year))
    filtered_df = data[filtro]

    #Separamos cada actor precente en "cast" y contamos cuanto aparece cada uno segun las peliculas filtradas
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
    
    #Devolvemos el que haya aparecido mas veces
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
    global data

    #Filtramos segun los imputs requeridos y contamos la cantidad de shows que concuerdan con lo requerido
    df_filtrado = data[(data['type'] == type) & (data['country'].str.contains(country)) & (data['release_year'] == year)]
    num_filas = len(df_filtrado)
    
    return {'paises': country, 'anio': year, 'peliculas': num_filas}

#Funcion que toma el rating del show y devuelve la cantidad de contenido que posee ese rating
@app.get('/get_contents/{rating}')
def get_contents(rating: str):
    global data

    #Filtramos segun la calificacion etaria y devolvemos cuantos shows concuerdan con dicha calificacion
    filtered_data = data[data['rating'] == rating]
    count = len(filtered_data)

    return {'rating': rating, 'contenido': count}

@app.get('/get_recommendation/{title}')
def get_recommendation(title: str):
    global data
    #importamos nuestro modelo de machine learning
    X = joblib.load('model.pkl')

    #Buscamos el indice del show
    movie_idx = data[data['title'] == title].index[0]

    #Aplicamos "pairwise_distance" junto a nuestro modelo para identificar las peliculas similares a la dada
    similarities = pairwise_distances(X, X[movie_idx].reshape(1, -1))
    
    #Ordenamos decrecientemente los resultados y luego buscamos su titulo
    similar_movie_indices = similarities.argsort(axis=0)[1:6].flatten()
    similar_movies = data.iloc[similar_movie_indices]['title'].tolist()

    return {"recomendacion": similar_movies}