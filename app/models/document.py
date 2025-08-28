from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String) # Путь к файлу в файловой системе
    content = Column(Text) # Извлеченный текст (для простоты хранится в БД, в реальном проекте лучше в Elasticsearch)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    # Можно добавить project_id, если будет реализовано в будущем