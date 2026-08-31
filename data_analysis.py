import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Настройки стиля графиков
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

# 1. Загрузка очищенных данных
df = pd.read_csv("hh_analytics_cleaned.csv")
rub_df = df[df["Валюта"] == "RUB"].dropna(subset=["ЗП_Средняя"])

print("=== ОСНОВНЫЕ МЕТРИКИ ЗАРПЛАТ (RUB) ===")
print(f"Медианная зарплата: {rub_df['ЗП_Средняя'].median():,.0f} руб.")
print(f"Средняя зарплата:   {rub_df['ЗП_Средняя'].mean():,.0f} руб.")
print(f"Минимальная ЗП:     {rub_df['ЗП_Средняя'].min():,.0f} руб.")
print(f"Максимальная ЗП:    {rub_df['ЗП_Средняя'].max():,.0f} руб.")

# 2. График 1: Распределение зарплат (Гистограмма)
plt.figure(figsize=(10, 6))
sns.histplot(rub_df["ЗП_Средняя"], bins=15, kde=True, color="#4C72B0")
plt.axvline(rub_df["ЗП_Средняя"].median(), color="red", linestyle="--", label=f"Медиана ({rub_df['ЗП_Средняя'].median():,.0f} ₽)")
plt.title("Распределение предлагаемых зарплат для Аналитиков данных (Удаленка)")
plt.xlabel("Зарплата (руб.)")
plt.ylabel("Количество вакансий")
plt.legend()
plt.tight_layout()
plt.savefig("salary_distribution.png", dpi=300)
plt.show()

# 3. График 2: Топ-10 работодателей по количеству вакансий
plt.figure(figsize=(10, 6))
top_companies = df["Компания"].value_counts().head(10)
sns.barplot(x=top_companies.values, y=top_companies.index, palette="viridis")
plt.title("Топ-10 компаний по количеству удаленных вакансий аналитиков")
plt.xlabel("Количество вакансий")
plt.ylabel("Компания")
plt.tight_layout()
plt.savefig("top_companies.png", dpi=300)
plt.show()