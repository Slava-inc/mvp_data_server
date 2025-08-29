# app/services/chunking_service.py
"""
Сервис для разбиения текста документов на фрагменты (chunks).
"""

import math
from typing import List, Generator

def chunk_by_tokens(text: str, max_tokens: int = 500, overlap_tokens: int = 50) -> Generator[str, None, None]:
    """
    Разбивает текст на фрагменты по максимальному количеству токенов.
    Примечание: Это упрощенная эвристика. Точный подсчет токенов требует
    использования токенизатора модели (например, tiktoken для OpenAI).
    Здесь мы приблизительно считаем 1 токен = 4 символа.
    """
    if not text:
        return

    # Очень грубая оценка: ~1 токен = 4 символа
    # Это НЕ точный способ, но подходит для MVP.
    # Для продакшена используйте библиотеки типа tiktoken.
    CHARS_PER_TOKEN = 4

    effective_chunk_size_chars = max_tokens * CHARS_PER_TOKEN
    effective_overlap_size_chars = overlap_tokens * CHARS_PER_TOKEN

    if effective_chunk_size_chars <= 0:
        raise ValueError("max_tokens должно быть положительным числом.")

    start = 0
    text_length = len(text)
    is_first = True

    while start < text_length:
        # Определяем конец текущего фрагмента
        end = start + effective_chunk_size_chars
        
        # Если это не первый фрагмент, добавляем перекрытие в начало
        if not is_first and start > 0:
            start = max(0, start - effective_overlap_size_chars)
            
        # Извлекаем фрагмент
        chunk = text[start:end].strip()
        
        if chunk: # Проверяем, что фрагмент не пустой
            yield chunk

        # Переходим к следующему фрагменту
        start = end
        is_first = False

def chunk_by_paragraphs(text: str, max_chunk_size: int = 2000) -> Generator[str, None, None]:
    """
    Разбивает текст на фрагменты по абзацам (\n\n), стараясь не превышать max_chunk_size символов.
    """
    if not text:
        return

    paragraphs = text.split('\n\n')
    current_chunk = ""
    
    for paragraph in paragraphs:
        # Проверяем, поместится ли абзац в текущий фрагмент
        test_chunk = (current_chunk + "\n\n" + paragraph).strip() if current_chunk else paragraph
        
        if len(test_chunk) <= max_chunk_size:
            current_chunk = test_chunk
        else:
            # Если абзац слишком большой, его нужно разбить или он становится отдельным фрагментом
            if current_chunk:
                # Сначала отдаем накопленный фрагмент
                yield current_chunk.strip()
                current_chunk = "" # Сброс
            
            # Теперь обрабатываем большой абзац
            if len(paragraph) <= max_chunk_size:
                # Если абзац вдруг стал меньше лимита (редкий случай после обрезки), добавляем его
                current_chunk = paragraph
            else:
                # Абзац больше лимита, разбиваем его принудительно
                # Простой способ: разбить по предложениям или строкам
                lines = paragraph.split('\n')
                temp_chunk = ""
                for line in lines:
                    test_line_chunk = (temp_chunk + "\n" + line).strip() if temp_chunk else line
                    if len(test_line_chunk) <= max_chunk_size:
                        temp_chunk = test_line_chunk
                    else:
                        if temp_chunk:
                            yield temp_chunk.strip()
                            temp_chunk = line # Начинаем новый фрагмент с текущей строки
                        else:
                            # Если даже одна строка больше лимита, обрезаем её
                            yield line[:max_chunk_size].strip()
                if temp_chunk:
                    yield temp_chunk.strip()
                    
    # Не забываем про последний фрагмент
    if current_chunk:
        yield current_chunk.strip()


# Можно выбрать стратегию по умолчанию
DEFAULT_CHUNKING_STRATEGY = chunk_by_paragraphs # или chunk_by_tokens

def create_chunks(text: str, strategy=None, **kwargs) -> List[str]:
    """
    Создает список фрагментов из текста, используя заданную стратегию.
    """
    if strategy is None:
        strategy = DEFAULT_CHUNKING_STRATEGY
        
    chunks = list(strategy(text, **kwargs))
    print(f"Текст разбит на {len(chunks)} фрагментов.")
    return chunks

# --- Пример использования ---
# text = "Ваш очень длинный текст документа..."
# chunks = create_chunks(text, strategy=chunk_by_paragraphs, max_chunk_size=1500)
# for i, chunk in enumerate(chunks):
#     print(f"--- Фрагмент {i+1} ---")
#     print(chunk)
#     print("-" * 20)
