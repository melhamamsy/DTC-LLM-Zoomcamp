import os
from dotenv import load_dotenv

def initialize_env_variables():
    # Construct the full path to the .env file
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    dotenv_path = os.path.join(project_root, '.env')

    print("Initialized environment variables listed in:",dotenv_path)
    # Load the .env file
    load_dotenv(dotenv_path)
