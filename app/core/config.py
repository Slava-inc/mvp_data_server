import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='env_vars')
print(f"Загружен MEILISEARCH_MASTER_KEY: '{os.getenv('MEILISEARCH_MASTER_KEY')}'")

class Settings:
    PROJECT_NAME: str = "Document AI MVP"
    PROJECT_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./instance/app.db")

    # File Storage
    UPLOAD_DIRECTORY: str = "./uploads"
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    # Elasticsearch
    ELASTICSEARCH_HOST: str = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT: str = os.getenv("ELASTICSEARCH_PORT", "9200")
    ELASTICSEARCH_URL: str = f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"

    # Для Meilisearch
    MEILISEARCH_HOST='localhost'
    MEILISEARCH_PORT=7700
    MEILISEARCH_MASTER_KEY: str = os.getenv("MEILISEARCH_MASTER_KEY", "")
    print(f"Settings.MEILISEARCH_MASTER_KEY установлен в: '{MEILISEARCH_MASTER_KEY}'") # <-- Добавить для отладки


    MEILISEARCH_HOST: str = os.getenv("MEILISEARCH_HOST", "localhost")
    MEILISEARCH_PORT: str = os.getenv("MEILISEARCH_PORT", "7700")
    MEILISEARCH_MASTER_KEY: str = os.getenv("MEILISEARCH_MASTER_KEY", "")
    MEILISEARCH_URL: str = f"http://{MEILISEARCH_HOST}:{MEILISEARCH_PORT}"

    # AI (Ollama settings)
    # OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "") # Закомментировано
    # OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo") # Закомментировано

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2") # Убедитесь, что модель скачана в Ollama


settings = Settings()