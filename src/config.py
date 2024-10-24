import os
from dotenv import load_dotenv


load_dotenv()

bot_token=os.getenv('BOT_TOKEN')
sheet_key=os.getenv('SHEET_KEY')
user_id=os.getenv('USER_ID')
username=os.getenv('USER_NAME')