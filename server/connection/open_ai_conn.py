from config import get_config

config = get_config()

def init_open_ai():
    api_key = config.openai_api_key
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
    return api_key
