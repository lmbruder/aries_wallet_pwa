from django.db import models

class Connection(models.Model):
    class Roles(models.TextChoices):
        NULL = 'null'
        INVITEE = 'invitee'
        REQUESTER = 'requester'
        INVITER = 'inviter'
        RESPONDER = 'responder'

    class States(models.TextChoices):
        START = 'start'
        INVITATION = 'invitation'
        REQUEST = 'request'
        RESPONSE = 'response'
        COMPLETED = 'completed'
        ACTIVE = 'active'
        ABANDONED = 'abandoned'

    class Accept(models.TextChoices):
        MANUAL = 'manual'
        AUTO = 'auto'

    connection_id = models.CharField(max_length=100, primary_key=True)
    their_label = models.CharField(max_length=100, default='User')
    created_at = models.DateTimeField(default='2022-04-01T13:06:15.833333Z')
    updated_at = models.DateTimeField(default='2022-04-01T13:06:15.833333Z')
    their_role = models.CharField(choices=Roles.choices, max_length=10, default=Roles.NULL)
    state = models.CharField(choices=States.choices, max_length=10, default=States.START)
    accept = models.CharField(choices=Accept.choices, max_length=6, default=Accept.MANUAL)

    def __str__(self):
        return self.connection_id

class Credential(models.Model):
    class States(models.TextChoices):
        PROPOSAL_SENT = 'proposal_sent'
        PROPOSAL_RECEIVED = 'proposal_received'
        OFFER_SENT = 'offer_sent'
        OFFER_RECEIVED = 'offer_received'
        REQUEST_SENT = 'request_sent'
        REQUEST_RECEIVED = 'request_received'
        ISSUED = 'issued'
        CREDENTIAL_RECEIVED = 'credential_received'
        CREDENTIAL_ACKED = 'credential_acked'

    state = models.CharField(choices=States.choices, max_length=30)
    credential_proposal_dict = models.JSONField()
    attributes = models.JSONField(default=dict)
    updated_at = models.DateTimeField()
    connection_id = models.CharField(max_length=100)
    credential_definition_id = models.CharField(max_length=100)
    schema_id = models.CharField(max_length=100)
    credential_exchange_id = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    schema_name = models.CharField(max_length=30, default="null")
    schema_version = models.CharField(max_length=4, default="1.0")
    credential_id = models.IntegerField(default=0)
    thread_id = models.CharField(max_length=100, default="null")

    def __str__(self):
        return self.credential_exchange_id

class PresentProof(models.Model):
    class States(models.TextChoices):
        REQUEST_RECEIVED = 'request_received'
        PROPOSAL_SENT = 'proposal_sent'
        PRESENTATION_SENT = 'presentation_sent'
        PRESENTATION_ACKED = 'presentation_acked'
        REJECT_SENT = 'reject_sent'
        DONE = 'done'

    proof_request_name = models.CharField(max_length=50)
    did = models.CharField(max_length=50, default='did:sov')
    presentation_exchange_id = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    state = models.CharField(choices=States.choices, max_length=30)
    presentation_request = models.JSONField(default=dict)
    requested_attributes = models.JSONField(default=dict)
    requested_predicates = models.JSONField(default=dict)
    connection_id = models.CharField(max_length=100, default="null")

    def __str__(self):
        return self.presentation_exchange_id

class AcapyWebhook(models.Model):
    class Types(models.TextChoices):
        NULL = 'null'
        CONNECTIONS = 'connections'
        BASICMESSAGES = 'basicmessages'
        FORWARD = 'forward'
        ISSUECREDENTIAL = 'issue_credential'
        PRESENTPROOF = 'present_proof'
        REVOCATIONNOTIFICATION = 'revocation_notification'
    type = models.CharField(choices=Types.choices, max_length=30, default=Types.NULL)
    received_at = models.DateTimeField(primary_key=True)
    content = models.JSONField(default=None, null=True)

    def __str__(self):
        return str(self.received_at).partition(".")[0]