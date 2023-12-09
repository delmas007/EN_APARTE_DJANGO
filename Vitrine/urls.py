from django.urls import path

from .views import Accueil, Contact, Faq,Produit,About,Produitdetails

app_name = 'vitrine'

urlpatterns = [

    path('Contact/', Contact, name='Contact'),
    path('Faq/', Faq, name='Faq'),
    path('Accueil/', Accueil, name='Accueil'),
    path('A_propos/', About, name='About'),
    path('Produit/', Produit, name='Produit'),
    path('Produit_details/', Produitdetails, name='Produit details'),
]
