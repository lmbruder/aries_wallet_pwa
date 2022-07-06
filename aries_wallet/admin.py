from django.contrib import admin
from .models import Connection, AcapyWebhook, Credential, PresentProof

admin.site.register(Connection)
admin.site.register(Credential)
admin.site.register(PresentProof)
admin.site.register(AcapyWebhook)
