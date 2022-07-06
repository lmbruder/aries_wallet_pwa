from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from aries_wallet.models import AcapyWebhook, Credential, Connection
from django.contrib.auth.models import User
from aries_wallet import utils
from ..forms import CredentialProblemReportForm

# CREDENTIALS
def credentials(request):
    all_creds = Credential.objects.order_by('-updated_at')
    return render(request, 'credentials.html', {'all_creds': all_creds})

def request_credential(request, credential_exchange_id):
    response = {}
    res_content = {}
    try: 
        # request credential from agent
        requests.post(url = 'http://localhost:10000/issue-credential/records/' + credential_exchange_id + '/send-request')

        res_content['message'] = 'Requested credential with credential exchange id: ' + credential_exchange_id + '.'
        response['success'] = True
        response['content'] = res_content
        return HttpResponse(json.dumps(response), content_type="application/json")

    except:
        res_content['message'] = 'Something went wrong!'
        response['success'] = False
        response['content'] = res_content
        return HttpResponse(json.dumps(response), content_type="application/json")

def problem_report(request, credential_exchange_id):
    if request.method == 'POST':
        form = CredentialProblemReportForm(request.POST)
        response = {}
        res_content = {}
        # check whether form data is valid
        if form.is_valid():
            text = form.cleaned_data['description']
            description = {
                "description": text
            }
            try: 
                # post problem report description to agent
                requests.post(url = 'http://localhost:10000/issue-credential/records/' + credential_exchange_id + '/problem-report', json = description)

                res_content['message'] = "Your problem relating to exchange id %s was reported with the following description: %s" %(credential_exchange_id, text)
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

    else:
        form = CredentialProblemReportForm()

    return render(request, 'problem_report.html', {'form': form, 'cred_ex_id': credential_exchange_id})

# webhook
@csrf_exempt
def webhook_issuecredential(request):    
    if request.method == 'POST':
        response = json.loads(request.body)
        AcapyWebhook(
            type=AcapyWebhook.Types.ISSUECREDENTIAL,
            received_at=datetime.now(),
            content=response
        ).save()

        if response.get('state'):
            # check if credential exchange id already in db, if it is update entry
            exchange_id = response['credential_exchange_id']
            credential_proposal_dict = response['credential_proposal_dict']

            try:
                cred = Credential.objects.get(credential_exchange_id = exchange_id)
                cred.state = response['state']
                cred.save()

                # store credential in agent wallet if credential is in state credential_received
                if str(response.get('state')) == 'credential_received':
                    # notification
                    utils.send_notif(
                        sender = Connection.objects.get(connection_id=cred.connection_id), 
                        recipient = User.objects.get(username='User'), 
                        head = "New credential", 
                        body = cred.schema_name + " was received."
                    )
                    countCreds = Credential.objects.all().count()
                    body = {
                        "credential_id": str(countCreds)
                    }
                    r = requests.post(url = 'http://localhost:10000/issue-credential/records/' + exchange_id + '/store', json = body)
                    if r.status_code != 200:
                        return HttpResponseBadRequest()
                    else:
                        cred.credential_id = countCreds
                        cred.save()

            # in any other case add a new db entry
            except Credential.DoesNotExist:
                # split schema id
                split_schema_id = response['schema_id'].split(":")
                
                Credential(
                    state = response['state'],
                    credential_proposal_dict = credential_proposal_dict,
                    attributes = credential_proposal_dict['credential_proposal']['attributes'],
                    updated_at = response['updated_at'],
                    connection_id = response['connection_id'],
                    credential_definition_id = response['credential_definition_id'],
                    schema_id = response['schema_id'],
                    credential_exchange_id = exchange_id,
                    created_at = response['created_at'],
                    thread_id = response['thread_id'],
                    schema_name = split_schema_id[2],
                    schema_version = split_schema_id[3]
                ).save()

                utils.send_notif(
                    sender = Connection.objects.get(connection_id=response['connection_id']), 
                    recipient = User.objects.get(username='User'), 
                    head = "New credential proposal", 
                    body = "New credential proposal"
                )
        return HttpResponse("Webhook received!")

@csrf_exempt
def webhook_revocation(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        AcapyWebhook(
            type=AcapyWebhook.Types.REVOCATIONNOTIFICATION,
            received_at=datetime.now(),
            content=response
        ).save()

        # get credential if it exists, otherwise raise 404
        cred = get_object_or_404(Credential, thread_id = response['thread_id'])

        if response.get('comment'):
            message = cred.schema_name + " was revoked with message: " + response['comment']
        else:
            message = cred.schema_name + " was revoked."

        # send notification
        utils.send_notif(
            sender = Connection.objects.get(connection_id=cred.connection_id), 
            recipient = User.objects.get(username='User'), 
            head = "Revocation", 
            body = message
        )
        return HttpResponse("Webhook received!")
    