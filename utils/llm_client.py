import os
from langchain_community.llms import Together
from langchain.prompts import PromptTemplate

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

llm = Together(
    model=MODEL_NAME,
    temperature=0.2,
    max_tokens=512,
    together_api_key=TOGETHER_API_KEY,
)

def call_llm(prompt: str) -> str:
    """Call the Together AI LLM with the given prompt and return the response as a string."""
    try:
        return llm(prompt)
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return "LLM Error: " + str(e)
    

if __name__ == "__main__":
      print(call_llm("Say hello."))