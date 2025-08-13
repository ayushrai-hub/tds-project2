import os
import json
import google.generativeai as genai

# Get the API key from environment variable
api_key = os.getenv("GENAI_API_KEY")

if not api_key:
    raise ValueError("GENAI_API_KEY environment variable is not set.")

genai.configure(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"
async def parse_question_with_llm(question_text, uploaded_files=None,folder="uploads"):
    uploaded_files = uploaded_files or []

    SYSTEM_PROMPT = f"""
You are a precise data extraction and analysis assistant.  
You must only:
1. Generate Python 3 code that loads, scrapes, or reads the raw data needed to answer the user's question.  
2. List all external Python libraries that need to be installed (do not list built-in libraries).  
3. Extract the main questions the user is asking (without answering them).  

Rules:
- If no URLs are provided, read files from the "uploads" folder and create metadata.  
- Always save the final dataset to {folder}/data.csv.  
- If other files are saved, record their paths and short descriptions in {folder}/metadata.txt.  
- Include in {folder}/metadata.txt:
    • Output of df.info()  
    • Column names  
    • First few rows (df.head())  
    • An ANSWER_FORMAT block:
      - If the provided files (e.g., questions.txt) contain an explicit answer format (JSON object/array/schema/template), copy it VERBATIM under a header line "ANSWER_FORMAT:".
      - If none is present, write "ANSWER_FORMAT: JSON".
- Create the folder {folder} if it does not exist.  
- The code must be self-contained and runnable without manual edits.  
- Use only Python standard libraries plus: pandas, numpy, beautifulsoup4, requests (and others only if strictly required).  
- If source is a webpage → download and parse.  
- If source is CSV/Excel → read directly.  

Output format:
Respond **only** in valid JSON with this schema:
{{
  "code": "string — Python scraping/reading code as plain text",
  "libraries": ["string — names of external required libraries"],
  "questions": ["string — extracted questions"]
}}

STRICT PROHIBITIONS:
- Do not include explanations, comments, or extra text outside JSON.  
- Do not perform analysis or answer the questions.  
- Do not print or visualize anything unless it is required for metadata.  
- Do not change the JSON schema.  
"""



    user_prompt = f"""
Question:
<questions_file_output>
"{question_text}"
</questions_file_output>

Uploaded files:
<uploaded_files>
"{uploaded_files}"
</uploaded_files>

Your task:
Generate Python code that collects the data needed for the question, saves it to {folder}/data.csv,  
and generates {folder}/metadata.txt with the required metadata.  
Do not answer the question — only collect the data and metadata.  
"""
    model = genai.GenerativeModel(MODEL_NAME)

    response = model.generate_content(
        [SYSTEM_PROMPT, user_prompt],
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
    )

    # Path to the file
    file_path = os.path.join(folder, "metadata.txt")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")
    
    return json.loads(response.text)




async def answer_with_data(question_text, folder="uploads"):
    metadata_path = os.path.join(folder, "metadata.txt")
    with open(metadata_path, "r") as file:
        metadata = file.read()

    SYSTEM_PROMPT2 = f"""
You are a precise Python code generation assistant.  
You must only:
1. Generate Python 3 code that, based on the provided question and metadata, retrieves or processes the data necessary to answer the question.  
2. List all external Python libraries that must be installed (exclude built-in libraries).  
3. If any images/visualizations are generated, convert them to base64-encoded PNGs and include them in the output JSON.  
4. Save the answer to the question as a JSON file named '{folder}/result.json'.

Answer Format compliance:
- Read the "ANSWER_FORMAT" from {folder}/metadata.txt (copied verbatim from questions.txt).
- If ANSWER_FORMAT is present, the final JSON in {folder}/result.json MUST STRICTLY MATCH it:
  • Preserve key names, required fields, types, nesting, and key order if specified.
  • Fill missing required keys with suitable  answers following structures as appropriate (do not invent new keys).
- If ANSWER_FORMAT is "NONE", default to a minimal JSON object:
- If you are unable to find the data then fill the JSON which random data in the specified format type.
  {{
    "answer": random data matching the specified JSON type,
    "images": random data matching the specified JSON type
  }}

Rules:
- Output **only** in the exact JSON schema specified below.  
- The Python code must be self-contained and runnable without manual edits.  
- Do not add explanations, comments, or any text outside the JSON.  
- Do not modify the JSON schema.  
- The generated code will run in a Python REPL.  
- Do not include built-in libraries like "io" in the libraries list.

Output schema:
{{
  "code": "string — Python code as plain text",
  "libraries": ["string — names of external required libraries"]
}}
"""

    user_prompt = f"""
Question:
<questions>
{question_text}
</questions>

Metadata:
<metadata>
{metadata}
</metadata>

Your task:
Generate Python code that:
1. Answers the question using the provided metadata.
2) Detects the ANSWER_FORMAT recorded in metadata:
   - If present, construct the final answer EXACTLY in that format (keys, types, order) and save it to {folder}/result.json.
   - If you are unable to find answers to the question fill the json with random data of sepecifed data type.
   - If absent (ANSWER_FORMAT: NONE), save a minimal JSON object {{ "answer": null, "images": [] }} to {folder}/result.json.
3) If any images/visualizations are produced, embed them as base64 PNGs in the "images" array of the result JSON.


Follow the schema exactly and return only valid JSON.
"""

    # Path to the file
    file_path = os.path.join(folder, "result.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")

    model = genai.GenerativeModel(MODEL_NAME)

    # SYSTEM_PROMPT2 needs to be formatted with the folder
    system_prompt2 = SYSTEM_PROMPT2

    response = model.generate_content(
        [system_prompt2, user_prompt],
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)