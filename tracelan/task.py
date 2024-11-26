from celery import shared_task
from django.core.mail import send_mail, send_mass_mail
from .models import Event, EventInvite


@shared_task
def envoyer_email_invitation(event_id, subject, message_template):
    """
    Envoie des emails aux invités d'un événement.
    """
    event = Event.objects.get(id=event_id)
    invites = EventInvite.objects.filter(event=event)
    emails = []

    for invite in invites:
        invite_object = invite.get_invite()
        email = getattr(invite_object, 'email', None)  # Vérifie si l'entité possède un champ email
        if email:
            message = message_template.format(
                name=str(invite_object),
                event=event.name,
                date=event.start_date.strftime('%d %B %Y, %H:%M'),
                location=event.location or "Lieu non spécifié",
            )
            emails.append((subject, message, 'admin@votredomaine.com', [email]))

    # Envoi des emails par lot
    return send_mass_mail(emails)


@shared_task
def envoyer_email_rappel(event_id):
    """
    Envoie des emails de rappel aux invités d'un événement.
    """
    event = Event.objects.get(id=event_id)
    subject = f"Rappel: Événement {event.name}"
    message_template = """
    Bonjour {name},

    Ceci est un rappel pour l'événement auquel vous êtes invité :
    - Événement : {event}
    - Date : {date}
    - Lieu : {location}

    Nous vous attendons !

    Cordialement,
    L'équipe
    """
    return envoyer_email_invitation(event_id, subject, message_template)
