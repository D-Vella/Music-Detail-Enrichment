# app.py
import os
from dotenv import load_dotenv

# 1. Load the .env file: 
# This function searches for the .env file and loads its contents 
# into os.environ, making the variables available throughout the script.
load_dotenv()

# 2. Access the variables using os.environ
openai_key = os.environ.get("OPENAI_API_KEY")
db_url = os.environ.get("DATABASE_URL")
weather_key = os.environ.get("WEATHER_API_KEY")

# 3. Use the variables
if openai_key:
    print(f"✅ Successfully loaded OpenAI Key (first 5 chars): {openai_key[:5]}...")
else:
    print("❌ ERROR: OPENAI_API_KEY is missing. Please check your .env file.")

if db_url:
    print(f"✅ Database URL loaded: {db_url[:30]}...")
