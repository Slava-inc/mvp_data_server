import meilisearch
from app.core.config import settings

# --- Инициализация клиента Meilisearch ---
try:
    # Создаем клиент с мастер-ключом для административных операций
    meili_client = meilisearch.Client(settings.MEILISEARCH_URL, settings.MEILISEARCH_MASTER_KEY)
    print(f"Клиент Meilisearch инициализирован. URL: {settings.MEILISEARCH_URL}")
except Exception as e:
    print(f"Ошибка инициализации клиента Meilisearch: {e}")
    meili_client = None

# --- Константы ---
INDEX_NAME = "documents"

def create_index_if_not_exists():
    """Создает индекс в Meilisearch, если он еще не существует."""
    if not meili_client:
        print("Клиент Meilisearch не инициализирован.")
        return

    try:
        # Пытаемся получить индекс
        index = meili_client.get_index(INDEX_NAME)
        print(f"Индекс '{INDEX_NAME}' уже существует.")
    except meilisearch.errors.MeilisearchApiError as e:
        # Если индекс не найден, создаем его
        if e.code == "index_not_found":
            try:
                # Создаем индекс. UID и имя индекса совпадают.
                task = meili_client.create_index(uid=INDEX_NAME, options={"primaryKey": "id"})
                # Дожидаемся завершения задачи создания
                meili_client.wait_for_task(task.task_uid)
                print(f"Индекс '{INDEX_NAME}' успешно создан.")
                
                # --- Настройка индекса (опционально, но рекомендуется) ---
                index = meili_client.get_index(INDEX_NAME)
                
                # Настройка поисковых атрибутов (по умолчанию ищет по всем, но можно сузить)
                # index.update_searchable_attributes(['content', 'filename'])
                
                # Настройка отображаемых атрибутов (что возвращается в результатах)
                # index.update_displayed_attributes(['id', 'filename', 'content']) 
                
                # Настройка основного ключа (если не был задан при создании)
                # index.update_primary_key('id') # Уже задан при создании
                
            except Exception as create_error:
                print(f"Ошибка создания индекса '{INDEX_NAME}': {create_error}")
        else:
            # Другая ошибка API
            print(f"Ошибка при проверке существования индекса '{INDEX_NAME}': {e}")
    except Exception as general_error:
        print(f"Неожиданная ошибка при проверке/создании индекса '{INDEX_NAME}': {general_error}")


def index_document(doc_id: str, content: str, filename: str):
    """
    Индексирует документ в Meilisearch.
    В MVP передаем doc_id как строку, так как Meilisearch использует строковые ID.
    """
    if not meili_client:
        print("Клиент Meilisearch не инициализирован.")
        return

    document = {
        "id": str(doc_id), # Meilisearch требует строковый ID
        "content": content,
        "filename": filename
        # Можно добавить другие поля, извлеченные из документа
    }
    
    try:
        index = meili_client.get_index(INDEX_NAME)
        # Используем add_documents, который обновит существующий документ или добавит новый
        task = index.add_documents([document])
        # Опционально: дождаться завершения индексации
        # meili_client.wait_for_task(task.task_uid) 
        print(f"Документ {doc_id} поставлен в очередь на индексацию в Meilisearch.")
    except Exception as e:
        print(f"Ошибка индексации документа {doc_id} в Meilisearch: {e}")

def search_documents(query: str):
    """
    Выполняет поиск по индексу Meilisearch.
    Возвращает список словарей с результатами.
    """
    if not meili_client:
        print("Клиент Meilisearch не инициализирован.")
        return []

    try:
        index = meili_client.get_index(INDEX_NAME)
        
        # Базовый поиск
        # search_results = index.search(query)
        
        # Поиск с параметрами
        search_results = index.search(
            query,
            {
                # "attributesToRetrieve": ["id", "filename"], # Какие атрибуты включить в результаты
                # "limit": 20, # Количество результатов
                # "offset": 0, # Смещение для пагинации
                # "attributesToHighlight": ["content"], # Какие поля подсвечивать
                # "showMatchesPosition": True # Показывать позиции совпадений
            }
        )
        
        hits = search_results.get('hits', [])
        # Преобразуем результаты для возврата
        # Meilisearch возвращает _formatted и другие метаданные, берем основные поля
        results = [
            {
                "id": hit.get('id'),
                "filename": hit.get('filename'),
                # "content_snippet": hit.get('_formatted', {}).get('content', '')[:100] + '...', # Пример сниппета
                "score": hit.get('_rankingScore', 0) # Meilisearch может возвращать разные метрики релевантности
            }
            for hit in hits
        ]
        return results
    except meilisearch.errors.MeilisearchApiError as api_error:
        print(f"Ошибка API Meilisearch при поиске: {api_error}")
        return []
    except Exception as e:
        print(f"Ошибка поиска в Meilisearch: {e}")
        return []

# --- Вызов при запуске приложения ---
# В app/main.py, после Base.metadata.create_all(bind=engine)
# create_index_if_not_exists() # <-- Добавить вызов