import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from diet_ai.models import UserDietHistory,PredictionLog

MODEL_PATH = 'diet_ai/model.pkl'
ENCODER_PATH = 'diet_ai/encoders.pkl'

def train_model():
    
    MODEL_PATH = 'diet_ai/model.pkl'
    ENCODER_PATH = 'diet_ai/encoders.pkl'

    # Данни от основната таблица
    qs = UserDietHistory.objects.all().values(
        'age', 'weight', 'height', 'sex', 'goal', 'activity', 'recommended_diet'
    )
    df = pd.DataFrame(qs)

    # Данни от PredictionLog с отзив
    feedback_qs = PredictionLog.objects.exclude(feedback__isnull=True).values(
        'age', 'weight', 'height', 'sex', 'goal', 'activity', 'predicted_diet', 'feedback'
    )
    feedback_df = pd.DataFrame(feedback_qs)
    if not feedback_df.empty:
        feedback_df = feedback_df.rename(columns={'predicted_diet': 'recommended_diet'})
        feedback_df['satisfaction_level'] = feedback_df['feedback'].map({
            'positive': 3.0,
            'negative': 0.5
        })
        df['satisfaction_level'] = 1.5  # базова стойност за основните записи
        df = pd.concat([df, feedback_df], ignore_index=True)
    else:
        df['satisfaction_level'] = 1.0  # ако няма отзиви

    if df.empty:
        print("⚠️ Няма достатъчно данни.")
        return None, None

    # Категориално кодиране
    mappings = {}
    for col in ['sex', 'goal', 'activity', 'recommended_diet']:
        df[col] = df[col].astype(str)
        mappings[col] = {val: i for i, val in enumerate(df[col].unique())}
        df[col] = df[col].map(mappings[col])

    X = df[['age', 'weight', 'height', 'sex', 'goal', 'activity']]
    y = df['recommended_diet']
    weights = df['satisfaction_level']

    # Обучение с тегла
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y, sample_weight=weights)

    # Запис на модела и енкодерите
    joblib.dump(model, MODEL_PATH)
    joblib.dump(mappings, ENCODER_PATH)

    print("📊 Моделът е обучен с тегло на отзивите.")
    return model, mappings


def load_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        model = joblib.load(MODEL_PATH)
        encoders = joblib.load(ENCODER_PATH)
        return model, encoders
    return None, None
