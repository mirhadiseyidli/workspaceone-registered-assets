### To get started first install Okta Python SDK
```
python3 -m pip install okta
```

### Create a config.json file and edit it based on your credentials
```
{
    "WORKSPACEONE_URL": "https://<org-url>.awmdm.com/API/system/users/enrolleddevices/search",
    "CLIENT_ID": "<client-id>",
    "CLIENT_SECRET": "<client-secret>",
    "API_TOKEN": "<api-toke>",
    "TOKEN_URL": "https://na.uemauth.vmwservices.com/connect/token", // Make sure to use correct region
    "DEVICE_BY_ID_URL": "https://<org-url>.awmdm.com/API/mdm/devices/",
    "okta_org_url": "https://<org-name>.okta.com/",
    "okta_token": "<api-token>"
}
```

Run the command:
```
python3 get_device_list.py
```
