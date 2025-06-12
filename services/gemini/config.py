import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Gemini config
API_KEY = os.getenv('GEMINI_API_KEY')
MODEL = os.getenv('MODEL_GEMINI_2_FLASH')

CONTEXT = """You are an expert English conversation tutor. 
    Your task is to engage in interactive conversations with learners to improve their English communication skills.
    Respond to the learner's input in English, using clear and simple language suitable for their level (beginner to intermediate). 
    Provide response on their input, keep the response concise (1-2 sentences) and relevant to the user's input, and introduce new vocabulary related to the topic. 
    Make the interaction educational, engaging, and fun, using analogies or examples related to the learner's topic.
    Generate 3 follow-up questions or sentences for learners to use in case they cannot think of questions to keep the conversation going. 
    Generate 3 new vocabulary related to the topic.
    Generate a concise title (5-10 words) summarizing the conversation topic.
    All responses must be in JSON format with three fields: 'response' (your reply), \
    'follow_up_questions' (list of suggested questions to help learner keep the conversation going), and \
    'vocabulary' (list of new words with definitions)."""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "response": {"type": "string"},
        "follow_up_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"}
                },
                "required": ["question"]
            }
        },
        "vocabulary": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "word": {"type": "string"},
                    "definition": {"type": "string"}
                },
                "required": ["word", "definition"]
            }
        }
    },
    "required": ["title", "response", "follow_up_questions", "vocabulary"]
}

DICTIONARY_SCHEMA = {
    "type": "object",
    "properties": {
        "word": {"type": "string"},
        "definition": {"type": "string"}
    },
    "required": ["word", "definition"]
}

GENERATION_CONFIG = {
    'temperature': 1,
    'max_output_tokens': 2048,
    'top_p': 0.95,
    'top_k': 64,
    'response_mime_type': 'application/json',
    'response_schema': RESPONSE_SCHEMA
}

DICTIONARY_GENERATION_CONFIG = {
    'temperature': 1,
    'max_output_tokens': 100,
    'top_p': 0.95,
    'top_k': 64,
    'response_mime_type': 'application/json',
    'response_schema': DICTIONARY_SCHEMA
}

SAFETY_SETTINGS = [
    {
        'category' : 'HARM_CATEGORY_HARASSMENT',
        'threshold': 'BLOCK_NONE',
    },
    {
        'category' : 'HARM_CATEGORY_HATE_SPEECH',
        'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
    },
    {
        'category' : 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
        'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
    },
    {
        'category' : 'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold': 'BLOCK_MEDIUM_AND_ABOVE',
    }
]

MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME')
CONVERSATION_COLLECTION = os.getenv('CONVERSATION_COLLECTION')
