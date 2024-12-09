from django.urls import path
from . import views

app_name = 'luckyApp'

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.history_list, name='history'),
    path('predictions/', views.prediction_list, name='predictions'),
    path('api/random/', views.generate_random, name='generate_random'),
    path('api/predict/', views.generate_prediction, name='generate_prediction'),
    path('api/save-prediction/', views.save_prediction, name='save_prediction'),
    path('api/latest-predictions/', views.get_latest_predictions, name='get_latest_predictions'),
    path('api/update/', views.update_lottery_data, name='update_data'),
] 