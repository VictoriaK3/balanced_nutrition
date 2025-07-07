from django.shortcuts import render
from .forms import PredictionForm
from .ml_model import load_model
from .ml_calorie_model import load_calorie_model
from .models import PredictionLog, UserDietHistory
import pandas as pd
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from diet_ai.management.commands.train_model import Command as TrainAllModels

def predict_diet_view(request):
    print("🔍 Страница за предсказване заредена")

    prediction = None
    calorie_result = None
    prediction_id = None
    
    model, encoders = load_model()
    calorie_model, calorie_features = load_calorie_model()

    if not model:
        print(" Моделът за режим не е наличен.")
        return render(request, 'diet_ai/predict.html', {
            'form': PredictionForm(),
            'error': 'Моделът за режим не е наличен. Моля, обучете го първо.'
        })

    if request.method == 'POST':
        print(" Получена е POST заявка")
        form = PredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(" Въведени данни:", data)

            try:
                user_input = pd.DataFrame([{
                    'age': data['age'],
                    'weight': data['weight'],
                    'height': data['height'],
                    'sex': encoders['sex'].get(data['sex'], -1),
                    'goal': encoders['goal'].get(data['goal'], -1),
                    'activity': encoders['activity'].get(data['activity'], -1),
                }])

                pred_code = model.predict(user_input)[0]
                pred_name = [k for k, v in encoders['recommended_diet'].items() if v == pred_code][0]
                prediction = pred_name
                print(f" Предсказан режим: {prediction}")

               
                if calorie_model:
                    print(" Зареждам калориен модел...")
                    encoded = pd.get_dummies(pd.DataFrame([data]))
                    for col in calorie_features:
                        if col not in encoded.columns:
                            encoded[col] = 0
                    encoded = encoded[calorie_features]
                    result = calorie_model.predict(encoded)[0]
                    calorie_result = {
                        'calories_deficit': int(result[0]),
                        'protein': int(result[1]),
                        'fat': int(result[2]),
                        'carbs': int(result[3]),
                    }
                    print(" Калории и макроси предсказани успешно.")

                # Запис в базата
                log = PredictionLog.objects.create(
                    age=data['age'],
                    weight=data['weight'],
                    height=data['height'],
                    sex=data['sex'],
                    goal=data['goal'],
                    activity=data['activity'],
                    predicted_diet=prediction,
                    feedback=None
                )
                prediction_id = log.id
                print(" Предсказанието е записано")
            except Exception as e:
                print(" Грешка при предсказване:", str(e))
    else:
        print(" Заредена е празна форма")
        form = PredictionForm()

    return render(request, 'diet_ai/predict.html', {
        'form': form,
        'prediction': prediction,
        'prediction_id': prediction_id,
        'calorie_result': calorie_result
    })



@require_POST
def feedback_view(request, prediction_id):
    feedback = request.POST.get("feedback") 

    try:
        log = PredictionLog.objects.get(id=prediction_id)
        log.feedback = feedback
        log.save()

       
        UserDietHistory.objects.create(
            age=log.age,
            weight=log.weight,
            height=log.height,
            sex=log.sex,
            goal=log.goal,
            activity=log.activity,
            recommended_diet=log.predicted_diet,
            initial_weight=log.weight,
            final_weight=log.weight,
            duration_days=0,
            waist_before=0,
            waist_after=0,
            hips_before=0,
            hips_after=0,
            chest_before=0,
            chest_after=0,
            food_likes="",
            food_dislikes="",
            diet_type_used=log.predicted_diet,
            satisfaction_level=5 if feedback == "positive" else 2,
            success="успешно" if feedback == "positive" else "неуспешно",
            estimated_lean_mass=0,
        )

        
        TrainAllModels().handle()

    except PredictionLog.DoesNotExist:
        pass

    return redirect("predict_diet")