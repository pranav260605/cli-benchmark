import argparse
     import json
     import re
     import sys
     # Precompiled patterns for performance
     GENRE_PATTERNS = ...
     LANGUAGE_PATTERNS = ...
     DURATION_PATTERNS = ...
     def infer_genre(text):
         ...
     def infer_language(text):
         ...
     def infer_duration(text):
         ...
     def main():
         parser = argparse.ArgumentParser(...)
         args = parser.parse_args()
         text = f"{args.title} {args.description}".lower()
         genre = infer_genre(text)
         language = infer_language(text)
         duration = infer_duration(text)
         result = {"genre": genre, "language": language, "duration_category": duration}
         print(json.dumps(result))
     if __name__ == "__main__":
         main()
