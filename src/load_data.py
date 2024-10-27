# load_data.py
import csv


def load_movies(redis_client):
    with open('rotten_tomatoes_movies.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["tomatometer_status"] == "Certified-Fresh" and row["content_rating"] != "NR":
                redis_client.set(row["movie_title"], str(row))
