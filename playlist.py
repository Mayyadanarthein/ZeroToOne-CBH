import requests
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from transformers import AutoModel, AutoTokenizer
import torch
import random
from pymongo import MongoClient
import isodate
import json
import os

app = Flask(__name__)
CORS(app)

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")



#mongoDB connection details 
MONGO_URI = "your_mongodb_uri"
client = MongoClient(MONGO_URI)
db = client['your_database_name']
collection = db['your_collection_name']

YOUTUBE_API_KEY = 'AIzaSyASwohtC_VIB4G6-kVmiZlTGSLgb-9KS8g'

# Define a set of expanded predefined vibes/themes with varied descriptions
themes = {
    "romantic": ["love ballad", "romantic music", "soft love songs"],
    "energetic": ["party anthems", "high-energy music", "upbeat dance hits"],
    "dark": ["gothic rock", "dark alternative", "moody indie rock"],
    "chill": ["lofi beats", "relaxation music", "smooth background tunes"],
    "passionate": ["intense ballad", "emotional pop", "soulful R&B"],
    "happy": ["upbeat pop music", "feel-good anthems", "cheerful tunes"],
    "sad": ["melancholic indie", "heartbreak ballads", "somber acoustic"],
    "uplifting": ["motivational pop", "inspiring music", "positive vibes"],
    "moody": ["alternative R&B", "melancholic vibes", "deep soul"],
    "jazzy": ["smooth jazz", "classic jazz standards", "instrumental jazz"],
}

# Function to get embedding of a word or phrase
def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# Function to find the theme with the closest vibe, randomly selecting a description for added diversity
def find_closest_theme(input_words):
    input_embedding = get_embedding(input_words)
    best_theme = None
    best_similarity = -1
    selected_description = ""

    for theme, descriptions in themes.items():
        for description in descriptions:
            theme_embedding = get_embedding(description)
            similarity = np.dot(input_embedding, theme_embedding.T) / (
                np.linalg.norm(input_embedding) * np.linalg.norm(theme_embedding)
            )
            if similarity > best_similarity:
                best_similarity = similarity
                best_theme = theme
                selected_description = description  # Select specific description for query

    return selected_description
@app.route('/api/generatePlaylist', methods=['POST'])
def generate_playlist():
    data = request.get_json()
    words = " ".join([data['word1'], data['word2'], data['word3']])
    query = find_closest_theme(words)

    random_offset = random.randint(0, 20)
    youtube_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={YOUTUBE_API_KEY}&maxResults=10"
    response = requests.get(youtube_url)
    results = response.json()

    # Return video IDs instead of full links
    playlist = [
        item['id']['videoId'] for item in results.get('items', [])
    ]
    # Get video details including duration
    video_details_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet&id={','.join(playlist)}&key={YOUTUBE_API_KEY}"
    details_response = requests.get(video_details_url)
    details_results = details_response.json()

    # Filter videos with duration over 7 minutes
    filtered_videos = [
        item['id'] for item in details_results.get('items', [])
        if isodate.parse_duration(item['contentDetails']['duration']).total_seconds() <= 420
    ]

    # Parse video details
    parsed_videos = [
        {
            'url': f"https://www.youtube.com/watch?v={item['id']}",
            'length': isodate.parse_duration(item['contentDetails']['duration']).total_seconds(),
            'name': item['snippet']['title'],
            'thumbnail': item['snippet']['thumbnails']['default']['url']
        }
        for item in details_results.get('items', [])
        if item['id'] in filtered_videos
    ]

    # Save parsed videos to a JSON file
    playlist_name = data.get('playlist_name', 'playlist')
    json_filename = f"{playlist_name}.json"
    json_filepath = os.path.join('templates', json_filename)
    
    with open(json_filepath, 'w') as json_file:
        json.dump(parsed_videos, json_file)

    return send_file(json_filepath, as_attachment=True)

@app.route('/get_playlist', methods=['GET'])
def get_playlist():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    random_offset = random.randint(0, 20)
    youtube_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={YOUTUBE_API_KEY}&maxResults=10"
    response = requests.get(youtube_url)
    results = response.json()

    # Return video IDs instead of full links
    playlist = [
        item['id']['videoId'] for item in results.get('items', [])
    ]
    # Get video details including duration
    video_details_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={','.join(playlist)}&key={YOUTUBE_API_KEY}"
    details_response = requests.get(video_details_url)
    details_results = details_response.json()

    # Filter videos with duration over 7 minutes
    filtered_videos = [
        item['id'] for item in details_results.get('items', [])
        if isodate.parse_duration(item['contentDetails']['duration']).total_seconds() <= 420
    ]
    return jsonify({'playlist': filtered_videos})



if __name__ == '__main__':
    app.run(port=5600)
