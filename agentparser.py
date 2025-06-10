import requests
import datetime
import pandas as pd

# Убедитесь, что у вас есть реализация функции find_id
# Примерная заглушка find_id (вам нужно заменить ее на вашу реальную логику)
def find_id(job_titles, pages_number, area, url_base):
    ids = []
    for title in job_titles:
        params = {
            "text": title,
            "area": area,
            "per_page": 100, # Максимальное количество вакансий на странице
            "page": 0
        }
        # Выполняем запросы к API для каждой страницы
        for page in range(pages_number):
            params["page"] = page
            try:
                response = requests.get(url_base, params=params)
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    ids.append(item["id"])
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при поиске ID вакансий: {e}")
                break # Прекращаем поиск, если возникла ошибка

    return ids


def fill_row(vacancy, columns):
    """Извлекает данные из JSON вакансии и формирует строку для DataFrame."""
    row = {}
    for col in columns:
        if col == 'area':
            row[col] = vacancy.get('area', {}).get('name')
        elif col == 'from':
            row[col] = vacancy.get('salary', {}).get('from')
        elif col == 'to':
            row[col] = vacancy.get('salary', {}).get('to')
        elif col == 'currency':
            row[col] = vacancy.get('salary', {}).get('currency')
        elif col == 'experience':
            row[col] = vacancy.get('experience', {}).get('name')
        elif col == 'schedule':
            row[col] = vacancy.get('schedule', {}).get('name')
        elif col == 'employment':
            row[col] = vacancy.get('employment', {}).get('name')
        elif col == 'employer':
            row[col] = vacancy.get('employer', {}).get('name')
        elif col == 'published_at':
             # Преобразуем дату в нужный формат, если необходимо
            published_at_str = vacancy.get('published_at')
            if published_at_str:
                try:
                    # Пример преобразования из ISO 8601 в YYYY-MM-DD HH:MM:SS
                    published_at_dt = datetime.datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                    row[col] = published_at_dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    row[col] = published_at_str # Оставляем как есть, если не удалось распарсить
            else:
                row[col] = None

        elif col in vacancy:
            row[col] = vacancy[col]
        else:
            row[col] = None # Заполняем None, если поле отсутствует

    return row


def get_vacancies_data(job_titles, pages_number, area):
    """Собирает данные о вакансиях и возвращает DataFrame."""
    url_base = 'https://api.hh.ru/vacancies/'
    ids = find_id(job_titles, pages_number, area, url_base)

    columns = ['id', 'premium', 'name', 'area', 'from', 'to', 'currency', 'experience',
               'schedule', 'employment', 'description', 'employer', 'published_at',
               'alternate_url', 'has_test']

    df = pd.DataFrame(columns = columns)
    leng = 0

    for vacancy_id in ids:
        try:
            vacancy = requests.get(url_base + vacancy_id).json()
            r = fill_row(vacancy, columns)
            df.loc[leng] = r
            leng += 1
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении деталей вакансии {vacancy_id}: {e}")
        except Exception as e:
             print(f"Неизвестная ошибка при обработке вакансии {vacancy_id}: {e}")


    # Переименование колонок для удобства
    df.rename(columns={'area':'city', 'from':'salary_from', 'to':'salary_to', 'alternate_url':'link'}, inplace=True)

    return df

def save_vacancies_to_csv(df, file_path):
    """Сохраняет DataFrame с вакансиями в CSV."""
    try:
        df.to_csv(file_path, index=False, encoding='utf-8')
        return f"Данные о вакансиях сохранены в {file_path}"
    except Exception as e:
        return f"Ошибка при сохранении данных в {file_path}: {e}"

def read_vacancies_from_csv(file_path):
    """Читает данные о вакансиях из CSV и возвращает DataFrame."""
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        return f"Файл {file_path} не найден."
    except Exception as e:
        return f"Ошибка при чтении файла {file_path}: {e}"