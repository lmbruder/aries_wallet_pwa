from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from aries_wallet.models import AcapyWebhook, PresentProof, Connection
from django.contrib.auth.models import User
from aries_wallet import utils
from ..forms import PresentProofForm

def proof_requests(request):
    pending_reqs = PresentProof.objects.all().order_by('-updated_at').exclude(state = 'presentation_acked')[:5]
    presented_reqs = PresentProof.objects.all().order_by('-updated_at').filter(state = 'presentation_acked')
    return render(request, 'proof_requests.html', {'pending_reqs': pending_reqs, 'presented_reqs': presented_reqs})

def present_proof(request, presentation_exchange_id):
    proof_request = PresentProof.objects.get(presentation_exchange_id=presentation_exchange_id)
    if request.method == 'POST':
        form = PresentProofForm(data = request.POST, pres_ex_id = presentation_exchange_id)
        response = {}
        res_content = {}
        if form.is_valid():
            wallet_cred_id = str(form.cleaned_data['credential'].credential_id)
            count_attributes = len(proof_request.requested_attributes)
            count_predicates = len(proof_request.requested_predicates)

            # format attributes for acapy
            # individual attribute
            attrProp = {}
            attrProp['cred_id'] = wallet_cred_id
            attrProp['revealed'] = True

            # add necessary amount of attributes
            requested_attributes = {}
            for x in range(count_attributes):
                requested_attributes["additionalProp" + str(x + 1)] = attrProp
            
            # format predicates for acapy
            # individual predicate
            predProp = {}
            predProp['cred_id'] = wallet_cred_id

            # add necessary amount of predicates
            requested_predicates = {}
            for x in range(count_predicates):
                requested_predicates["additionalProp" + str(x + 1)] = predProp

            # add to json data
            data = {}
            data['requested_attributes'] = requested_attributes
            data['requested_predicates'] = requested_predicates
            data['self_attested_attributes'] = {}
            try: 
                # present proof to agent
                requests.post(url = 'http://localhost:10000/present-proof/records/' + presentation_exchange_id + '/send-presentation', json = data)
            
                res_content['message'] = 'Credential was presented.'
                response['success'] = True
                response['content'] = res_content
                return HttpResponse(json.dumps(response), content_type="application/json")

            except: 
                res_content['message'] = 'Something went wrong!'
                response['success'] = False
                response['content'] = res_content
                return HttpResponse(json.dumps(response), content_type="application/json")


        else: 
            res_content['message'] = json.loads(form.errors.as_json())['credential'][0]['message']
            response['success'] = False
            response['content'] = res_content
            return HttpResponse(json.dumps(response), content_type="application/json")

    else:
        form = PresentProofForm()

        return render(request, 'present_proof.html', {'form': form, 'pres_ex_id': presentation_exchange_id, 'did': proof_request.did})


# webhook
@csrf_exempt
def webhook_presentproof(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        AcapyWebhook(
            type=AcapyWebhook.Types.PRESENTPROOF,
            received_at=datetime.now(),
            content=response
        ).save()

        if 'state' in response.__str__():
            # check if presentation exchange id already in db, if it is update the entry
            exchange_id = response['presentation_exchange_id']
            presentation_request = response['presentation_request']
            try:
                pres = PresentProof.objects.get(presentation_exchange_id = exchange_id)
                pres.state = response['state']
                pres.save()
            # in any other case add a new db entry
            except PresentProof.DoesNotExist:
                PresentProof(
                    proof_request_name = presentation_request['name'],
                    did = response['presentation_request_dict']['@type'].split(';')[0],
                    presentation_exchange_id = response['presentation_exchange_id'],
                    created_at = response['created_at'],
                    updated_at = response['updated_at'],
                    state = response['state'],
                    presentation_request = presentation_request,
                    requested_attributes = presentation_request['requested_attributes'],
                    requested_predicates = presentation_request['requested_predicates'],
                    connection_id = response['connection_id']
                ).save()
                # send notification to user
                utils.send_notif(
                        sender = Connection.objects.get(connection_id=response['connection_id']), 
                        recipient = User.objects.get(username='User'), 
                        head = "New presentation request", 
                        body = "New presentation request."
                    )
        return HttpResponse("Webhook received!")