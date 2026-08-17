import logging
from django.conf import settings
from .models import Notification

logger = logging.getLogger(__name__)


def _send_sms(telephone, message):
    if not telephone:
        logger.warning('Aucun numéro de téléphone fourni pour le SMS')
        return False

    provider = getattr(settings, 'SMS_PROVIDER', 'console').lower()
    if provider == 'twilio':
        try:
            from twilio.rest import Client
        except ImportError:
            logger.warning('Twilio non installé, SMS non envoyé')
            return False

        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)
        if not all([account_sid, auth_token, from_number]):
            logger.warning('Twilio mal configuré, SMS non envoyé')
            return False

        client = Client(account_sid, auth_token)
        try:
            client.messages.create(body=message, from_=from_number, to=telephone)
            return True
        except Exception:
            logger.exception('Erreur lors de l’envoi du SMS Twilio')
            return False

    if provider == 'console':
        logger.info('SMS simulé vers %s : %s', telephone, message)
        return True

    logger.warning('Fournisseur SMS inconnu (%s), SMS non envoyé', provider)
    return False


def _creer_notification(utilisateur, commande, titre, message, type_='commande'):
    telephone = getattr(utilisateur, 'phone', None) or getattr(utilisateur, 'telephone', None)
    sms_envoye = _send_sms(telephone, message)
    notification = Notification.objects.create(
        utilisateur=utilisateur,
        commande=commande,
        titre=titre,
        message=message,
        type=type_,
        sms_envoye=sms_envoye
    )
    return notification
