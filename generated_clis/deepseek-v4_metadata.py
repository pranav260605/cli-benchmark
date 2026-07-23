import argparse
import json
import re
import sys
def extract_genre(title: str, description: str) -> str:
    """Determine genre based on keywords in title and description."""
    text = (title + " " + description).lower()
    genre_keywords = {
        "action": ["action", "explosion", "fight", "battle", "war", "combat"],
        "comedy": ["comedy", "funny", "humor", "laugh", "hilarious", "sitcom"],
        "drama": ["drama", "emotional", "tragic", "heartbreaking", "intense"],
        "horror": ["horror", "scary", "frightening", "ghost", "haunted", "terror"],
        "sci-fi": ["sci-fi", "science fiction", "space", "alien", "future", "dystopian"],
        "romance": ["romance", "love", "romantic", "relationship", "couple"],
        "thriller": ["thriller", "suspense", "mystery", "twist", "psychological"],
        "documentary": ["documentary", "real", "true story", "biography", "history"],
        "fantasy": ["fantasy", "magic", "mythical", "dragon", "wizard", "enchanted"],
        "animation": ["animation", "animated", "cartoon", "cgi", "pixar"],
    }
    for genre, keywords in genre_keywords.items():
        if any(kw in text for kw in keywords):
            return genre
    return "unknown"
def extract_language(title: str, description: str) -> str:
    """Determine language based on explicit mentions in description."""
    text = description.lower()
    # Common language names and their ISO codes (simplified)
    language_map = {
        "english": "en",
        "spanish": "es",
        "french": "fr",
        "german": "de",
        "italian": "it",
        "portuguese": "pt",
        "japanese": "ja",
        "korean": "ko",
        "chinese": "zh",
        "russian": "ru",
        "arabic": "ar",
        "hindi": "hi",
        "turkish": "tr",
        "dutch": "nl",
        "swedish": "sv",
        "polish": "pl",
        "thai": "th",
        "vietnamese": "vi",
    }
    for lang_name, code in language_map.items():
        if lang_name in text:
            return code
    # Fallback: check title for common language indicators
    title_lower = title.lower()
    for lang_name, code in language_map.items():
        if lang_name in title_lower:
            return code
    return "unknown"
def extract_duration_category(title: str, description: str) -> str:
    """Infer duration category from description (short, medium, long, unknown)."""
    text = (title + " " + description).lower()
    # Look for explicit duration mentions
    # Patterns like "90 minutes", "2 hours", "short film", "feature length"
    duration_patterns = {
        "short": [
            r"\bshort\s*(?:film|movie|video)?\b",
            r"\bunder\s*\d+\s*minutes?\b",
            r"\b\d+\s*minutes?\b(?:\s*or\s*less)?",
            r"\bless\s*than\s*\d+\s*minutes?\b",
        ],
        "medium": [
            r"\b\d{2,3}\s*minutes?\b",  # e.g., 45 minutes, 90 minutes
            r"\b\d+\.?\d*\s*hours?\b",  # e.g., 1.5 hours
            r"\b(?:about|approximately|around)\s*\d+\s*minutes?\b",
        ],
        "long": [
            r"\b(?:over|more\s*than|exceeds?)\s*\d+\s*minutes?\b",
            r"\b\d+\s*hours?\b",  # e.g., 2 hours (if not caught by medium)
            r"\bfeature\s*(?:length|film|movie)?\b",
            r"\blong\s*(?:film|movie|video)?\b",
        ],
    }
    for category, patterns in duration_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return category
    return "unknown"
def main():
    parser = argparse.ArgumentParser(
        description="Generate content metadata tags (genre, language, duration category) for a media item."
    )
    parser.add_argument("title", type=str, help="Title of the media item")
    parser.add_argument("description", type=str, help="Description of the media item")
    args = parser.parse_args()
    genre = extract_genre(args.title, args.description)
    language = extract_language(args.title, args.description)
    duration_category = extract_duration_category(args.title, args.description)
    output = {
        "genre": genre,
        "language": language,
        "duration_category": duration_category,
    }
    # Output as JSON to stdout
    json.dump(output, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
if __name__ == "__main__":
    main()
