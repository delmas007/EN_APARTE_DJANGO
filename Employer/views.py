from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from Employer.forms import ConfirmationReservationForm
from Model.models import Rendez_vous
from Model.views import evaluation_email
from xhtml2pdf import pisa


@login_required
def reservations_confirmer(request):
    if not request.user.roles or request.user.roles.role != 'EMPLOYER':
        return redirect('vitrine:Acces_interdit')
    rendez_vous = Rendez_vous.objects.filter(confirmation=True, en_attente=False, fin=False, employer=request.user.id)
    reservations_en_attentes = Rendez_vous.objects.filter(en_attente=True, confirmation=False,
                                                          preference_employer=None).count()
    reservations_en_attentes_moi = Rendez_vous.objects.filter(en_attente=True, confirmation=False,
                                                              preference_employer=request.user).count()
    reservations_confirmerr = Rendez_vous.objects.filter(en_attente=False, confirmation=True, fin=False,
                                                         employer=request.user.id).count()
    # Calculez le nombre total de réservations
    total_reservations = reservations_en_attentes + reservations_confirmerr + reservations_en_attentes_moi

    # Renvoyez ces valeurs dans le contexte pour les utiliser dans le template
    context = {
        'reservations_en_attente': reservations_en_attentes,
        'reservations_en_attentes_moi': reservations_en_attentes_moi,
        'reservations_confirmerr': reservations_confirmerr,
        'total_reservations': total_reservations,
        'rendez_vous': rendez_vous
    }
    return render(request, 'indexe2.html', context)


@login_required
def debut_rendez_vous(request, rendez_vous_id):
    rdv = get_object_or_404(Rendez_vous, id=rendez_vous_id)

    # Mettre à jour le champ 'debut' à True
    rdv.debut = True
    rdv.save()

    return redirect('employer:reservation_confirmer')


@login_required
def fin_rendez_vous(request, rendez_vous_id, email, uuid):
    rdv = get_object_or_404(Rendez_vous, id=rendez_vous_id)
    rdv.fin = True
    rdv.save()

    evaluation_email(request, mail=email, rendez_vous_uuid=uuid)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_rendez_vous_{rdv.id}.pdf"'
    template_path = 'facture_template.html'
    template = get_template(template_path)
    html = template.render({'rendez_vous': rdv})
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    return response


@login_required
def reservations_en_attente(request):
    if not request.user.roles or request.user.roles.role != 'EMPLOYER':
        return redirect('vitrine:Acces_interdit')

    reservations = Rendez_vous.objects.filter(en_attente=True, confirmation=False, preference_employer=None)

    reservations_en_attentes = Rendez_vous.objects.filter(en_attente=True, confirmation=False,
                                                          preference_employer=None).count()
    reservations_en_attentes_moi = Rendez_vous.objects.filter(en_attente=True, confirmation=False,
                                                              preference_employer=request.user).count()
    reservations_confirmerr = Rendez_vous.objects.filter(en_attente=False, confirmation=True, fin=False,
                                                         employer=request.user.id).count()
    # Calculez le nombre total de réservations
    total_reservations = reservations_en_attentes + reservations_confirmerr + reservations_en_attentes_moi

    # Renvoyez ces valeurs dans le contexte pour les utiliser dans le template
    context = {
        'reservations_en_attente': reservations_en_attentes,
        'reservations_en_attentes_moi': reservations_en_attentes_moi,
        'reservations_confirmerr': reservations_confirmerr,
        'total_reservations': total_reservations,
        'reservations': reservations,
    }

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
            send_confirmation_email(reservation.client.email, reservation, request.user)

            # Ajoutez d'autres logiques pour le refus de la réservation si nécessaire
            # ...

            return redirect('employer:reservation')
    else:
        form = ConfirmationReservationForm()
        context['form'] = form

    return render(request, 'indexe.html', context)


@login_required
def reservations_en_attente_moi(request):
    if not request.user.roles or request.user.roles.role != 'EMPLOYER':
        return redirect('vitrine:Acces_interdit')

    reservations = Rendez_vous.objects.filter(en_attente=True, confirmation=False, preference_employer=request.user)

    reservations_en_attentes = Rendez_vous.objects.filter(en_attente=True, confirmation=False,
                                                          preference_employer=None).count()
    reservations_en_attentes_moi = Rendez_vous.objects.filter(en_attente=True, confirmation=False,
                                                              preference_employer=request.user).count()
    reservations_confirmerr = Rendez_vous.objects.filter(en_attente=False, confirmation=True, fin=False,
                                                         employer=request.user.id).count()
    # Calculez le nombre total de réservations
    total_reservations = reservations_en_attentes + reservations_confirmerr + reservations_en_attentes_moi

    # Renvoyez ces valeurs dans le contexte pour les utiliser dans le template
    context = {
        'reservations_en_attente': reservations_en_attentes,
        'reservations_en_attentes_moi': reservations_en_attentes_moi,
        'reservations_confirmerr': reservations_confirmerr,
        'total_reservations': total_reservations,
        'reservations': reservations,
    }

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
            send_confirmation_email(reservation.client.email, reservation, request.user)

            # Ajoutez d'autres logiques pour le refus de la réservation si nécessaire
            # ...

            return redirect('employer:reservation')
    else:
        form = ConfirmationReservationForm()
        context['form'] = form

    return render(request, 'indexe_me.html', context)


def send_confirmation_email(client_email, reservation, employer):
    subject = 'Confirmation de rendez-vous EN APARTE'
    message = render_to_string('emaile.html', {'reservation': reservation, 'employer': employer})
    plain_message = strip_tags(message)
    recipient_list = [client_email]

    email = EmailMultiAlternatives(subject=subject, body=plain_message, to=recipient_list)
    email.attach_alternative(message, "text/html")
    email.send()
