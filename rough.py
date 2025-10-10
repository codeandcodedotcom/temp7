# save as test_token.py and run: python test_token.py
import requests, os
TENANT="<TENANT_ID>"
CID="<CLIENT_ID>"
SECRET="<CLIENT_SECRET>"
SCOPE="https://databricks.azure.net/.default"
r = requests.post(f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token",
                  data={"client_id":CID,"client_secret":SECRET,"grant_type":"client_credentials","scope":SCOPE},
                  timeout=15)
print("STATUS:", r.status_code)
print("BODY:", r.text)
