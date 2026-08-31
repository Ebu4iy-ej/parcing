import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Загрузка данных
print("Загрузка датасета...")
df = pd.read_csv("crawlee_books_dataset.csv")
print(f"Успешно загружено {df.shape[0]} строк и {df.shape[1]} колонок.\n")

# 2. Очистка данных (Data Cleaning)
# Наш парсер собрал рейтинг словами (One, Two, Three...). Для математики нужны цифры.
rating_dict = {
    "One": 1, 
    "Two": 2, 
    "Three": 3, 
    "Four": 4, 
    "Five": 5
}
# Создаем новую числовую колонку
df["Рейтинг_число"] = df["Рейтинг"].map(rating_dict)

# Проверяем, нет ли пустых значений после трансформации
if df["Рейтинг_число"].isnull().sum() == 0:
    print("Очистка рейтинга прошла успешно!\n")

# 3. Разведочный анализ (EDA)
print("--- Базовая статистика по ценам ---")
print(df["Цена"].describe().round(2)) # describe() выдает среднее, мин/макс и квартили

print("\n--- Средняя цена в зависимости от рейтинга ---")
price_by_rating = df.groupby("Рейтинг_число")["Цена"].mean().round(2)
print(price_by_rating)

# 4. Визуализация данных
# Настроим стиль графика
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

# Строим Boxplot (ящик с усами). Он идеально показывает распределение цен внутри каждой категории
sns.boxplot(
    x="Рейтинг_число", 
    y="Цена", 
    data=df, 
    hue="Рейтинг_число",
    palette="Set2",
    legend=False
)

plt.title("Распределение цен на книги по рейтингу (1-5 звезд)", fontsize=14, pad=15)
plt.xlabel("Количество звезд", fontsize=12)
plt.ylabel("Цена (£)", fontsize=12)

# Показываем график
plt.show()