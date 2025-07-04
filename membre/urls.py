from django.urls import path
from . import views
from .views import liste_media

app_name = 'membre'

urlpatterns = [
path('', liste_media, name='liste_media'),
  #  path('medias/', views.liste_media, name='liste_media'),
]
