from django.shortcuts import render
from bibliothecaire.models import CD, DVD, Livre, JeuDePlateau


def liste_media(request):
    cds = CD.objects.all()
    dvds = DVD.objects.all()
    livres = Livre.objects.all()
    jeux = JeuDePlateau.objects.all()

    context = {
        'cds': cds,
        'dvds': dvds,
        'livres': livres,
        'jeux': jeux,
    }
    return render(request, 'membre/liste_media.html', context)
