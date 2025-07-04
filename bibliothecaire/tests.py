from django.test import TestCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Membre, CD, DVD, Livre, Emprunt, JeuDePlateau

#Test Models
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

#Test Forms
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from .forms import EmpruntForm
from .models import Membre, CD, DVD, Livre, Emprunt

class EmpruntFormTest(TestCase):

    def setUp(self):
        # Création d'un membre
        self.membre = Membre.objects.create(prenom='Jean', nom='Dupont', email='jean@example.com')

        # Création de médias disponibles
        self.cd = CD.objects.create(name='Album Test', artiste='Artiste Test', disponible=True)
        self.dvd = DVD.objects.create(name='Film Test', realisateur='Réalisateur Test', disponible=True)
        self.livre = Livre.objects.create(name='Livre Test', auteur='Auteur Test', disponible=True)

    def test_form_valid_cd(self):
        form_data = {
            'membre': self.membre.id,
            'type_media': 'CD',
            'media': self.cd.id,
        }
        form = EmpruntForm(data=form_data)
        self.assertTrue(form.is_valid())
        emprunt = form.save()
        self.assertEqual(emprunt.membre, self.membre)
        self.assertEqual(emprunt.media, self.cd)

    def test_form_valid_dvd(self):
        form_data = {
            'membre': self.membre.id,
            'type_media': 'DVD',
            'media': self.dvd.id,
        }
        form = EmpruntForm(data=form_data)
        self.assertTrue(form.is_valid())
        emprunt = form.save()
        self.assertEqual(emprunt.media, self.dvd)

    def test_form_valid_livre(self):
        form_data = {
            'membre': self.membre.id,
            'type_media': 'LIVRE',
            'media': self.livre.id,
        }
        form = EmpruntForm(data=form_data)
        self.assertTrue(form.is_valid())
        emprunt = form.save()
        self.assertEqual(emprunt.media, self.livre)

    def test_form_invalid_media_for_type(self):
        # Essayer de sélectionner un DVD avec type_media CD (invalide)
        form_data = {
            'membre': self.membre.id,
            'type_media': 'CD',
            'media': self.dvd.id,  # DVD id, mais type_media CD
        }
        form = EmpruntForm(data=form_data)
        self.assertFalse(form.is_valid())

#Test views
from django.test import TestCase, Client
from django.urls import reverse
from bibliothecaire.models import Membre, CD, Emprunt
from bibliothecaire.forms import MembreForm, EmpruntForm

class MembreViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.membre = Membre.objects.create(prenom="Jean", nom="Dupont", email="jean@example.com")

    def test_liste_membres_GET(self):
        url = reverse('bibliothecaire:liste_membres')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jean")

    def test_creer_membre_POST_valid(self):
        url = reverse('bibliothecaire:creer_membre')
        data = {'prenom': 'Alice', 'nom': 'Martin', 'email': 'alice@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirection attendue
        self.assertTrue(Membre.objects.filter(email='alice@example.com').exists())

    def test_modifier_membre_POST(self):
        url = reverse('bibliothecaire:modifier_membre', args=[self.membre.id])
        data = {'prenom': 'Jean', 'nom': 'Dupont', 'email': 'jean.dupont@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.membre.refresh_from_db()
        self.assertEqual(self.membre.email, 'jean.dupont@example.com')

    def test_supprimer_membre_POST(self):
        url = reverse('bibliothecaire:supprimer_membre', args=[self.membre.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Membre.objects.filter(id=self.membre.id).exists())

class MediaViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.cd = CD.objects.create(name="CD Test", disponible=True, artiste="Artiste Test")

    def test_liste_media_GET(self):
        url = reverse('bibliothecaire:liste_media')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.cd.name)

    def test_ajouter_media_POST(self):
        url = reverse('bibliothecaire:ajouter_media')
        data = {'type_media': 'CD', 'name': 'Nouveau CD', 'disponible': True}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CD.objects.filter(name='Nouveau CD').exists())

class EmpruntViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.membre = Membre.objects.create(prenom="Paul", nom="Durand", email="paul@example.com")
        self.cd = CD.objects.create(name="CD Emprunt", disponible=True, artiste="Artiste Emprunt")

    def test_creer_emprunt_GET(self):
        url = reverse('bibliothecaire:creer_emprunt')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Type de média')

    def test_creer_emprunt_POST_success(self):
        url = reverse('bibliothecaire:creer_emprunt')
        data = {
            'membre': self.membre.id,
            'type_media': 'CD',
            'media': self.cd.id,
            'date_retour': '',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.cd.refresh_from_db()
        self.assertFalse(self.cd.disponible)
        self.assertTrue(Emprunt.objects.filter(membre=self.membre).exists())

    def test_creer_emprunt_POST_jeu_interdit(self):
        # Création d'un jeu de plateau non empruntable
        from bibliothecaire.models import JeuDePlateau
        jeu = JeuDePlateau.objects.create(name="Jeu interdit", disponible=True, createur="Créateur")

        url = reverse('bibliothecaire:creer_emprunt')
        data = {
            'membre': self.membre.id,
            'type_media': 'JEU',
            'media': jeu.id,
            'date_retour': '',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Impossible d&#x27;emprunter un jeu de plateau.", response.content.decode('utf-8'))
