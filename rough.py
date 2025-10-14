import requests
import json

# ===== HARDCODED VALUES - Replace with your actual values =====
WORKSPACE_URL = "https://adb-<workspace-id>.azuredatabricks.net"  # Replace with your workspace URL
CLIENT_ID = "your-client-id-here"                                  # Replace with your Service Principal App ID
CLIENT_SECRET = "your-client-secret-here"                          # Replace with your Service Principal secret
TENANT_ID = "your-tenant-id-here"                                  # Replace with your Azure Tenant ID

# Models to test
MODELS = ["gpt-4-1-mini", "gpt-4-1", "gpt-4o"]

# ===== STEP 1: Get Azure Token =====
print("Getting Azure token...")
token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
token_data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default",
    "grant_type": "client_credentials"
}

token_response = requests.post(token_url, data=token_data)
if token_response.status_code != 200:
    print(f"✗ Failed to get token: {token_response.text}")
    exit()

access_token = token_response.json()["access_token"]
print("✓ Azure authentication successful\n")

# ===== STEP 2: Test Model Accessibility =====
print(f"Testing models: {MODELS}\n")

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

for model in MODELS:
    # Test 1: Check if endpoint exists
    url = f"{WORKSPACE_URL}/api/2.0/serving-endpoints/{model}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print(f"✓ {model}: Accessible")
        endpoint_data = response.json()
        print(f"  Status: {endpoint_data.get('state', 'Unknown')}")
        
        # Test 2: Try to invoke the model
        invoke_url = f"{WORKSPACE_URL}/serving-endpoints/{model}/invocations"
        payload = {
            "messages": [
                {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
            ]
        }
        
        invoke_response = requests.post(invoke_url, json=payload, headers=headers, timeout=30)
        
        if invoke_response.status_code == 200:
            result = invoke_response.json()
            print(f"  ✓ Invocation successful")
            if "choices" in result and len(result["choices"]) > 0:
                if "message" in result["choices"][0]:
                    print(f"  Response: {result['choices'][0]['message']}")
                elif "text" in result["choices"][0]:
                    print(f"  Response: {result['choices'][0]['text']}")
            else:
                print(f"  Response: {result}")
        else:
            print(f"  ✗ Invocation failed: HTTP {invoke_response.status_code}")
            print(f"  Error: {invoke_response.text}")
    else:
        print(f"✗ {model}: HTTP {response.status_code}")
        print(f"  Error: {response.text}")
    
    print()
