from django.urls import include, path
import notifications.urls
from .views import connection_views, credential_views, index_views, proof_views

urlpatterns = [
    # urls related to connections
    path('connections', connection_views.connections, name='connections'),
    path('receive_invitation', connection_views.receive_invitation, name='receive invitation'),
    path('accept_connection/<connection_id>', connection_views.accept_connection, name='accepted connection'),

    # urls related to credentials
    path('credentials', credential_views.credentials, name='credentials'),
    path('request_credential/<credential_exchange_id>', credential_views.request_credential, name="request credential"),
    path('problem_report/<credential_exchange_id>', credential_views.problem_report, name="problem report"),

    # urls related to proof requests
    path('proof_requests', proof_views.proof_requests, name='proof requests'),
    path('present_proof/<presentation_exchange_id>', proof_views.present_proof, name="present proof"),

    # webhooks
    path('webhook/topic/connections/', connection_views.webhook_connections),
    path('webhook/topic/basicmessages/', index_views.webhook_basicmessages),
    path('webhook/topic/issue_credential/', credential_views.webhook_issuecredential),
    path('webhook/topic/revocation-notification/', credential_views.webhook_revocation),
    path('webhook/topic/present_proof/', proof_views.webhook_presentproof),

    # notifications
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),

    # index page
    path('', index_views.index, name='index')
]
