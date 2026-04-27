from fastapi import FastAPI, HTTPException
from error_handler import error_manager # Imports your logic
import time

app = FastAPI(title="Reliability Layer API")

@app.post("/api/evaluate_answer")
async def evaluate_answer(session_id: str, answer_text: str, simulate_timeout: bool = False):
    
    # 1. Test the "Silence / No Response" logic
    if not answer_text.strip():
        response = error_manager.handle_user_silence(session_id)
        return response.dict()

    # 2. Test the "LLM Timeout" logic
    if simulate_timeout:
        # We manually trigger a timeout exception for testing purposes
        response = error_manager.handle_llm_timeout(session_id)
        return response.dict()
        
    return {"status": "success", "score": 1, "message": "Answer accepted"}