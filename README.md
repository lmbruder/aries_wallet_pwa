# aries_wallet_pwa

## Set-Up
Install [Docker](https://docs.docker.com/get-docker/).
Clone the following github repositories into the docker folder:

- von-network: \
git clone https://github.com/bcgov/von-network.git

- indy-tails-server: \
git clone https://github.com/bcgov/indy-tails-server.git

All docker related files are located in the docker folder.
Start all docker containers with the `startup.sh` script (or `first_startup.sh` if the containers have not been built yet).
The script will start the von-network, indy-tails-server and two ACA-Py containers (one running on port 10000 and one on 10010).
The von-network interface is accessible through port 9000. The indy-tails-server runs on 4044.

Install all relevant Python packages in a virtual environment:
```
python3 -m venv venv_name
source venv_name/bin/activate
pip install -r requirements.txt
```

## Running the application

Run `./manage.py runserver`. The application is now available on port 8000.

To test all PWA features by accessing the application via HTTPS install [ngrok](https://ngrok.com/).
After installing ngrok run `ngrok http 8000` in a terminal. ngrok now displays a HTTPS domain that serves as a tunnel to localhost:8000.
Do not forget to add the ngrok domain to `ALLOWED_HOSTS` in `settings.py`.

## Accounts
To test all functionalities login with: \
Username: User \
Password: password@user \
\
To access the admin panel login with the following credentials: \
Username: admin \
Password: django2022


## Quick guide to interaction between two ACA-Pys
### Create and assign public DID
To create your first connection invitation you need to create and publish a DID from ACA-Py 10010 (which serves as your example company/institution in this case). Do that by opening up `localhost:10010` in your browser. Create a local DID with the `/wallet/did/create` endpoint. Go to `localhost:9000` and register the newly created DID in the tab `Register from DID`. Next assign the public DID from the ACA-Py API by calling `/wallet/did/public` endpoint via `POST`.

Now you are ready to set up your first invitation URL that can be later passed to the Django wallet.

### Base64 encoded connection invitation
With your DID you can now create a connection invitation that the second ACA-Py is able to receive. For it to understand who it is connecting to, we need to create a JSON with the relevant information in the correct format.

In the API interface we can see that `/connections/receive-invitation` takes a JSON argument that looks like this
```
{
  "@id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "did": "WgWxqztrNooG92RXvxSTWv",
  "imageUrl": "http://192.168.56.101/img/logo.jpg",
  "label": "Bob",
  "recipientKeys": [
    "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  ],
  "routingKeys": [
    "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
  ],
  "serviceEndpoint": "http://192.168.56.101:8020"
}
```

However, some of these parameters are optional. In fact, we can create a connection invitation with a JSON looking like the following: 
```
{
  "@type": "did:sov:{DID};spec/connections/1.0/invitation",
  "@id": "1",
  "label": "University Musterstadt",
  "did": "did:sov:{DID}"
}
```
After substituting {DID} with our recently created public DID, we need to encode the JSON (without whitespaces!) with base64. (for example with this command in the command line: `echo -n 'my-string' | base64`). By convention our base64 string needs to be preceeded by the following string `c_i=` as defined in the [Hyperledger Aries Documentation](https://github.com/hyperledger/aries-rfcs/blob/a1e4f2fbbca325bc1e27869cc949e691442c5b3c/features/0160-connection-protocol/README.md). c_i stands for connection invitation.

Now you can paste this string into the django wallet application to receive a new connection and accept it via the accept button.

### Issuing a credential
To issue a credential to our new connection we first need to create a schema with the attributes that we want to issue for the connection. This is possible through a `POST` to `/schemas`. In this JSON we need to define which attributes the schema should entail, its name and its version.
```
{
  "attributes": [
    "First name",
    "Last name",
    "Age"
  ],
  "schema_name": "Student Card",
  "schema_version": "1.0"
}
```
With the schema_id we receive as a response we can now create a credential with a `POST` to `/credential-definitions`:
```
{
  "revocation_registry_size": 1000,
  "schema_id": "MtAVd7cvWtLh2AMKEgaAru:2:Student Card:1.0",
  "support_revocation": true,
  "tag": "default"
}
```
When revocation is set to true it will later be possible to revoke a credential.

Now pass the following type of JSON to the `/issue_credential/send-offer` endpoint. We can get the `connection_id` by calling the `\connections` endpoint.
```
{
  "auto_issue": true,
  "auto_remove": false,
  "comment": "string",
  "connection_id": "c2565e44-ea28-4b68-8eac-a05284261c6b",
  "cred_def_id": "HPER9G8WkSQ9XLQwyZqW4v:3:CL:106:default",
  "credential_preview": {
    "@type": "issue-credential/1.0/credential-preview",
    "attributes": [
      {
        "name": "First name",
        "value": "Max"
      },
      {
      
        "name": "Last name",
        "value": "Mustermann"
      },
      {
        "name": "Age",
        "value": "25"
      }
    ]
  },
  "trace": true
}
```
It is now possible to accept or decline the credential in the application.

### Revoking a credential
To revoke a credential we need to get the credential exchange id as well as the thread id related to the credential exchange. These can for example be found in the response to the `/issue-credential/send-offer` call.
```
{
  "connection_id": "e46a26f6-5a30-43fd-abee-a36fff7f1e63",
  "cred_ex_id": "4ccd4f1a-c7cf-452b-b38b-b37bb8d51b84",
  "notify": true,
  "publish": true,
  "thread_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

### Requesting a proof presentation

To request a proof presentation, we need to post to the `/present-proof/send-request` endpoint.
The JSON should look like the following:
```
{
  "comment": "string",
  "connection_id": "e46a26f6-5a30-43fd-abee-a36fff7f1e63",
  "proof_request": {
    "name": "Above 20",
    "non_revoked": {
      "to": 1655295165
    },
    "nonce": "1",
    "requested_attributes": {
      "additionalProp1": {
        "name": "First name"
      },
      "additionalProp2": {
        "name": "Last name"
      }
    },
    "requested_predicates": {
       "additionalProp1": {
        "name": "Age",
        "non_revoked": {
        "to": 1655295165
        },
        "p_type": ">",
        "p_value": 20
      }
    },
    "version": "1.0"
  },
  "trace": true
}
```
