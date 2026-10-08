from django.urls import path
from . import views

app_name = 'diagnostico_financiero'

urlpatterns = [
    path('', views.ingreso_datos, name='ingreso_datos'),
    path('dashboard/<int:evaluacion_id>/', views.dashboard, name='dashboard'),
]
