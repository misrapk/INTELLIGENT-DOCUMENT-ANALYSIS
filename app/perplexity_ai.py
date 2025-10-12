import os
from dotenv import load_dotenv
from perplexity import Perplexity

load_dotenv()  # Load variables from .env file

api_key = os.getenv("API_KEY")
client = Perplexity(api_key=api_key)

def ask_perplexity(prompt, model="sonar-pro"):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
