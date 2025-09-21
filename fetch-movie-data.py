import json
import csv
import urllib.request
import boto3

# Constants
API_BASE_URL = "https://api.themoviedb.org/3"
API_KEY = "19a028658b3d5b14b8176490f62c607e"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
S3_BUCKET_NAME = "movie-s3-1"  # Replace with your S3 bucket name

# S3 client
s3_client = boto3.client('s3')

def fetch_movie_data(year, min_movies=30):
    try:
        # Fetch genres
        genre_url = f"{API_BASE_URL}/genre/movie/list?api_key={API_KEY}&language=en-US"
        with urllib.request.urlopen(genre_url) as response:
            genre_data = json.load(response)
            genres = {genre['id']: genre['name'] for genre in genre_data.get('genres', [])}

        # Fetch movies for the specified year across multiple pages
        movies = []
        page = 1
        while len(movies) < min_movies:
            movie_url = f"{API_BASE_URL}/discover/movie?api_key={API_KEY}&language=en-US&primary_release_year={year}&sort_by=popularity.desc&page={page}"
            with urllib.request.urlopen(movie_url) as response:
                movie_data = json.load(response)
                results = movie_data.get('results', [])
                movies.extend(results)
                page += 1

                # Stop if no more results are returned
                if not results:
                    break

        # Remove duplicates based on 'id' and limit to desired count
        unique_movies = {movie['id']: movie for movie in movies}.values()
        top_movies = list(unique_movies)[:min_movies]

        return genres, top_movies
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}, []

def process_and_save_data(genres, movies):
    try:
        # Prepare file content
        file_content = []
        header = [
            'Movie ID', 'Title', 'Release Date', 'Genre', 'Vote Average',
            'Vote Count', 'Overview', 'Language', 'Budget', 'Revenue',
            'Poster Path', 'Popularity', 'Adult', 'Production Companies'
        ]
        file_content.append(header)

        for movie in movies:
            movie_id = movie.get('id')
            title = movie.get('title')
            release_date = movie.get('release_date')
            genre_ids = movie.get('genre_ids', [])
            vote_average = movie.get('vote_average')
            vote_count = movie.get('vote_count')
            overview = movie.get('overview')
            language = movie.get('original_language')
            popularity = movie.get('popularity')
            poster_path = f"{IMAGE_BASE_URL}{movie.get('poster_path', '')}"
            adult = movie.get('adult', False)

            # Fetch detailed information
            details_url = f"{API_BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
            with urllib.request.urlopen(details_url) as response:
                details = json.load(response)
                budget = details.get('budget', 'N/A')
                revenue = details.get('revenue', 'N/A')
                production_companies = ", ".join([company['name'] for company in details.get('production_companies', [])])

            # Create a separate row for each genre
            for genre_id in genre_ids:
                genre_name = genres.get(genre_id, "Unknown")
                row = [
                    movie_id, title, release_date, genre_name, vote_average,
                    vote_count, overview, language, budget, revenue,
                    poster_path, popularity, adult, production_companies
                ]
                file_content.append(row)

        # Save to a temporary CSV file
        temp_file_name = "/tmp/top_movies.csv"
        with open(temp_file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(file_content)

        # Upload to S3
        s3_client.upload_file(temp_file_name, S3_BUCKET_NAME, "top_movies.csv")
        print(f"CSV file uploaded to S3 bucket '{S3_BUCKET_NAME}' successfully.")
    except Exception as e:
        print(f"Error processing data: {e}")

# Lambda entry point
def lambda_handler(event, context):
    # Extract year from event arguments
    year = event.get('year', None)
    
    if year is None:
        return {
            'statusCode': 400,
            'body': json.dumps("Year is required.")
        }

    genres, movies = fetch_movie_data(year)
    if not genres or not movies:
        return {
            'statusCode': 500,
            'body': json.dumps("Failed to fetch movie data.")
        }

    process_and_save_data(genres, movies)
    return {
        'statusCode': 200,
        'body': json.dumps(f"CSV file created and uploaded to S3 bucket '{S3_BUCKET_NAME}'.")
    }

if __name__ == "__main__":
    # Example for testing locally
    test_event = {"year": 2023}
    print(lambda_handler(test_event, None))
