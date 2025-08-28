from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.services.search_service import create_index_if_not_exists

# Создание таблиц БД
Base.metadata.create_all(bind=engine)
create_index_if_not_exists()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

# Подключение роутов API
app.include_router(api_router)

# Опционально: подключить статические файлы, если понадобятся
# app.mount("/static", StaticFiles(directory="app/static"), name="static")