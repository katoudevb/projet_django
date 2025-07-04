from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),


    path('membre/', include(('membre.urls', 'membre'), namespace='membre')),

    path('bibliothecaire/', include(('bibliothecaire.urls', 'bibliothecaire'), namespace='bibliothecaire')),
    path('', RedirectView.as_view(url='/bibliothecaire/')),  # redirige la racine vers /bibliothecaire/
]