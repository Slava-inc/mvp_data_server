import httpx
from app.core.config import settings

# Мы сосредоточимся на Ollama, так как он указан как основной способ в этом запросе.
# Код для OpenAI можно оставить закомментированным или удалить.

async def ask_llm(prompt: str, context: str = "") -> str:
    """
    Отправляет запрос к локальной LLM через Ollama API и возвращает ответ.
    """
    # Пример для Ollama API (генерация)
    ollama_generate_url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    # Формируем промт, включая контекст
    full_prompt = f"Ты помощник, отвечающий на вопросы по предоставленным документам.\n\nКонтекст:\n{context}\n\nВопрос: {prompt}\nОтвет:"

    data = {
        "model": settings.OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False, # Получаем полный ответ сразу
        "options": {
            # Можно настроить параметры генерации, например:
            # "temperature": 0.7,
            # "top_p": 0.9,
            # "repeat_penalty": 1.1
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client: # Увеличен таймаут для локальной модели
        try:
            print(f"Отправка запроса к Ollama: {ollama_generate_url}")
            print(f"Модель: {settings.OLLAMA_MODEL}")
            print(f"Промт: {full_prompt[:100]}...")
            response = await client.post(ollama_generate_url, json=data)
            response.raise_for_status()
            json_response = response.json()
            answer = json_response.get('response', 'Ответ не получен.')
            print(f"Ответ от Ollama: {answer[:100]}...")
            return answer
        except httpx.HTTPStatusError as e:
            error_msg = f"Ошибка HTTP при обращении к Ollama: {e.response.status_code} - {e.response.text}"
            print(error_msg)
            return f"Ошибка при обращении к ИИ (Ollama): {error_msg}"
        except httpx.RequestError as e:
            error_msg = f"Ошибка запроса к Ollama: {str(e)}"
            print(error_msg)
            return f"Ошибка при обращении к ИИ (Ollama): {error_msg}"
        except Exception as e:
            error_msg = f"Неожиданная ошибка при обращении к Ollama: {str(e)}"
            print(error_msg)
            return f"Ошибка при обращении к ИИ (Ollama): {error_msg}"

    # return "Ollama не настроен или недоступен." # Этот return не будет достигнут, если try/except охватывает все
