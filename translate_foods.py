import pandas as pd
from googletrans import Translator
import os

#df = pd.read_csv("users/data/FOOD-DATA-GROUP1.csv")

# Списък с файлове за превод (относителни или абсолютни пътища)
files_to_translate = [
    "data/FOOD-DATA-GROUP1.csv",
    "data/FOOD-DATA-GROUP2.csv",
    "data/FOOD-DATA-GROUP3.csv",
    "data/FOOD-DATA-GROUP4.csv",
    "data/FOOD-DATA-GROUP5.csv"
]

translator = Translator()

for file_path in files_to_translate:
    try:
        df = pd.read_csv(file_path)
        
        if 'food' not in df.columns:
            print(f"⛔ Пропуснат файл (няма 'food' колона): {file_path}")
            continue

        # Превеждаме уникалните стойности
        unique_foods = df['food'].unique()
        translations = {}

        for food in unique_foods:
            try:
                translated = translator.translate(food, src='en', dest='bg').text
                translations[food] = translated
            except Exception:
                translations[food] = food  # при грешка оставя оригинала

        # Създаване на нова колона и изтриване на старата
        df['food_name'] = df['food'].map(translations)
        df = df.drop(columns=['food'])

        # Пренареждане на колоните
        cols = ['food_name'] + [col for col in df.columns if col != 'food_name']
        df = df[cols]

        # Създаване на име за преведения файл
        filename = os.path.basename(file_path)
        new_filename = filename.replace(".csv", "-BG.csv")
        new_path = os.path.join("data", new_filename)

        # Записване
        df.to_csv(new_path, index=False, encoding='utf-8-sig')
        print(f"✅ Преведен файл: {new_filename}")

    except Exception as e:
        print(f"⚠️ Грешка при обработката на {file_path}: {e}")

files_to_delete = [
    "data/FOOD-DATA-GROUP2.csv",
    "data/FOOD-DATA-GROUP3.csv",
    "data/FOOD-DATA-GROUP4.csv",
    "data/FOOD-DATA-GROUP5.csv",
]

for file_path in files_to_delete:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"✅ Изтрит: {file_path}")
    else:
        print(f"⚠️ Не съществува: {file_path}")
