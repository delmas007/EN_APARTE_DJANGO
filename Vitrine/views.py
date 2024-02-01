from random import sample

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from Model.models import Produit, Commande, Paniers


def panier(request):
    if not request.user.is_authenticated:
        return redirect('Accueil')
    # Récupérez le panier utilisateur avec confirmation_panier=False
    panier_utilisateur = Paniers.objects.filter(client=request.user, confirmation_panier=False).first()
    print(1)

    # Si le panier existe
    if panier_utilisateur:
        print(2)
        if request.method == 'POST':
            print(3)
            if 'mise_a_jour' in request.POST:
                for commande in panier_utilisateur.ordre.all():
                    nouvelle_quantite = request.POST.get(f'quantite-{commande.id}')
                    if nouvelle_quantite:
                        commande.quantite = nouvelle_quantite
                        commande.save()

            elif 'confirmer_commande' in request.POST:
                montant_total = panier_utilisateur.calculer_montant_total()
                panier_utilisateur.confirmation_panier = True
                panier_utilisateur.montant_total = montant_total
                panier_utilisateur.save()
                messages.success(request, 'Commande effecuer avec succès!')
                return redirect('vitrine:panier_confirme')
        print(4)
        return render(request, 'PanierContent.html', {'panier_utilisateur': panier_utilisateur})
    else:
        print(5)
        return render(request, 'PanierContent.html', {'panier_utilisateur': panier_utilisateur})


def supprimer_element_panier(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    commande.delete()
    return redirect('vitrine:panier_confirme')


def supprimer_panier(request):
    panier_utilisateur = Paniers.objects.filter(client=request.user, confirmation_panier=False).first()

    if panier_utilisateur:
        panier_utilisateur.supprimer_panier()

    return redirect('Accueil')


def liste_tous_produits(request):
    tous_les_produits = Produit.objects.all()

    context = {'tous_les_produits': tous_les_produits}
    return render(request, 'products.html', context)


@login_required
def commander_produit(request):
    produit_id = request.POST.get('produit_id')
    quantite = request.POST.get('quantite')
    quantit = int(quantite)
    produit = get_object_or_404(Produit, pk=produit_id)
    prix = produit.get_prix_reduit() * quantit
    # Créer la commande avec le produit et la quantité
    commande = Commande.objects.create(
        client=request.user,
        quantite=quantit,
        montant_total=prix,  # Utilisez la méthode get_prix_reduit
        confirmer=False,
        statut='En attente'
    )

    # Ajouter le produit à la commande
    commande.produits.add(produit)

    response_data = {'message': 'Commande enregistrée avec succès!'}

    return JsonResponse(response_data)


def Accueil(request):
    tous_les_produits = Produit.objects.all()

    if tous_les_produits:
        if len(tous_les_produits) >= 3:
            # Sélectionner trois éléments aléatoires
            produits_aleatoires = sample(list(tous_les_produits), 3)
        else:
            # Si la taille de la population est insuffisante, utilisez tous les produits disponibles
            produits_aleatoires = tous_les_produits
    else:
        # Si la taille de la population est insuffisante, utilisez tous les produits disponibles
        produits_aleatoires = tous_les_produits

    context = {'tous_les_produits': produits_aleatoires}
    return render(request, 'index.html', context)


def Contact(request):
    return render(request, 'contact.html')


def Faq(request):
    return render(request, 'faq.html')


def About(request):
    return render(request, 'about.html')


def produit_details(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id)

    context = {'produit': produit}
    return render(request, 'product-detail.html', context)


def ajouter_panier(request, produit_id):
    user = request.user
    product = get_object_or_404(Produit, pk=produit_id)

    # Vérifiez si l'utilisateur a un panier non confirmé
    panier_non_confirme = Paniers.objects.filter(client=user, confirmation_panier=False).first()

    if panier_non_confirme:
        panier = panier_non_confirme
        print("Utilisation du panier non confirmé existant.")
    else:
        # Création d'un nouveau panier avec confirmation_panier=False
        panier = Paniers.objects.create(client=user)
        print("Création d'un nouveau panier avec confirmation_panier=False.")

    # Création d'une nouvelle commande
    commande, cree = Commande.objects.get_or_create(client=user, produits=product,
                                                    client__paniers__confirmation_panier=False, paniers=panier)

    if cree:
        if panier.ordre.exists():
            panier.ordre.add(commande)
            panier.save()
            print("Nouvel ordre créé.")
        else:
            panier.ordre.add(commande)
            panier.save()
            print("Commande ajoutée à l'ordre existant.")
        print("Nouveau panier et commande créés.")
    else:
        commande.quantite += 1
        commande.save()
        print("Quantité de commande mise à jour.")

    return redirect(reverse("vitrine:Produit_details", kwargs={"produit_id": produit_id}))


def EnvoyerFormulaire(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire

        nom = request.POST.get('name')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')  # Récupérer l'email soumis
        objet = request.POST.get('Objet')
        message = request.POST.get('message')
        contenu_message = f"De : {nom} {prenom}\nAdresse e-mail : {email}\n\n{message}"
        send_mail(
            subject=objet,
            message=contenu_message,
            from_email='votre_adresse_email@gmail.com',
            recipient_list=['alidouwrm@gmail.com'],
            fail_silently=False,
        )
        messages.success(request, 'Formulaire soumis avec succès!')
        return redirect('vitrine:Contact')


def Acces_interdit(request):
    return render(request, "Acces_interdit.html")
