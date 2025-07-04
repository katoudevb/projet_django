from django.urls import path
from . import views

app_name = 'bibliothecaire'

urlpatterns = [
    # MembreEmprunteur
    path('membres/', views.liste_membres, name='liste_membres'),
    path('membres/creer/', views.creer_membre, name='creer_membre'),
    path('membres/modifier/<int:id>/', views.modifier_membre, name='modifier_membre'),
    path('membres/supprimer/<int:id>/', views.supprimer_membre, name='supprimer_membre'),

    # Media
    path('media/', views.liste_media, name='liste_media'),
    path('media/supprimer/<str:type_media>/<int:media_id>/', views.supprimer_media, name='supprimer_media'),
    path('media/ajouter/', views.ajouter_media, name='ajouter_media'),
    path('medias-disponibles/', views.medias_disponibles, name='medias_disponibles'),

    # Emprunt
    path('emprunts/creer/', views.creer_emprunt, name='creer_emprunt'),
    path('emprunts/rentrer/<int:id>/', views.rentrer_emprunt, name='rentrer_emprunt'),
    path('emprunts/liste', views.liste_emprunts, name='liste_emprunts'),


    path('', views.accueil, name='accueil'),
]

