from django.test import TestCase, Client
from django.urls import reverse
from bibliothecaire.models import CD, DVD, Livre, JeuDePlateau

from django.test import TestCase
from django.urls import reverse
from bibliothecaire.models import CD, DVD, Livre, JeuDePlateau

class MembreViewsTests(TestCase):

    def setUp(self):
        # Création des objets médias
        self.cd = CD.objects.create(name="CD Test", artiste="Artiste Test", disponible=True)
        self.dvd = DVD.objects.create(name="DVD Test", realisateur="Réalisateur Test", disponible=True)
        self.livre = Livre.objects.create(name="Livre Test", auteur="Auteur Test", disponible=True)
        self.jeu = JeuDePlateau.objects.create(name="Jeu Test", createur="Créateur Test", disponible=True)

    def test_liste_media_view(self):
        # Appel GET à la vue liste_media (adapter le nom de l’URL selon ta config)
        response = self.client.get(reverse('membre:liste_media'))  # Remplace 'membre:liste_media' par ton nom d'URL exact

        self.assertEqual(response.status_code, 200)

        # Vérifie que les objets sont dans le contexte
        self.assertIn(self.cd, response.context['cds'])
        self.assertIn(self.dvd, response.context['dvds'])
        self.assertIn(self.livre, response.context['livres'])
        self.assertIn(self.jeu, response.context['jeux'])

        # Vérifie que les noms apparaissent dans le contenu HTML
        self.assertContains(response, self.cd.name)
        self.assertContains(response, self.dvd.name)
        self.assertContains(response, self.livre.name)
        self.assertContains(response, self.jeu.name)
