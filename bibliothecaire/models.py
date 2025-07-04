from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# 🔹 Modèle représentant un membre inscrit à la bibliothèque
class Membre(models.Model):
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"  # Affichage lisible du membre dans l’admin ou les logs

# 🔹 Classe mère Media – base commune pour CD, DVD, Livre
class Media(models.Model):
    name = models.CharField(max_length=100)
    disponible = models.BooleanField(default=True)

    def emprunter(self):
        if self.disponible:
            self.disponible = False
            self.save()
            return True
        return False

    def __str__(self):
        return self.name  # Représentation textuelle du média

# 🔹 Spécialisation : CD hérite de Media
class CD(Media):
    artiste = models.CharField(max_length=100)  # Ajout du champ spécifique : artiste du CD

# 🔹 Spécialisation : DVD hérite de Media
class DVD(Media):
    realisateur = models.CharField(max_length=100)  # Champ spécifique : réalisateur du DVD

# 🔹 Spécialisation : Livre hérite de Media
class Livre(Media):
    auteur = models.CharField(max_length=100)  # Champ spécifique : auteur du livre

# 🔹 Modèle représentant un emprunt d’un média par un membre
class Emprunt(models.Model):
    membre = models.ForeignKey('Membre', on_delete=models.CASCADE)
    # Lien vers le membre emprunteur ; suppression en cascade si le membre est supprimé

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    media = GenericForeignKey('content_type', 'object_id')
    # Ces trois champs permettent de lier dynamiquement l'emprunt à un objet de type CD, DVD ou Livre

    date_emprunt = models.DateField(auto_now_add=True)
    date_retour = models.DateField(null=True, blank=True)
    date_retour_prevue = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Définit automatiquement la date de retour prévue si non précisée
        if not self.date_retour_prevue:
            self.date_retour_prevue = (self.date_emprunt or timezone.now().date()) + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

# 🔹 Modèle spécifique pour les jeux de plateau (non empruntables)
class JeuDePlateau(models.Model):
    name = models.CharField(max_length=100)
    disponible = models.BooleanField(default=True)

    def emprunter(self):
        return False  # Surcharge explicite pour interdire les emprunts

    def __str__(self):
        return self.name  # Représentation textuelle du jeu
