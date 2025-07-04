# Import des classes nécessaires
from django import forms
from .models import Livre, CD, DVD, JeuDePlateau, Media, Emprunt, Membre
from django.contrib.contenttypes.models import ContentType

# Formulaire basé sur le modèle Membre, utilisé pour créer ou modifier un membre
class MembreForm(forms.ModelForm):
    class Meta:
        model = Membre  # Modèle lié au formulaire
        fields = ['prenom', 'nom', 'email']  # Champs affichés et modifiables dans le formulaire


# Formulaire pour gérer les emprunts (association entre un membre et un média)
class EmpruntForm(forms.ModelForm):
    # Liste des types de médias possibles à emprunter
    TYPE_CHOICES = [
        ('CD', 'CD'),
        ('DVD', 'DVD'),
        ('LIVRE', 'Livre'),
        ('JEU', 'Jeu de plateau'),  # Ici, l'option est présente mais sera interdite plus bas
    ]

    type_media = forms.ChoiceField(choices=TYPE_CHOICES, label='Type de média')  # Sélection du type
    media = forms.ModelChoiceField(queryset=CD.objects.none(), label='Média')  # Sélection dynamique du média

    class Meta:
        model = Emprunt  # Modèle Emprunt lié
        fields = ['membre', 'type_media', 'date_retour']  # Champs affichés dans le formulaire

    # Surcharge du constructeur pour ajuster dynamiquement les médias disponibles
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si l'utilisateur a sélectionné un type de média (soumis via POST)
        if 'type_media' in self.data:
            type_media = self.data.get('type_media')

            # On filtre dynamiquement les objets disponibles selon le type sélectionné
            if type_media == 'CD':
                self.fields['media'].queryset = CD.objects.filter(disponible=True)
            elif type_media == 'DVD':
                self.fields['media'].queryset = DVD.objects.filter(disponible=True)
            elif type_media == 'LIVRE':
                self.fields['media'].queryset = Livre.objects.filter(disponible=True)
            elif type_media == 'JEU':
                self.fields['media'].queryset = CD.objects.none()  # Aucun jeu disponible à l’emprunt
            else:
                self.fields['media'].queryset = CD.objects.none()
        else:
            self.fields['media'].queryset = CD.objects.none()  # Par défaut, rien n’est affiché

    # Validation personnalisée
    def clean(self):
        cleaned_data = super().clean()
        type_media = cleaned_data.get('type_media')
        media = cleaned_data.get('media')

        # Interdiction de l’emprunt de jeux de plateau
        if type_media == 'JEU':
            raise forms.ValidationError("Impossible d'emprunter un jeu de plateau.")

        # Si aucun média sélectionné alors que requis
        if not media:
            self.add_error('media', "Ce champ est obligatoire.")

        return cleaned_data

    # Sauvegarde personnalisée de l’emprunt
    def save(self, commit=True):
        emprunt = super().save(commit=False)  # Création de l’objet sans commit immédiat
        type_media = self.cleaned_data['type_media']
        media_obj = self.cleaned_data['media']

        # Association générique avec le bon type d’objet via ContentType
        emprunt.content_type = ContentType.objects.get_for_model(media_obj.__class__)
        emprunt.object_id = media_obj.pk

        if commit:
            emprunt.save()  # Sauvegarde effective en base
        return emprunt


# Formulaire de base pour le modèle Media
class MediaForm(forms.ModelForm):
    disponible = forms.BooleanField(required=False)  # Champ booléen optionnel
    class Meta:
        model = Media
        fields = '__all__'  # Inclut tous les champs du modèle Media


# Formulaire de filtrage ou de recherche de média
class MediaSelectorForm(forms.Form):
    # Liste des types de médias proposés
    TYPE_CHOICES = [
        ('CD', 'CD'),
        ('DVD', 'DVD'),
        ('LIVRE', 'Livre'),
        ('JEU', 'Jeu de plateau'),
    ]

    type_media = forms.ChoiceField(choices=TYPE_CHOICES, label='Type de média')  # Choix du type
    name = forms.CharField(label='Nom')  # Nom du média (recherche ou saisie)
    disponible = forms.BooleanField(label='Disponible', required=False, initial=True)  # Filtre par disponibilité
