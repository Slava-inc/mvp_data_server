import os
import re # Импортируем модуль re для работы с регулярными выражениями
from docx import Document as DocxDocument
# from PyPDF2 import PdfReader # или используйте pypdf.PdfReader
# Рекомендуется использовать pypdf, так как PyPDF2 больше не поддерживается
import pypdf

def extract_text_from_file(file_path: str) -> str:
    """Извлекает текст из файла в зависимости от его расширения."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    text = ""

    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        elif ext == '.docx':
            doc = DocxDocument(file_path)
            # Объединяем абзацы, добавляя пробел или перевод строки между ними
            # Это помогает сохранить некоторую структуру, но избежать излишнего разбиения слов
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        elif ext == '.pdf':
            # reader = PdfReader(file_path) # PyPDF2
            reader = pypdf.PdfReader(file_path) # pypdf
            for page in reader.pages:
                text += page.extract_text() + "\n"
        else:
            text = f"[Неподдерживаемый формат файла: {ext}]"
    except Exception as e:
        print(f"Ошибка при извлечении текста из {file_path}: {e}")
        text = f"[Ошибка извлечения текста: {str(e)}]"

    # --- Добавляем постобработку для нормализации текста ---
    if text and not text.startswith("["): # Не обрабатываем сообщения об ошибках
        # 1. Заменить различные виды пробелов и неразрывных пробелов на обычный пробел
        # \s включает пробел, табуляцию, новую строку, возврат каретки, вертикальную табуляцию
        # unicodedata.normalize('NFKD', text) может помочь с нормализацией символов юникода
        import unicodedata
        text = unicodedata.normalize('NFKD', text) # Нормализация символов Unicode
        text = re.sub(r'[^\S ]', ' ', text) # Заменить все пробельные символы (кроме обычного пробела) на пробел
        # 2. Заменить множественные пробелы на один
        text = re.sub(r' +', ' ', text)
        # 3. Заменить множественные переводы строк на двойной перевод строки (для разделения абзацев)
        # Это помогает сохранить структуру абзацев, но убрать лишние пустые строки
        text = re.sub(r'\n\s*\n', '\n\n', text) # Заменить пустые строки на двойной \n
        # 4. Убрать пробелы в начале и конце текста
        text = text.strip()
        # 5. (Опционально) Убрать одиночные переводы строк, оставив только абзацы
        # text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text) # Заменить одиночные \n на пробел, если не окружены другими \n
        # Или более простой вариант - заменить одиночные \n на пробел, а \n\n оставить
        # text = re.sub(r'(?<=\S)\n(?=\S)', ' ', text) # Заменить \n между символами на пробел
        # text = re.sub(r'(?<=\S)\n(?=\s*\n)', '', text) # Убрать \n перед пустой строкой
        # Простой и эффективный способ: заменить одиночные \n на пробел
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    # -------------------------------

    return text

# Пример использования функции нормализации отдельно (для тестирования)
def normalize_text(text: str) -> str:
    """Отдельная функция для нормализации текста."""
    if not text or text.startswith("["):
        return text
    import unicodedata
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^\S ]', ' ', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text) # Заменить одиночные \n на пробел
    return text.strip()
