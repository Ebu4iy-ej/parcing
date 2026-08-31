import pandas as pd
import re
import numpy as np

df = pd.read_csv("hh_analytics_dataset.csv")
df = df.drop_duplicates(subset=["Ссылка"]).copy()

def parse_salary(text):
    if pd.isna(text) or text == "Не указана":
        return pd.Series([np.nan, np.nan, None])
    
    # Очищаем строку от подстрок про опыт, чтобы они не попадали в цифры ЗП
    text_clean = re.sub(r'Опыт\s+\d+[-\u2013\d]*\s*(года|лет|месяцев)?', '', str(text), flags=re.IGNORECASE)
    
    currency = None
    if "₽" in text or "руб" in text.lower():
        currency = "RUB"
    elif "so'm" in text.lower() or "сум" in text.lower():
        currency = "UZS"
    elif "₸" in text.lower() or "тенге" in text.lower():
        currency = "KZT"
    elif "$" in text or "usd" in text.lower():
        currency = "USD"
    elif "€" in text or "eur" in text.lower():
        currency = "EUR"

    cleaned_text = re.sub(r'(\d)\s+(\d)', r'\1\2', text_clean)
    numbers = [int(n) for n in re.findall(r'\d+', cleaned_text)]

    sal_from = np.nan
    sal_to = np.nan

    if "от" in text_clean.lower() and "до" in text_clean.lower() and len(numbers) >= 2:
        sal_from, sal_to = numbers[0], numbers[1]
    elif "от" in text_clean.lower() and len(numbers) >= 1:
        sal_from = numbers[0]
    elif "до" in text_clean.lower() and len(numbers) >= 1:
        sal_to = numbers[0]
    elif len(numbers) == 2:
        sal_from, sal_to = numbers[0], numbers[1]
    elif len(numbers) == 1:
        sal_from = numbers[0]

    return pd.Series([sal_from, sal_to, currency])

df[["ЗП_От", "ЗП_До", "Валюта"]] = df["Зарплата"].apply(parse_salary)

# Отфильтровываем фантомные значения ниже 10 000 рублей
df.loc[(df["Валюта"] == "RUB") & (df["ЗП_От"] < 10000), "ЗП_От"] = np.nan
df.loc[(df["Валюта"] == "RUB") & (df["ЗП_До"] < 10000), "ЗП_До"] = np.nan

df["ЗП_Средняя"] = df[["ЗП_От", "ЗП_До"]].mean(axis=1)

df.to_csv("hh_analytics_cleaned.csv", index=False, encoding="utf-8-sig")
print("Данные успешно переочищены и сохранены!")