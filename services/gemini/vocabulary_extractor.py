import re
import os
from typing import List, Dict, Optional
import requests
from requests.exceptions import RequestException

class VocabularyExtractor:
    """Extracts vocabulary words and definitions from text."""
    
    def __init__(self):
        self.api_url = os.getenv('DICTIONARY_API_URL')
    
    def extract_vocabulary(self, text: str) -> List[Dict[str, str]]:
        # Extract words with 4+ characters
        words = re.findall(r'\b\w{4,}\b', text.lower())
        vocab_list = []
        for word in set(words):  # Remove duplicates
            if len(vocab_list) >= 3:
                break

            definition = self._fetch_definition(word)
            if definition:
                vocab_list.append({"word": word, "definition": definition})

        return vocab_list
    
    def lookup_word(self, word: str) -> Dict:
        """
        Returned examples:
        {
            "word": "hello",
            "phonetic": "/həˈloʊ/",
            "meanings": [
                {
                "partOfSpeech": "exclamation",
                "definitions": [
                    {
                    "definition": "used as a greeting or to begin a phone conversation.",
                    "example": "hello there, Katie!"
                    }
                ]
                }
            ]
        }
        """
        word_data = self._fetch_word_data(word)
        if not word_data: # Not Found
            raise ValueError(f"Word '{word}' not found in dictionary")

        result = {
            "word": word_data["word"],
            "phonetic": word_data.get("phonetic", ""),
            "meanings": []
        }

        for meaning in word_data.get("meanings", []):
            definitions = []
            for defn in meaning.get("definitions", []):
                definition_entry = {
                    "definition": defn.get("definition", ""),
                    "example": defn.get("example", "")
                }
                if definition_entry["example"]:  # Only include non-empty examples
                    definitions.append(definition_entry)
                else:
                    definitions.append({"definition": definition_entry["definition"], "example": ""})
            if definitions:  # Only include meanings with definitions
                result["meanings"].append({
                    "partOfSpeech": meaning.get("partOfSpeech", "unknown"),
                    "definitions": definitions
                })

        return result
    
    def _fetch_word_data(self, word: str) -> Optional[Dict]:
        try:
            response = requests.get(self.api_url.format(word.lower()), timeout=5)
            if response.status_code == 200:
                print(response)
                data = response.json()
                if data and isinstance(data, list) and data[0].get("word"):
                    return data[0]
            return None
        except (RequestException, ValueError, KeyError):
            return None
    
    def _fetch_definition(self, word: str) -> Optional[str]:
        try:
            response = requests.get(self.api_url.format(word), timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Take first entry and first meaning
                if data and isinstance(data, list) and data[0].get("meanings"):
                    meaning = data[0]["meanings"][0]
                    part_of_speech = meaning.get("partOfSpeech", "unknown")
                    definition = meaning["definitions"][0].get("definition", "")
                    return f"{definition}: {part_of_speech}"
            return None
        except (RequestException, ValueError, KeyError):
            return None
        