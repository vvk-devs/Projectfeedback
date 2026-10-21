
import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY missing. Check your .env file."
    )

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(timeout=30000),
)

app = FastAPI()


class Review(BaseModel):
    text: str


class Analysis(BaseModel):
    label: str
    score: int
    theme: str


@app.get("/")
def home():
    return {"message": "Feedback API is running"}


@app.post("/analyze", response_model=Analysis)
def analyze(review: Review):
    print("1. Received review:", review.text[:100])

    try:
        start = time.time()
        print("2. Sending request to Gemini...")

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "Analyze this customer review. "
                "Return label as positive, negative, or neutral. "
                "Score must be an integer from 1 to 5. "
                "Theme must be one lowercase word, such as "
                "delivery, taste, price, service, or quality. "
                "Review: " + review.text
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Analysis,
                max_output_tokens=100,
                temperature=0,
            ),
        )

        print(f"3. Gemini responded in {time.time() - start:.2f}s")

        result = response.parsed

        if result is None:
            raise ValueError("Gemini returned no parsed result.")

        return result

    except Exception as error:
        print(f"Gemini error: {type(error).__name__}: {error}")
        raise HTTPException(
            status_code=502,
            detail=f"Gemini analysis failed: {type(error).__name__}",
        ) from error
