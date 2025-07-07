import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from diet_ai.models import UserDietHistory

CALORIE_MODEL_PATH = 'diet_ai/ml_models/calorie_model.joblib'
CALORIE_FEATURES_PATH = 'diet_ai/ml_models/calorie_features.joblib'

def train_calorie_model():
    qs = UserDietHistory.objects.all().values()
    df = pd.DataFrame(qs)

    df = df.dropna(subset=['calories_deficit', 'macro_protein', 'macro_fat', 'macro_carbs'])

    features = ['age', 'weight', 'height', 'sex', 'goal', 'activity']
    targets = ['calories_deficit', 'macro_protein', 'macro_fat', 'macro_carbs']

    df_encoded = pd.get_dummies(df[features])
    X = df_encoded
    y = df[targets]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump((model, X.columns.tolist()), CALORIE_MODEL_PATH)
    joblib.dump(X.columns.tolist(), CALORIE_FEATURES_PATH)

    print(" Калориен модел обучен успешно.")
    return model, X.columns.tolist()

def load_calorie_model():
    try:
        model, features = joblib.load(CALORIE_MODEL_PATH)
        return model, features
    except:
        return None, None
