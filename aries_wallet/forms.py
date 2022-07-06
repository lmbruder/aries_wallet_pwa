from django import forms
import logging
from aries_wallet.models import Credential, PresentProof

logger = logging.getLogger(__name__)


class ConnectionInvitationForm(forms.Form):
    invitation_url = forms.CharField(label='Invitation URL', max_length=1000)

    def clean(self):
        # check if invitation url is in the right format (needs to include the identifier c_i)
        invitation_url = self.cleaned_data['invitation_url']
        if "c_i=" not in invitation_url:
            raise forms.ValidationError("URL is not in valid format.")
        return invitation_url

class CredentialProblemReportForm(forms.Form):
    description = forms.CharField(label='Description', max_length=1000, widget=forms.Textarea)

class PresentProofForm(forms.Form):
    credential = forms.ModelChoiceField(queryset=Credential.objects.all().order_by('-updated_at').filter(state='credential_acked'), required=True)

    def __init__(self, *args, **kwargs):
        self.pres_ex_id = kwargs.pop('pres_ex_id', None)
        super(PresentProofForm, self).__init__(*args, **kwargs)

    def clean_credential(self):
        proof_request = PresentProof.objects.get(presentation_exchange_id = self.pres_ex_id)
        cred = self.cleaned_data['credential']
        # verify that the attributes of the credential match the requested ones in the proof request
        for attr in cred.attributes:
            if attr['name'] not in proof_request.requested_attributes.__str__() and attr['name'] not in proof_request.requested_predicates.__str__():
                raise forms.ValidationError("Attributes or predicates do not match")
        return cred