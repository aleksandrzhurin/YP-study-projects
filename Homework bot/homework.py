import logging
import os
import time
import sys

import requests
import telegram
from dotenv import load_dotenv

from exceptions import KeyNotResponse

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('main.log', 'w', 'utf-8')
handler.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        logger.debug(f'Сообщение {message}. Начало отправки')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError:
        logger.error(f'Сообщение {message} не отправлено')
    else:
        logger.debug(f'Сообщение {message}. Отправлено')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.ConnectionError:
        raise requests.ConnectionError('Эндпоинт недоступен')
    except requests.RequestException:
        logger.error('Код ответа не 200')
    if response.status_code in [500, 401]:
        raise requests.RequestException('Неверный код ответа 500/401')
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('"response" не словарь')
    if 'homeworks' not in response:
        raise KeyNotResponse('Ключа "homeworks" нет в response')
    if not isinstance(response['homeworks'], list):
        raise TypeError('В ключе "homeworks" не список')
    if len(response['homeworks']) == 0:
        raise KeyNotResponse('"homeworks" пустой')
    return response['homeworks'][0]


def parse_status(homework):
    """Извлекаем информацию из API."""
    if 'homework_name' not in homework:
        raise KeyError('Ключа "homework_name" нет')
    if 'status' not in homework:
        raise KeyError('Ключа "status" нет')
    if not isinstance(homework, dict):
        raise KeyNotResponse('"homework" не словарь')
    homework_name = homework.get('homework_name')
    verdict = homework.get('status')
    if verdict not in HOMEWORK_VERDICTS or verdict is None:
        raise KeyError('Неожиданный статус домашней работы')
    return (f'Изменился статус проверки'
            f' работы "{homework_name}". {HOMEWORK_VERDICTS[verdict]}')


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Нет обязательных переменных')
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    old_response = None
    err_mes = None
    while True:
        try:
            get_api = get_api_answer(timestamp)
            response = check_response(get_api)
            status = parse_status(response)
            if response['status'] != old_response:
                send_message(bot, status)
                old_response = response['status']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != err_mes:
                send_message(bot, message)
                err_mes = message
        finally:
            timestamp = int(time.time())
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
