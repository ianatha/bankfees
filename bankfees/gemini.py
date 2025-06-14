import os
import sys
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
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


def generate_content(client: genai.Client, prompt: str, tools: list[Tool] = []) -> str:
  """
  Generate content using the Gemini model.
  Args:
      client: Configured Gemini client.
      prompt: The prompt to use for generating content.
  Returns:
      The generated content as a string, or an empty list if no content is found.
  """
  response = client.models.generate_content(
      model=MODEL_NAME,
      contents=prompt,
      config=GenerateContentConfig(tools=tools, response_modalities=["TEXT"]),
  )

  if not response.candidates:
    print("No candidates found in the response.", file=sys.stderr)
    return []
  if not response.candidates[0].content.parts:
    print("No content parts found in the first candidate.", file=sys.stderr)
    return []
  if not response.candidates[0].content.parts[0].text:
    print("No text found in the first content part.", file=sys.stderr)
    return []

  # Print the raw response for debugging
  print("Raw response:")
  print(json.dumps(response.to_json_dict(), indent=2, ensure_ascii=False))
  print()

  return response.candidates[0].content.parts[0].text


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
