
import random
import requests


BASE_URL = "https://qa-internship.avito.com"



def generate_seller_id():
    """
    Генерирует случайный уникальный sellerId в диапазоне 111111-999999
    Проверяет, что для этого sellerId нет объявлений (свободный ID)
    """
    max_attempts = 100  # Защита от бесконечного цикла
    
    for _ in range(max_attempts):
        seller_id = random.randint(111111, 999999)
        
        # Проверяем, есть ли объявления у этого продавца
        response = requests.get(f"{BASE_URL}/api/1/{seller_id}/item")
        
        # Если 404 или пустой массив - sellerId свободен
        if response.status_code == 404:
            return seller_id
        
        if response.status_code == 200:
            items = response.json()
            if len(items) == 0:
                return seller_id
        
        # Если есть объявления - пробуем другой ID
    
    # Если не нашли свободный за max_attempts попыток - это ошибка
    raise RuntimeError(
        f"Не удалось найти свободный sellerId за {max_attempts} попыток. "
        "Попробуйте запустить тесты позже или увеличьте диапазон ID."
    )


# ====================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==================== 

def create_item_and_get_id(seller_id, name="Тестовый товар", price=100):
    """
    Создаёт объявление и возвращает его ID
    Используется в тестах, где нужно сначала создать объявление
    """
    # Шаг 1: Создаём объявление
    payload = {
        "sellerId": seller_id,
        "name": name,
        "price": price,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    assert response.status_code == 200, f"Не удалось создать объявление: {response.text}"
    
    # Шаг 2: Получаем список объявлений продавца, чтобы найти ID
    response = requests.get(f"{BASE_URL}/api/1/{seller_id}/item")
    assert response.status_code == 200
    items = response.json()
    
    # Шаг 3: Находим наше объявление по имени и цене
    for item in items:
        if item.get("name") == name and item.get("price") == price:
            return item["id"]
    
    raise AssertionError("Созданное объявление не найдено в списке")


# ====================
# БЛОК 1: СОЗДАНИЕ ОБЪЯВЛЕНИЯ
# ====================

def test_tk01_create_item_success():
    """ТК-01: Успешное создание объявления"""
    seller_id = generate_seller_id()
    
    # Подготавливаем данные для создания объявления
    payload = {
        "sellerId": seller_id,
        "name": "Новогодний мандарин",
        "price": 99,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }
    
    # Отправляем POST запрос
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    
    # Проверяем результат
    assert response.status_code == 200, f"Ожидали код 200, получили {response.status_code}"
    body = response.json()
    assert "status" in body, "В ответе отсутствует поле 'status'"


def test_tk02_create_without_seller():
    """ТК-02: Создание без обязательного поля sellerId"""
    # Отправляем запрос БЕЗ поля sellerId
    payload = {
        "name": "Test item",
        "price": 100,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    
    # Ожидаем ошибку 400
    assert response.status_code == 400
    body = response.json()
    # Проверяем, что в сообщении есть слово "обязательно"
    message = body.get("result", {}).get("message", "").lower()
    assert "обязательно" in message


def test_tk03_create_invalid_seller_type():
    """ТК-03: Создание с некорректным типом sellerId (строка вместо числа)"""
    payload = {
        "sellerId": "abc",  # передаём строку вместо числа
        "name": "Test item",
        "price": 100,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


def test_tk04_create_negative_price():
    """ТК-04: Создание с отрицательной ценой"""
    seller_id = generate_seller_id()
    
    payload = {
        "sellerId": seller_id,
        "name": "Test item",
        "price": -100,  # отрицательная цена
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


def test_tk05_create_empty_body():
    """ТК-05: Создание с пустым телом запроса"""
    # Отправляем пустой JSON
    response = requests.post(f"{BASE_URL}/api/1/item", json={})
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


def test_tk06_create_with_extra_fields():
    """ТК-06: Создание с лишними полями"""
    seller_id = generate_seller_id()
    
    payload = {
        "sellerId": seller_id,
        "name": "Test item",
        "price": 100,
        "color": "red",  # лишнее поле
        "extra_field": 123,  # ещё одно лишнее поле
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


def test_tk07_create_invalid_name_int():
    """ТК-07: Создание с некорректным типом name (число)"""
    seller_id = generate_seller_id()
    
    payload = {
        "sellerId": seller_id,
        "name": 123,  # число вместо строки
        "price": 100,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


def test_tk08_create_invalid_name_boolean():
    """ТК-08: Создание с некорректным типом name (boolean)"""
    seller_id = generate_seller_id()
    
    payload = {
        "sellerId": seller_id,
        "name": True,  # boolean вместо строки
        "price": 100,
        "statistics": {
            "likes": 1,
            "viewCount": 1,
            "contacts": 1
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/1/item", json=payload)
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


# ====================
# БЛОК 2: ПОЛУЧЕНИЕ ОБЪЯВЛЕНИЯ ПО ID
# ====================

def test_tk10_get_existing_item():
    """ТК-10: Получение существующего объявления"""
    seller_id = generate_seller_id()
    
    # Сначала создаём объявление
    item_id = create_item_and_get_id(seller_id, "Тестовый товар для получения", 150)
    
    # Получаем объявление по ID
    response = requests.get(f"{BASE_URL}/api/1/item/{item_id}")
    
    # Проверяем результат
    assert response.status_code == 200
    body = response.json()
    # API возвращает массив, берём первый элемент
    assert isinstance(body, list), "Ответ должен быть массивом"
    assert len(body) > 0, "Массив не должен быть пустым"
    item = body[0]
    assert item.get("id") == item_id
    assert item.get("sellerId") == seller_id


def test_tk11_get_nonexistent_item():
    """ТК-11: Получение несуществующего объявления"""
    # Генерируем несуществующий UUID
    fake_id = "cbe09960-45a5-49d9-a6ae-dc0734cb7792"
    
    response = requests.get(f"{BASE_URL}/api/1/item/{fake_id}")
    
    # Ожидаем ошибку 404
    assert response.status_code == 404


def test_tk12_get_invalid_id():
    """ТК-12: Получение с невалидным id (строка)"""
    response = requests.get(f"{BASE_URL}/api/1/item/abcde")
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


# ====================
# БЛОК 3: ПОЛУЧЕНИЕ ОБЪЯВЛЕНИЙ ПРОДАВЦА
# ====================

def test_tk13_get_items_by_seller():
    """ТК-13: Получение объявлений по sellerId"""
    seller_id = generate_seller_id()
    
    # Создаём хотя бы одно объявление для этого продавца
    create_item_and_get_id(seller_id, "Товар продавца", 200)
    
    # Получаем все объявления продавца
    response = requests.get(f"{BASE_URL}/api/1/{seller_id}/item")
    
    # Проверяем результат
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list), "Ответ должен быть массивом"
    assert len(items) > 0, "Должно быть хотя бы одно объявление"
    
    # Проверяем, что все объявления принадлежат нужному продавцу
    for item in items:
        assert item.get("sellerId") == seller_id


def test_tk14_get_items_by_seller_empty():
    """ТК-14: Получение по несуществующему sellerId"""
    # Используем sellerId, для которого точно нет объявлений
    unused_seller_id = random.randint(900000, 999999)
    
    response = requests.get(f"{BASE_URL}/api/1/{unused_seller_id}/item")
    
    # API может вернуть либо 200 с пустым массивом, либо 404
    if response.status_code == 404:
        # Это допустимо, пропускаем тест
        pass
    else:
        assert response.status_code == 200
        assert response.json() == []


def test_tk15_get_items_invalid_seller():
    """ТК-15: Некорректный sellerId"""
    response = requests.get(f"{BASE_URL}/api/1/abc/item")
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


# ====================
# БЛОК 4: ПОЛУЧЕНИЕ СТАТИСТИКИ
# ====================

def test_tk16_get_stats_existing():
    """ТК-16: Получение статистики по существующему item"""
    seller_id = generate_seller_id()
    
    # Создаём объявление
    item_id = create_item_and_get_id(seller_id, "Товар со статистикой", 300)
    
    # Получаем статистику
    response = requests.get(f"{BASE_URL}/api/1/statistic/{item_id}")
    
    # Проверяем результат
    assert response.status_code == 200
    stats = response.json()
    assert isinstance(stats, list), "Статистика должна быть массивом"
    assert len(stats) > 0, "Статистика не должна быть пустой"
    
    # Проверяем наличие необходимых полей
    first_stat = stats[0]
    assert "likes" in first_stat
    assert "viewCount" in first_stat
    assert "contacts" in first_stat


def test_tk17_get_stats_nonexistent():
    """ТК-17: Получение статистики несуществующего item"""
    fake_id = "cbe09960-45a5-49d9-a6ae-dc0734cb7793"
    
    response = requests.get(f"{BASE_URL}/api/1/statistic/{fake_id}")
    
    # Ожидаем ошибку 404
    assert response.status_code == 404


def test_tk18_get_stats_invalid_id():
    """ТК-18: Невалидный id (статистика)"""
    response = requests.get(f"{BASE_URL}/api/1/statistic/abcde")
    
    # Ожидаем ошибку 400
    assert response.status_code == 400


# ====================
# БЛОК 5: УДАЛЕНИЕ ОБЪЯВЛЕНИЯ
# ====================

def test_tk19_delete_existing_item():
    """ТК-19: Удаление существующего объявления"""
    seller_id = generate_seller_id()
    
    # Создаём объявление
    item_id = create_item_and_get_id(seller_id, "Товар для удаления", 400)
    
    # Удаляем объявление (используем /api/2/ для DELETE)
    response = requests.delete(f"{BASE_URL}/api/2/item/{item_id}")
    
    # API может вернуть либо 200, либо 204
    assert response.status_code in (200, 204)


def test_tk20_get_deleted_item():
    """ТК-20: Получение удалённого объявления"""
    seller_id = generate_seller_id()
    
    # Создаём и удаляем объявление
    item_id = create_item_and_get_id(seller_id, "Товар для проверки удаления", 500)
    delete_response = requests.delete(f"{BASE_URL}/api/2/item/{item_id}")
    assert delete_response.status_code in (200, 204)
    
    # Пытаемся получить удалённое объявление
    response = requests.get(f"{BASE_URL}/api/1/item/{item_id}")
    
    # Ожидаем ошибку 404
    assert response.status_code == 404


def test_tk21_delete_nonexistent_item():
    """ТК-21: Удаление несуществующего id"""
    fake_id = "cbe09960-45a5-49d9-a6ae-dc0734cb7794"
    
    response = requests.delete(f"{BASE_URL}/api/2/item/{fake_id}")
    
    # Ожидаем ошибку 404
    assert response.status_code == 404


def test_tk22_delete_invalid_id():
    """ТК-22: Удаление с невалидным id"""
    response = requests.delete(f"{BASE_URL}/api/2/item/abcde")
    
    # Ожидаем ошибку 400
    assert response.status_code == 400
