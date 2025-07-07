from django.urls import path
from .views import predict_diet_view
from .views import feedback_view

urlpatterns = [
    path('predict/', predict_diet_view, name='predict_diet'),
    path("feedback/<int:prediction_id>/", feedback_view, name="feedback"),
]

