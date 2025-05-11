from typing import Dict, List

class ResponseFormatter:
    def format_response(self, response: str, follow_up_questions: List[Dict], vocabulary: List[Dict]) -> Dict:
        return {
            "response": response,
            "follow_up_questions": follow_up_questions,
            "vocabulary": vocabulary
        }
    
    def format_error(self, error_message: str) -> Dict:
        return {
            "response": f"Error: {error_message}",
            "follow_up_questions": [],
            "vocabulary": []
        }