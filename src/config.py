import os
from dotenv import load_dotenv


load_dotenv()

bot_token=os.getenv('BOT_TOKEN')
user_id=os.getenv('USER_ID')
username=os.getenv('USER_NAME')

creds_file_path='credentials.json'
sheet_key=os.getenv('SHEET_KEY')