import argparse
import json
import os
import sys
def generate_metadata(title, description):
    # Define a dictionary to map genres
    genres = {
        'action': ['fight', 'battle', 'war', 'adventure'],
        'comedy': ['funny', 'laughter', 'joke', 'humor'],
        'drama': ['sad', 'emotional', 'tragic', 'heartbreaking'],
        'horror': ['scary', 'frightening', 'spooky', 'terrifying'],
        'romance': ['love', 'heart', 'relationship', 'cute']
    }
    # Define a dictionary to map languages
    languages = {
        'english': ['english', 'american', 'us'],
        'spanish': ['spanish', 'latin', 'latin american'],
        'french': ['french', 'france', 'paris'],
        'german': ['german', 'germany', 'berlin'],
        'italian': ['italian', 'italy', 'rome']
    }
    # Define a dictionary to map duration categories
    duration_categories = {
        'short': ['short', 'brief', 'concise'],
        'medium': ['medium', 'average', 'standard'],
        'long': ['long', 'extended', 'epic']
    }
    # Initialize metadata dictionary
    metadata = {
        'genre': None,
        'language': None,
        'duration_category': None
    }
    # Determine genre
    for genre, keywords in genres.items():
        for keyword in keywords:
            if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                metadata['genre'] = genre
                break
    # Determine language
    for language, keywords in languages.items():
        for keyword in keywords:
            if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                metadata['language'] = language
                break
    # Determine duration category
    for duration_category, keywords in duration_categories.items():
        for keyword in keywords:
            if keyword.lower() in title.lower() or keyword.lower() in description.lower():
                metadata['duration_category'] = duration_category
                break
    return metadata
def main():
    parser = argparse.ArgumentParser(description='Generate content metadata tags')
    parser.add_argument('--title', required=True, help='Media item title')
    parser.add_argument('--description', required=True, help='Media item description')
    parser.add_argument('--output', required=True, help='Output file path')
    args = parser.parse_args()
    metadata = generate_metadata(args.title, args.description)
    with open(args.output, 'w') as f:
        json.dump(metadata, f)
if __name__ == '__main__':
    main()
