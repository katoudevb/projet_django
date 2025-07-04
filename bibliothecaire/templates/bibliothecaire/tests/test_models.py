from django.test import TestCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Membre, CD, DVD, Livre, Emprunt, JeuDePlateau

class MembreModelTest(TestCase):
    def test_str(self):
        membre = Membre.objects.create(prenom="Jean", nom="Dupont", email="jean.dupont@example.com")
        self.assertEqual(str(membre), "Jean Dupont")

class MediaEmpruntTest(TestCase):
    def setUp(self):
        self.cd = CD.objects.create(name="Best Of", artiste="Artiste", disponible=True)
        self.jeu = JeuDePlateau.objects.create(name="Monopoly", createur="Hasbro", disponible=True)

    def test_emprunter_media_disponible(self):
        self.assertTrue(self.cd.emprunter())
        self.cd.refresh_from_db()
        self.assertFalse(self.cd.disponible)

    def test_emprunter_jeu_de_plateau_inempruntable(self):
        self.assertFalse(self.jeu.emprunter())
        self.jeu.refresh_from_db()
        self.assertTrue(self.jeu.disponible)

class EmpruntModelTest(TestCase):
    def setUp(self):
        self.membre = Membre.objects.create(prenom="Anna", nom="Smith", email="anna.smith@example.com")
        self.livre = Livre.objects.create(name="1984", auteur="Orwell", disponible=True)
        self.content_type = ContentType.objects.get_for_model(Livre)

    def test_creation_emprunt_date_retour_prevue(self):
        emprunt = Emprunt.objects.create(
            membre=self.membre,
            content_type=self.content_type,
            object_id=self.livre.id,
            date_emprunt=timezone.now().date()
        )
        expected_date = emprunt.date_emprunt + timezone.timedelta(days=7)
        self.assertEqual(emprunt.date_retour_prevue, expected_date)

    def test_emprunt_media_incorrect(self):
        emprunt = Emprunt(membre=self.membre)
        emprunt.content_type = ContentType.objects.get_for_model(JeuDePlateau)
        emprunt.object_id = 9999  # Id qui n'existe pas
        # L'accès au media doit être None (aucun objet correspondant)
        self.assertIsNone(emprunt.media)