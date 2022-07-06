from notifications.signals import notify
from webpush import send_user_notification

# send notifications internally and externally via webpush
def send_notif(sender, recipient, head, body):
    # send internal notification
    notify.send(sender=sender, recipient=recipient, verb=body)

    # send push (external) notification
    payload = {"head": head, "body": body, "icon": "/aries_wallet/static/images/aries.png"}
    send_user_notification(user=recipient, payload=payload, ttl=1000)
