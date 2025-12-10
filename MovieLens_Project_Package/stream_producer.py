"""
Stream Producer
Goal: Simulate real-time movie ratings and send to Spark Streaming via socket.
"""
import socket
import time
import json
import random
import datetime
import csv

def load_movie_ids():
    try:
        movie_ids = []
        with open('ml-latest-small/movies.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_ids.append(int(row['movieId']))
        return movie_ids
    except Exception as e:
        print(f"Error loading movies: {e}")
        return list(range(1, 1000))

def start_server(host='0.0.0.0', port=9999):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    print(f"Listening on {host}:{port}...")
    
    movie_ids = load_movie_ids()
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        
        try:
            while True:
                # Generate random rating
                data = {
                    'userId': random.randint(1, 1000),
                    'movieId': random.choice(movie_ids),
                    'rating': round(random.uniform(0.5, 5.0) * 2) / 2,
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
                json_data = json.dumps(data) + "\n"
                client_socket.send(json_data.encode('utf-8'))
                print(f"Sent: {json_data.strip()}")
                
                # Sleep random time
                time.sleep(random.uniform(0.1, 0.5))
                
        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()

if __name__ == "__main__":
    start_server()
