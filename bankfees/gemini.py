import os
import sys
from typing import Optional
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, SchemaUnion, ThinkingConfig
import json

MODEL_NAME = "gemini-2.5-pro-preview-06-05"

GOOGLE_SEARCH_TOOL = Tool(
    google_search=GoogleSearch()
)


def create_gemini() -> genai.Client:
  """
  Configure the Google Generative AI (Gemini) client.
  Expects the API key in the environment variable GEMINI_API_KEY.
  """
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    print("Error: Please set the GEMINI_API_KEY environment variable.", file=sys.stderr)
    sys.exit(1)
  client = genai.Client(api_key=api_key)
  return client


def generate_content(client: genai.Client, prompt: str, tools: list[Tool] = [], response_schema: Optional[SchemaUnion] = None):
  """
  Generate content using the Gemini model.
  Args:
      client: Configured Gemini client.
      prompt: The prompt to use for generating content.
  Returns:
      The generated content as a string, or an empty list if no content is found.
  """

  if response_schema and len(tools) == 0:
    config = GenerateContentConfig(
        tools=tools,
        thinking_config=ThinkingConfig(
          include_thoughts=False,
          thinking_budget=2000,
        ),
        response_modalities=["TEXT"],
        response_mime_type="application/json",
        response_schema=response_schema,
    )
  elif not response_schema and len(tools) > 0:
    config = GenerateContentConfig(
        tools=tools,
        response_modalities=["TEXT"]
    )
  else:
    raise ValueError("Either response_schema or tools must be provided, but not both.")
  
  response = client.models.generate_content(
      model=MODEL_NAME,
      contents=prompt,
      config=config,
  )

  if not response.candidates:
    raise ValueError("No candidates found in the response.")
  if not response.candidates[0].content.parts:
    raise ValueError("No content parts found in the first candidate.")
  if not response.candidates[0].content.parts[0].text:
    raise ValueError("No text found in the first content part.")

  if response_schema:
    return response_schema.model_validate_json(response.candidates[0].content.parts[0].text)
  else:
    return response.candidates[0].content.parts[0].text.strip()

def generate_content_with_search(client: genai.Client, prompt: str) -> str:
  """
  Generate content using the Gemini model with Google search tool.
  Args:
      client: Configured Gemini client.
      prompt: The search query to use for generating content.
  Returns:
      The generated content as a string, or an empty list if no content is found.
  """
  return generate_content(client, prompt, tools=[GOOGLE_SEARCH_TOOL])
