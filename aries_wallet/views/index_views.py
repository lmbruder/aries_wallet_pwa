from datetime import datetime
import json
from django.http import HttpResponse
from django.shortcuts import render
from aries_wallet.models import AcapyWebhook, Connection, Credential
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from aries_wallet import utils


def index(request):
    all_cons = Connection.objects.order_by('-updated_at')[:3]
    all_creds = Credential.objects.order_by('-updated_at')[:3]
    return render(request, 'index.html', {'all_cons': all_cons, 'all_creds': all_creds})

# webhooks
@csrf_exempt
def webhook_basicmessages(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        AcapyWebhook(
            type=AcapyWebhook.Types.BASICMESSAGES,
            received_at=datetime.now(),
            content=response
        ).save()

        sender = Connection.objects.get(connection_id=response['connection_id'])
        utils.send_notif(
            sender = sender, 
            recipient = User.objects.get(username='User'), 
            head = "Message from " + sender.their_label, 
            body = "Message: " + response['content']
        )
        return HttpResponse("Webhook received!")
