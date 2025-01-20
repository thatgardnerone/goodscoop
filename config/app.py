import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'user': {
        'name': os.getenv('USER_NAME'),
        'number': os.getenv('USER_NUMBER'),
    }
}
