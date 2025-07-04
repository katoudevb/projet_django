from django.shortcuts import render, get_object_or_404, redirect
from .models import Membre, Emprunt, CD, DVD, Livre, JeuDePlateau, Media
from .forms import MembreForm, EmpruntForm, MediaSelectorForm
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse


# Liste tous les membres inscrits
def liste_membres(request):
    membres = Membre.objects.all()  # Requête brute, sans filtre ni pagination
    return render(request, 'bibliothecaire/membre/liste.html', {
        'membres': membres,
        'app_name': 'bibliothecaire',
    })


# Création d’un membre via formulaire
def creer_membre(request):
    if request.method == 'POST':
        form = MembreForm(request.POST)
        if form.is_valid():
            form.save()  # Création persistée en base
            return redirect('bibliothecaire:liste_membres')  # PRG pattern respecté
    else:
        form = MembreForm()  # Formulaire vierge pour GET
    return render(request, 'bibliothecaire/membre/formulaire.html', {'form': form})


# Mise à jour d’un membre existant
def modifier_membre(request, id):
    membre = get_object_or_404(Membre, id=id)  # Sécurisation par 404 si absent
    if request.method == 'POST':
        form = MembreForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()  # Update en base
            return redirect('bibliothecaire:liste_membres')
    else:
        form = MembreForm(instance=membre)  # Form pré-rempli
    return render(request, 'bibliothecaire/membre/formulaire.html', {'form': form})


# Suppression sécurisée d’un membre
def supprimer_membre(request, id):
    membre = get_object_or_404(Membre, id=id)
    if request.method == 'POST':
        membre.delete()  # Suppression cascade potentielle
        return redirect('bibliothecaire:liste_membres')
    return render(request, 'bibliothecaire/membre/confirmer_delete.html', {'membre': membre})


# Liste des médias par type
def liste_media(request):
    cds = CD.objects.all()
    dvds = DVD.objects.all()
    livres = Livre.objects.all()
    jeux = JeuDePlateau.objects.all()

    return render(request, 'bibliothecaire/media/liste.html', {
        'cds': cds,
        'dvds': dvds,
        'livres': livres,
        'jeux': jeux,
    })


# Ajout d’un média polymorphe via un formulaire générique
def ajouter_media(request):
    if request.method == 'POST':
        form = MediaSelectorForm(request.POST)
        if form.is_valid():
            type_media = form.cleaned_data['type_media']
            name = form.cleaned_data['name']
            disponible = form.cleaned_data['disponible']

            # Création selon type, pas d’héritage polymorphe exploité ici
            if type_media == 'CD':
                CD.objects.create(name=name, disponible=disponible)
            elif type_media == 'DVD':
                DVD.objects.create(name=name, disponible=disponible)
            elif type_media == 'LIVRE':
                Livre.objects.create(name=name, disponible=disponible)
            elif type_media == 'JEU':
                JeuDePlateau.objects.create(name=name, disponible=disponible)

            return redirect('bibliothecaire:liste_media')
    else:
        form = MediaSelectorForm()

    return render(request, 'bibliothecaire/media/ajouter.html', {'form': form})


# Retourne en JSON la liste des médias disponibles d’un type donné (pour AJAX)
def medias_disponibles(request):
    type_media = request.GET.get('type_media')

    if type_media == 'CD':
        medias = CD.objects.filter(disponible=True)
    elif type_media == 'DVD':
        medias = DVD.objects.filter(disponible=True)
    elif type_media == 'LIVRE':
        medias = Livre.objects.filter(disponible=True)
    elif type_media == 'JEU':
        medias = JeuDePlateau.objects.filter(disponible=True)
    else:
        medias = []

    data = [{'id': media.id, 'name': media.name} for media in medias]
    return JsonResponse(data, safe=False)


# Suppression média avec gestion dynamique du modèle
def supprimer_media(request, type_media, media_id):
    model_map = {
        'CD': CD,
        'DVD': DVD,
        'LIVRE': Livre,
        'JEU': JeuDePlateau,
    }
    Model = model_map.get(type_media.upper())
    if not Model:
        return redirect('bibliothecaire:liste_media')

    media = get_object_or_404(Model, id=media_id)

    if request.method == 'POST':
        media.delete()
        return redirect('bibliothecaire:liste_media')

    return render(request, 'bibliothecaire/media/confirmer_delete.html', {'media': media, 'type_media': type_media})


# Création d’un emprunt avec règles métier multiples et validation
def creer_emprunt(request):
    if request.method == 'POST':
        form = EmpruntForm(request.POST)
        if form.is_valid():
            emprunt = form.save(commit=False)
            membre = emprunt.membre
            media = emprunt.media

            # Interdiction d’emprunter un jeu de plateau
            if isinstance(media, JeuDePlateau):
                form.add_error(None, "Impossible d'emprunter un jeu de plateau.")
                return render(request, 'bibliothecaire/emprunt/creer.html', {'form': form})

            # Limite à 3 emprunts actifs
            emprunts_actifs = Emprunt.objects.filter(membre=membre, date_retour__isnull=True).count()
            if emprunts_actifs >= 3:
                form.add_error(None, "Ce membre a déjà 3 emprunts en cours.")
                return render(request, 'bibliothecaire/emprunt/creer.html', {'form': form})

            # Vérifie si le membre a un emprunt en retard (>7 jours)
            retards = Emprunt.objects.filter(
                membre=membre,
                date_retour__isnull=True,
                date_emprunt__lt=timezone.now().date() - timezone.timedelta(days=7)
            )
            if retards.exists():
                form.add_error(None, "Ce membre a un emprunt en retard, il ne peut pas emprunter.")
                return render(request, 'bibliothecaire/emprunt/creer.html', {'form': form})

            # Passage du média en indisponible si disponible
            if media.disponible:
                media.disponible = False
                media.save()

                emprunt.date_emprunt = timezone.now().date()
                emprunt.save()
                return redirect('bibliothecaire:liste_emprunts')
            else:
                form.add_error(None, "Ce média n'est pas disponible.")
    else:
        form = EmpruntForm()
    return render(request, 'bibliothecaire/emprunt/creer.html', {'form': form})


# Liste de tous les emprunts (manque pagination)
def liste_emprunts(request):
    emprunts = Emprunt.objects.all()
    return render(request, 'bibliothecaire/emprunt/liste.html', {'emprunts': emprunts})


# Enregistrement du retour d’un emprunt
def rentrer_emprunt(request, id):
    emprunt = get_object_or_404(Emprunt, id=id)

    if emprunt.date_retour:
        # Empêche la saisie multiple de retour
        return render(request, 'bibliothecaire/emprunt/erreur.html', {'message': 'Cet emprunt a déjà été rentré.'})

    if request.method == 'POST':
        form = EmpruntForm(request.POST, instance=emprunt)
        if form.is_valid():
            with transaction.atomic():  # Assure atomicité des opérations
                emprunt = form.save(commit=False)

                if not emprunt.date_retour:
                    form.add_error('date_retour', "La date de retour doit être renseignée.")
                    return render(request, 'bibliothecaire/emprunt/rentrer.html', {'form': form})

                # Remise à disposition du média lié
                emprunt.media.disponible = True
                emprunt.media.save()
                emprunt.save()

            return redirect('liste_emprunts')
    else:
        form = EmpruntForm(instance=emprunt)

    return render(request, 'bibliothecaire/emprunt/rentrer.html', {'form': form})


# Vue accueil simple
def accueil(request):
    return render(request, 'bibliothecaire/base.html')
