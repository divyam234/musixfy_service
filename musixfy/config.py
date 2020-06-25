from functools import lru_cache
import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    token: str = ""
    proxy: str = ""
    secret: str = ""

    class Config:
        env_file = os.path.join(os.getcwd(), '.env')


@lru_cache()
def get_settings():
    return Settings()
