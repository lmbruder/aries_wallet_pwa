from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
import base64
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from aries_wallet.models import AcapyWebhook, Connection
from ..forms import ConnectionInvitationForm

# CONNECTIONS
def connections(request):
    # get all connections from the database and order them newest to latest
    all_cons = Connection.objects.order_by('-updated_at')
    # respond to the request with the connections rendered inside the connections.html 
    return render(request, 'connections.html', {'all_cons': all_cons})


def receive_invitation(request):
    # POST request
    if request.method == 'POST':
        # populate form with data
        form = ConnectionInvitationForm(request.POST)
        response = {}
        res_content = {}
        # check whether it's valid:
        if form.is_valid():
            # get base64 encoded string
            base64encoded = form.cleaned_data.partition("=")[2]
            padding = len(base64encoded) % 4
            # remove padding if necessary
            if padding:
                base64encoded += '='* (4 - padding)
            try:
                # decode base64
                decodedInvitation = str(base64.b64decode(base64encoded),  "utf-8")

                # post JSON to agent
                r = requests.post(url = 'http://localhost:10000/connections/receive-invitation', json = decodedInvitation)

                response = r.json()

                #save to db
                Connection(
                    connection_id = response['connection_id'],
                    their_role = response['their_role'], 
                    state = response['state'],
                    accept = response['accept'],
                    created_at = response['created_at'],
                    updated_at = response['updated_at'],
                    their_label = response['their_label']
                ).save()

                res_content['message'] = "Success! New connection with: "+ response['connection_id']
                response['success'] = True
                response['content'] = res_content
                
                return HttpResponse(json.dumps(response), content_type="application/json")

            except:
                res_content['message'] = 'Something went wrong!'
                response['success'] = False
                response['content'] = res_content
                return HttpResponse(json.dumps(response), content_type="application/json")

        else: 
            res_content['message'] = 'Something went wrong!'
            response['success'] = False
            response['content'] = res_content
            return HttpResponse(json.dumps(response), content_type="application/json")

    # GET request
    else:
        # initiate ConnectionInvitationForm
        form = ConnectionInvitationForm()
        # pass form to receive_invitation.html and render 
        return render(request, 'receive_invitation.html', {'form': form})

def accept_connection(request, connection_id):
    response = {}
    res_content = {}
    try: 
        # accept connection
        r = requests.post(url = 'http://localhost:10000/connections/' + connection_id + '/accept-invitation')
        
        response = r.json()
        # update db
        conn = Connection.objects.get(connection_id=connection_id)
        conn.updated_at = response['updated_at']
        conn.state = response['state']
        conn.save()

        res_content['message'] = 'Accepted connection with id: ' + response['connection_id'] + '.'
        response['success'] = True
        response['content'] = res_content
        return HttpResponse(json.dumps(response), content_type="application/json")

    except:
        res_content['message'] = 'Something went wrong!'
        response['success'] = False
        response['content'] = res_content
        return HttpResponse(json.dumps(response), content_type="application/json")            

# webhook
@csrf_exempt
def webhook_connections(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        AcapyWebhook(
            type=AcapyWebhook.Types.CONNECTIONS,
            received_at=datetime.now(),
            content=response
        ).save()
        # if response has state parameter add connection to database
        if response.get('state'):
            connection_id = response['connection_id']
            conn = Connection.objects.get(connection_id=connection_id)
            conn.updated_at = response['updated_at']
            conn.state = response['state']
            conn.save()
            
            # trust ping to confirm active connection
            if str(response.get('state')) == 'response':
                requests.post(url = 'http://localhost:10000/connections/' + connection_id + '/send-ping', json={})
        return HttpResponse("Webhook received!")
