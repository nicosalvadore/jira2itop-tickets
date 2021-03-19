import requests
import json
import base64

# Updating an Itop ticket / UserRequest object.
def update(key, fields):
    json_data = {
        'operation': 'core/update',
        'class': "UserRequest",
        'key': key,
        'fields': fields,
        'comment': "update ticket",
        'output_fields': 'id',
    }
    return request(json_data)

# Creating an Itop ticket / UserRequest object.
def create(org_id, title, description, start_date):
    json_data = {
        'operation': 'core/create',
        'class': "UserRequest",
        'fields': {
                'title': title,
                'description': description,
                'org_id': org_id,
                'start_date': start_date,
        },
        'comment': "import ticket from Jira",
        'output_fields': 'id',
    }
    return request(json_data)

# Importing an attachment to an Itop ticket / UserRequest object.
def attachment(id, name, mimetype, data):
    json_data = {
        'operation': 'core/create',
        'comment': "automatic import of attachment",
        'class': "Attachment",
        'fields': {
            'item_class': "UserRequest",
            'item_id': id,
            'contents' : {
                'data': base64.b64encode(data).decode('utf-8'),
                'filename': name,
                'mimetype': mimetype
            },
        },
    }
    return request(json_data)

# Sending an HTTP request to Itop REST API
def request(json_data):
    url = "https://itop.example.com/webservices/rest.php?"
    user = "user-api"
    password = "itop-api-secret"

    return requests.post(url + "version=1.3", data={'auth_user': user, 'auth_pwd': password, 'json_data': json.dumps(json_data)})