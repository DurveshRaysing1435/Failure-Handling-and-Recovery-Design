import time
import logging
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# Set up standard logging (this will eventually connect to your database)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- 1. Define Strict Schemas (API-First Design) ---

class ErrorLogSchema(BaseModel):
    timestamp: str
    incident_id: str
    module: str
    failure_type: str
    severity: str
    retry_count: int
    reason: str
    resolution: str
    session_id: str

class UIResponseSchema(BaseModel):
    status: str
    action: str
    fallback_text: str
    trigger_tts: bool
    allow_input: bool

# --- 2. Core Error Handling Module ---

class FailureHandler:
    def __init__(self):
        # We track state locally for this session. In production, this might live in Redis or a DB.
        self.silence_retries = {}
        self.invalid_retries = {}
        self.llm_retries = {}

    def log_failure(self, log_data: ErrorLogSchema):
        """Simulates pushing the structured error log to your database."""
        logging.error(f"SYSTEM FAILURE LOGGED: {log_data.json()}")
        # Future step: Add database insertion logic here (e.g., MongoDB / PostgreSQL)

    def handle_user_silence(self, session_id: str) -> UIResponseSchema:
        """Handles the 'No Response' edge case."""
        count = self.silence_retries.get(session_id, 0)
        
        if count == 0:
            self.silence_retries[session_id] = 1
            return UIResponseSchema(
                status="handled_failure", action="prompt_user",
                fallback_text="I didn't quite catch that. Could you please provide your answer?",
                trigger_tts=True, allow_input=True
            )
        elif count == 1:
            self.silence_retries[session_id] = 2
            return UIResponseSchema(
                status="handled_failure", action="prompt_user",
                fallback_text="I'm still not hearing anything. If we don't get an answer, we will have to move to the next question.",
                trigger_tts=True, allow_input=True
            )
        else:
            # Max retries reached (Count = 2)
            self.log_failure(ErrorLogSchema(
                timestamp=datetime.utcnow().isoformat(),
                incident_id=f"err_{int(time.time())}",
                module="Audio_Processor", failure_type="user_silence_timeout",
                severity="medium", retry_count=2,
                reason="User failed to respond after 3 attempts.",
                resolution="question_skipped_0_points", session_id=session_id
            ))
            # Reset counter for next question
            self.silence_retries[session_id] = 0 
            return UIResponseSchema(
                status="handled_failure", action="skip_question",
                fallback_text="Let's go ahead and move on to the next question.",
                trigger_tts=True, allow_input=False
            )

    def handle_llm_timeout(self, session_id: str) -> UIResponseSchema:
        """Handles API failures with simulated exponential backoff."""
        count = self.llm_retries.get(session_id, 0)

        if count < 2:
            # Exponential backoff (wait 2s, then 4s)
            backoff_time = 2 ** (count + 1)
            logging.warning(f"LLM Timeout. Applying backoff of {backoff_time} seconds before retry.")
            time.sleep(backoff_time)
            
            self.llm_retries[session_id] = count + 1
            return UIResponseSchema(
                status="retrying", action="retry_llm_call",
                fallback_text="", trigger_tts=False, allow_input=False
            )
        else:
            # Fail gracefully after 2 retries
            self.log_failure(ErrorLogSchema(
                timestamp=datetime.utcnow().isoformat(),
                incident_id=f"err_{int(time.time())}",
                module="LLM_Evaluator", failure_type="llm_timeout",
                severity="high", retry_count=2,
                reason="OpenAI API exceeded response threshold after retries.",
                resolution="fallback_triggered_question_skipped", session_id=session_id
            ))
            # Reset counter
            self.llm_retries[session_id] = 0
            return UIResponseSchema(
                status="handled_failure", action="skip_question",
                fallback_text="I'm experiencing a brief network delay. Let's skip this one for now and move to the next question.",
                trigger_tts=True, allow_input=False
            )

# Instantiate the handler to be imported by your main FastAPI routes
error_manager = FailureHandler()