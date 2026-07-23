import argparse
import json
import os
import re
from collections import defaultdict
# Predefined genres and their keywords
genres = {
    'action': ['action', 'adventure', 'thriller'],
    'comedy': ['comedy', 'funny', 'humor'],
    'drama': ['drama', 'emotional', 'serious'],
    'horror': ['horror', 'scary', 'frightening'],
    'romance': ['romance', 'love', 'relationship']
}
# Predefined languages and their keywords
languages = {
    'english': ['english', 'american', 'british'],
    'spanish': ['spanish', 'espanol', 'latin'],
    'french': ['french', 'francais', 'french'],
    'german': ['german', 'deutsch', 'german'],
    'italian': ['italian', 'italiano', 'italian']
}
# Predefined duration categories and their keywords
duration_categories = {
    'short': ['short', 'brief', 'less than 30 minutes'],
    'medium': ['medium', 'average', '30-60 minutes'],
    'long': ['long', 'extended', 'more than 60 minutes']
}
def generate_metadata(title, description):
    metadata = {
        'genre': None,
        'language': None,
        'duration_category': None
    }
    # Genre detection
    for genre, keywords in genres.items():
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', title.lower() + ' ' + description.lower()):
                metadata['genre'] = genre
                break
        if metadata['genre']:
            break
    # Language detection
    for language, keywords in languages.items():
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', title.lower() + ' ' + description.lower()):
                metadata['language'] = language
                break
        if metadata['language']:
            break
    # Duration category detection
    for duration_category, keywords in duration_categories.items():
        for keyword in keywords:
            if re.search(r'\b' + keyword + r'\b', title.lower() + ' ' + description.lower()):
                metadata['duration_category'] = duration_category
                break
        if metadata['duration_category']:
            break
    return metadata
def main():
    parser = argparse.ArgumentParser(description='Generate content metadata tags')
    parser.add_argument('--title', required=True, help='Media item title')
    parser.add_argument('--description', required=True, help='Media item description')
    parser.add_argument('--output', choices=['json', 'csv'], default='json', help='Output format')
    args = parser.parse_args()
    metadata = generate_metadata(args.title, args.description)
    if args.output == 'json':
        print(json.dumps(metadata))
    elif args.output == 'csv':
        print('genre,language,duration_category')
        print(f'{metadata["genre"]},{metadata["language"]},{metadata["duration_category"]}')
if __name__ == '__main__':
    main()
