import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

API_KEY = 'a2c1bac2e8da4fe8e668520e46f97e57'
BASE_URL = 'https://api.themoviedb.org/3'

def get_movie_details(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}'
    params = {'api_key': API_KEY, 'language': 'pl', 'append_to_response': 'credits'}
    response = requests.get(url, params=params)
    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/table')
def table():
    return render_template('table.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    url = f'{BASE_URL}/search/movie'
    params = {'api_key': API_KEY, 'query': query, 'language': 'pl'}
    response = requests.get(url, params=params)
    data = response.json()
    movies = []

    for result in data['results']:
        movie = get_movie_details(result['id'])
        director_name = ''
        director_id = 0
        for crew_member in movie.get('credits', {}).get('crew', []):
            if crew_member['job'] == 'Director':
                director_name = crew_member['name']
                director_id = crew_member['id']
                break

        movies.append({
            'id': movie['id'],
            'title': movie['title'],
            'director': director_name,
            'director_id': director_id,
            'release_date': movie['release_date'],
            'vote_average': movie['vote_average'],
            'vote_count': movie['vote_count'],
            'poster_path': movie['poster_path']
        })
    return jsonify(movies)

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    movie = get_movie_details(movie_id)
    director_name = ''
    for crew_member in movie.get('credits', {}).get('crew', []):
        if crew_member['job'] == 'Director':
            director_name = crew_member['name']
            break

    movie_data = {
        'title': movie['title'],
        'director': director_name,
        'release_date': movie['release_date'],
        'vote_average': movie['vote_average'],
        'vote_count': movie['vote_count'],
        'overview': movie['overview']
    }
    return jsonify(movie_data)

@app.route('/director/<int:director_id>')
def director(director_id):
    url = f'{BASE_URL}/discover/movie'
    params = {
        'api_key': API_KEY,
        'with_crew': director_id,
        'sort_by': 'vote_average.desc',
        'language': 'pl'
    }
    response = requests.get(url, params=params)
    data = response.json()
    movies = [
        {'title': movie['title'], 'vote_average': movie['vote_average']}
        for movie in data['results'][:10]
    ]
    return jsonify(movies)

if __name__ == '__main__':
    app.run(debug=True)
