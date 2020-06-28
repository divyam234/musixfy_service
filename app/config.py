from functools import lru_cache
import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Load Env Variables
    token: str = os.getenv('ACCESS_TOKEN')
    proxy: str = os.getenv('PROXY')
    secret: str = os.getenv('SECRET')
    cache_path: str = os.getenv('CACHE_PATH')


@lru_cache()
def get_settings():
    return Settings()
