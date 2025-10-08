from azure.identity import ClientSecretCredential
import requests

credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Get token for Azure Management API
token = credential.get_token("https://management.azure.com/.default")

# List resources in subscription (works with Reader role)
subscription_id = "your-subscription-id"
url = f"https://management.azure.com/subscriptions/{subscription_id}/resources?api-version=2021-04-01"

headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    print("✓ Service Principal authentication WORKS!")
    print(f"Found {len(response.json().get('value', []))} resources")
else:
    print(f"Response: {response.text[:300]}")
