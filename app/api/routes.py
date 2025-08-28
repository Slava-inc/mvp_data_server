from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.document import DocumentCreate, DocumentResponse
from app.services import document_service, search_service, ai_service
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
import os
from app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "settings": settings})

@router.post("/upload/", response_model=DocumentResponse)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file:
        raise HTTPException(status_code=400, detail="Файл не выбран")

    # Проверка расширения (простая)
    allowed_extensions = {'.txt', '.docx', '.pdf'}
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Неподдерживаемый тип файла")

    db_document = document_service.save_document(db, file, file.filename)

    # Индексируем в Elasticsearch
    search_service.index_document(db_document.id, db_document.content, db_document.filename)

    return db_document

@router.get("/documents/", response_model=List[DocumentResponse])
async def read_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = document_service.get_documents(db, skip=skip, limit=limit)
    return documents

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def read_document(document_id: int, db: Session = Depends(get_db)):
    db_document = document_service.get_document(db, document_id=document_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Документ не найден")
    return db_document

@router.get("/search/")
async def search(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Пустой поисковый запрос")
    results = search_service.search_documents(query)
    return results

@router.post("/ask/")
async def ask_question(question: str = Form(...), db: Session = Depends(get_db)):
    if not question:
        raise HTTPException(status_code=400, detail="Пустой вопрос")

    # Поиск релевантных документов (берем первый результат как контекст)
    search_results = search_service.search_documents(question)
    context = ""
    if search_results:
        doc_id = search_results[0]['id']
        db_doc = document_service.get_document(db, int(doc_id))
        if db_doc:
            context = db_doc.content[:2000] # Ограничиваем контекст для MVP

    # Запрос к LLM
    answer = await ai_service.ask_llm(question, context)
    return {"question": question, "answer": answer, "context_source": search_results[0]['filename'] if search_results else "Нет контекста"}

# Добавить эндпоинт для генерации отчета (PDF)
# ...