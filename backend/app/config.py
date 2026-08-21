from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # database connection // 
    # db user?
    # db password?

    # Tavily
    # n8n?
    # Gmail thing?
    # LangChain

    # mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / '.env-dev',     # TODO: change to .env later
        env_file_encoding='utf-8'
    )

    # NOTE: loaded in order
    database_url: str

settings = Settings()