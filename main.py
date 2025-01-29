from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

together_api_key = os.getenv("TOGETHER_API_KEY")

if together_api_key is None:
    print("TOGETHER_API_KEY is not found. Check your .env file.")
else:
    print("API Key Loaded Successfully")
