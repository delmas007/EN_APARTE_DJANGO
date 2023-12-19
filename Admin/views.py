from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import DateField
from django.db.models.functions import Cast
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from Admin.forms import UserRegistrationForme, ServiceForm, ServiceForme, HoraireForm
from Employer.forms import ConfirmationReservationForm
from Model.models import Rendez_vous, Roles, Utilisateur, Produit, Paniers, ProduitLog, Service, horaire


@login_required
def filtrer_Commande(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    # Obtenez la liste de tous les rendez-vous
    tous_Paniers = Paniers.objects.filter(reception_commande=True)

    # Gestion des filtres
    date_filtre = request.GET.get('date', '')
    vendeur_filtre = request.GET.get('vendeur', '')
    client_filtre = request.GET.get('client', '')

    # Appliquer les filtres
    if date_filtre:
        tous_Paniers = tous_Paniers.annotate(
            date_only=Cast('date_reception_commande', output_field=DateField())
        ).filter(date_only=date_filtre)
    if vendeur_filtre:
        tous_Paniers = tous_Paniers.filter(employer__nom__icontains=vendeur_filtre)
    if client_filtre:
        tous_Paniers = tous_Paniers.filter(client__nom__icontains=client_filtre)

    context = {
        'tous_Paniers': tous_Paniers,
        'date_filtre': date_filtre,
        'vendeur_filtre': vendeur_filtre,
        'client_filtre': client_filtre,
    }
    return render(request, 't_D.html', context)


@login_required
def produit_log_list(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    # Récupération des données depuis le modèle ProduitLog
    produit_logs = ProduitLog.objects.all()

    # Filtrage en fonction de la saisie de l'utilisateur
    action_filter = request.GET.get('action', None)
    user_filter = request.GET.get('user', None)
    date_filter = request.GET.get('date', None)

    if action_filter:
        produit_logs = produit_logs.filter(action=action_filter)
    if user_filter:
        produit_logs = produit_logs.filter(utilisateur__username=user_filter)
    if date_filter:
        produit_logs = produit_logs.filter(timestamp__date=date_filter)

    context = {
        'produit_logs': produit_logs,
    }
    return render(request, 'H_P.html', context)


@login_required
def liste_produits_D(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    produits = Produit.objects.all()
    return render(request, 'list_PO_D.html', {'produits': produits})


@login_required
def liste_paniers_confirmes_D(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    paniers_confirmes = Paniers.objects.filter(confirmation_panier=True, confirmation_employer=False)

    context = {'paniers_confirmes': paniers_confirmes}
    return render(request, 'panier_C_D.html', context)


@login_required
def liste_paniers_traitements_D(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    paniers_traitements = Paniers.objects.filter(confirmation_employer=True, reception_commande=False)

    context = {'paniers_traitements': paniers_traitements}
    return render(request, 'panier_T_D.html', context)


@login_required
def liste_commandes_receptionnees_D(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    commandes_receptionnees = Paniers.objects.filter(
        reception_commande=True,
        date_reception_commande__date=date.today()
    )

    context = {'commandes_receptionnees': commandes_receptionnees}
    return render(request, 'panier_E_D.html', context)


@csrf_protect
@login_required
def inscription_D(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    context = {}
    if request.method == 'POST':
        form = UserRegistrationForme(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Employer ajouter avec succès !')
        else:
            context['errors'] = form.errors

    form = UserRegistrationForme()
    context['form'] = form
    return render(request, 'employer_D.html', context=context)


# Create your views here.

@login_required
def employer_compte(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')

    # Inclure à la fois les rôles "EMPLOYER" et "VENDEUR"
    utilisateurs_employers = Utilisateur.objects.filter(roles__role__in=[Roles.EMPLOYER, Roles.VENDEUR])

    return render(request, 'employer_ac.html', {'employers': utilisateurs_employers})


@login_required
def active_emp(request, employer_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = True
    employer.save()

    return redirect('admins:Compte_employer')


@login_required
def desactive_amp(request, employer_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    employer = get_object_or_404(Utilisateur, id=employer_id)
    employer.is_active = False
    employer.save()

    return redirect('admins:Compte_employer')


@login_required
def filtrer_rendez_vous(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    # Obtenez la liste de tous les rendez-vous
    tous_les_rendez_vous = Rendez_vous.objects.filter(fin=True)

    # Gestion des filtres
    date_filtre = request.GET.get('date', '')
    employer_filtre = request.GET.get('employer', '')
    client_filtre = request.GET.get('client', '')

    # Appliquer les filtres
    if date_filtre:
        tous_les_rendez_vous = tous_les_rendez_vous.filter(date_rendez_vous=date_filtre)
    if employer_filtre:
        tous_les_rendez_vous = tous_les_rendez_vous.filter(employer__nom__icontains=employer_filtre)
    if client_filtre:
        tous_les_rendez_vous = tous_les_rendez_vous.filter(client__nom__icontains=client_filtre)

    context = {
        'tous_les_rendez_vous': tous_les_rendez_vous,
        'date_filtre': date_filtre,
        'employer_filtre': employer_filtre,
        'client_filtre': client_filtre,
    }
    return render(request, 'indexe3_D.html', context)


@login_required
def reservations_en_attente_D(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')

    reservations = Rendez_vous.objects.filter(en_attente=True, confirmation=False)

    if request.method == 'POST':
        form = ConfirmationReservationForm(request.POST)

        if form.is_valid():
            reservation_id = form.cleaned_data['reservation_id']
            confirmation = form.cleaned_data['confirmation']

            reservation = get_object_or_404(Rendez_vous, id=reservation_id)

            # Mettez à jour le champ de confirmation
            reservation.confirmation = True

            # Si la réservation est confirmée, enregistrez l'id de l'utilisateur connecté comme client
            if reservation.confirmation:
                reservation.employer = request.user
                reservation.en_attente = False

            reservation.save()

            # Ajoutez d'autres logiques pour le refus de la réservation si nécessaire
            # ...

            return redirect('employer:reservation')
    else:
        form = ConfirmationReservationForm()

    return render(request, 'indexe_D.html', {'reservations': reservations, 'form': form})


def reservations_confirmer_D(request):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    rendez_vous = Rendez_vous.objects.filter(confirmation=True, en_attente=False, fin=False, debut=False)
    return render(request, 'indexe2_D.html', {'reservations': rendez_vous})


def rendez_vous_aujourdhui(request):
    # Obtenez la date actuelle
    today = timezone.now().date()

    # Filtrez les rendez-vous d'aujourd'hui
    rendez_vous_aujourdhui = Rendez_vous.objects.filter(
        date_rendez_vous=today
    )

    # Calculez l'état de chaque rendez-vous
    for rendez_vous in rendez_vous_aujourdhui:
        if rendez_vous.en_attente:
            rendez_vous.etat = "Reservation pas encore accepter"
        elif rendez_vous.debut == True and rendez_vous.fin == False:
            rendez_vous.etat = "en cours..."
        elif rendez_vous.fin:
            rendez_vous.etat = "Terminé"
        elif not rendez_vous.debut:
            rendez_vous.etat = "Pas encore commencé"

    context = {'rendez_vous_aujourdhui': rendez_vous_aujourdhui}
    return render(request, 'rendez_vous_auj.html', context)


def ajout_service(request):
    context = {}
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service ajouter avec succès !')
            # return redirect('admins:ajout_service')  # Rediriger vers la liste des services ou une autre page
        else:
            context['errors'] = form.errors

    form = ServiceForm()
    context['form'] = form
    return render(request, 'service_A.html', context)


def liste_services(request):
    services = Service.objects.all()
    context = {'services': services}
    return render(request, 'sup.html', context)


def supprimer_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    service.delete()
    return redirect('admins:liste_services')


def liste_services_mode(request):
    services = Service.objects.all()
    context = {'services': services}
    return render(request, 'mod_list.html', context)


@login_required
def modifier_service(request, service_id):
    if not request.user.roles or request.user.roles.role != 'ADMIN':
        return redirect('Accueil')
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':

        form = ServiceForme(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service modifier avec succès !')
    else:
        form = ServiceForme(instance=service)
    context = {
        'form': form, 'service': service
    }

    return render(request, 'mod.html', context)


def ajout_horaire(request):
    context = {}
    if request.method == 'POST':
        form = HoraireForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'horaire ajouter avec succès !')
            # return redirect('admins:ajout_service')  # Rediriger vers la liste des services ou une autre page
        else:
            context['errors'] = form.errors

    form = HoraireForm()
    context['form'] = form
    return render(request, 'horaire_A.html', context)


def liste_horaire(request):
    horair = horaire.objects.all()
    context = {'horaires': horair}
    return render(request, 'sup_h.html', context)


def supprimer_horaire(request, horaire_id):
    horair = get_object_or_404(horaire, pk=horaire_id)
    horair.delete()
    return redirect('admins:liste_horaire')
