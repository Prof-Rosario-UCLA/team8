import os
import json
import asyncio
from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from models.user import User  # Assuming this exists
from controllers.resume import get_full_resume  # Assuming this exists
from db import db  # Assuming this exists

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# --- AI Configuration ---

# It's best practice to configure the API key once when the app starts.
# Ensure the GEMINI_API_KEY environment variable is set.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=GEMINI_API_KEY)

# A more detailed system prompt that sets the persona and task clearly.
SYSTEM_PROMPT = """
You are Pro, an expert resume rating assistant from a service called Prolio.
Your role is to analyze a user's resume, provided as a JSON object, and provide a constructive, helpful, and encouraging critique.
Your response must be a JSON object containing a numerical rating and a brief reasoning for that score.
Focus on providing actionable feedback that the user can implement to improve their resume.

Do not directly reference the JSON structure or fields. Just respond by referring to the natural language text.
"""

# Define the structured response format we expect from the model.
GENERATION_CONFIG = GenerationConfig(
    response_mime_type="application/json",
    response_schema={
        "type": "object",
        "properties": {
            "rating": {
                "type": "number",
                "description": "A rating of the resume on a scale from 1 to 10.",
            },
            "reasoning": {
                "type": "string",
                "description": "A concise, constructive reasoning for the rating, written from the perspective of Pro from Prolio.",
            },
        },
        "required": ["rating", "reasoning"],
    },
)



# --- Flask Blueprint ---

ai_views = Blueprint("ai_views", __name__, url_prefix="/ai")


@ai_views.get("/rate/<int:resume_id>")
@login_required
def rate_resume(resume_id: int):
    """
    Asynchronously rates a resume using the Gemini 1.5 Flash API with JSON mode.
    """
    try:
        # Ensure the logged-in user context is valid.
        assert isinstance(current_user, User)

        # Get the resume data.
        resume_data = get_full_resume(resume_id, current_user, db.session)

        # If resume is not found, return 404.
        if not resume_data:
            return jsonify({"error": "Resume not found or access denied."}), 404

        # Convert the resume object to a JSON string for the prompt.
        try:
            resume_json_string = resume_data.json()
        except TypeError:
            # This catches cases where the resume_data is not JSON serializable.
            return jsonify(
                {"error": "Internal server error: Could not process resume data."}
            ), 500

        # Call the Gemini API asynchronously.
        prompt = (
            f"Please analyze and rate the following resume:\n\n{resume_json_string}"
        )
        
        # Initialize the Gemini model.
        gemini_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=SYSTEM_PROMPT,
            generation_config=GENERATION_CONFIG,
        )

        response = gemini_model.generate_content(prompt) # TODO: make async, but will probably need to change gunicorn to uvicorn

        # UPDATE: Modern best practice is to check the prompt_feedback for safety blocks
        # instead of relying solely on a broad StopCandidateException.
        if response.prompt_feedback.block_reason:
            current_app.logger.error(f"Error: Model response was blocked. Reason: {response.prompt_feedback.block_reason.name}")
            return jsonify(
                {
                    "error": "The resume could not be processed due to a content policy violation."
                }
            ), 400

        # The response.text should be a valid JSON string due to the generation_config.
        result = json.loads(response.text)
        return jsonify(result), 200

    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred: {e}")
        # General error handler for unexpected issues (e.g., API key invalid, network issues).
        return jsonify(
            {"error": "An internal error occurred while rating the resume."}
        ), 500
