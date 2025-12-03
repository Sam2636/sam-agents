# llm_client.py
import os
import json
from dotenv import load_dotenv
import openai

# Load environment variables from .env
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a senior software engineer and technical writer.
Your job: convert structured JSON (functions, params, return types, globals)
into a precise, production-style Markdown file.

Rules:
- Do NOT invent functions, params, or types.
- Only use information present in JSON.
- Mark missing fields as MISSING.
- Keep style consistent and professional.
- Include: Summary, Functions (signature, inputs, outputs, description), Globals, Notes, Source Reference.
"""

USER_TEMPLATE = """
Here is the parsed JSON for a source file:

{json_blob}

Produce a Markdown document following the rules above.
"""

def json_to_markdown(parsed_json: dict) -> str:
    json_blob = json.dumps(parsed_json, indent=2)
    prompt = USER_TEMPLATE.format(json_blob=json_blob)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    # ChatCompletion API (OpenAI >=1.0)
    resp = openai.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=messages,
        temperature=0.0,
        max_tokens=1500
    )
    return resp.choices[0].message.content
