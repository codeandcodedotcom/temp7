from azure.identity import ClientSecretCredential
import requests

credential = ClientSecretCredential(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Get token
token = credential.get_token("https://cognitiveservices.azure.com/.default")

base_url = "https://azureai-nprd-weu-openai-ai27.openai.azure.com"

# Try different API paths
test_endpoints = [
    # Control plane API (list deployments)
    f"{base_url}/openai/deployments?api-version=2024-06-01",
    f"{base_url}/openai/deployments?api-version=2023-05-15",
    f"{base_url}/openai/deployments?api-version=2024-10-21",
    
    # Data plane API (list models)
    f"{base_url}/openai/models?api-version=2024-06-01",
    f"{base_url}/openai/models?api-version=2023-05-15",
    
    # Simple root check
    f"{base_url}/"
]

headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}

print(f"Token scope used: https://cognitiveservices.azure.com/.default\n")

for endpoint in test_endpoints:
    print(f"Testing: {endpoint}")
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code != 404:
            print(f"  ✓ SUCCESS! Response: {response.text[:200]}")
            break
        else:
            print(f"  ✗ 404 - {response.text[:100]}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
