# API_FINAL_YATUBE

С помощью данного API, вы сможете создавать и управлять записями о своих котиках. 

## Установка

- Клонируйте репозиторий: 
  ```
  git clone git@github.com:aleksandrzhurin/api_yatube.git
  ```
- Создайте вирутальное окружение:
    ```
    python -m venv venv
    ```
- Установите зависимости: 
    ```
    pip install -r requirements.txt
    ```
- Примените миграции: 
    ```
    python manage.py migrate
    ```
- Запустите API: 
    ```
    python manage.py runserver
    ```


## Примеры работы с API
GET /api/v1/posts/

```Python
#include <stdio.h>
HTTP 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

[
    {
        "id": 1,
        "author": "admin",
        "text": "Привет, это я!",
        "pub_date": "2023-03-20T19:02:38.650878Z",
        "image": null,
        "group": 1
    }
]
```