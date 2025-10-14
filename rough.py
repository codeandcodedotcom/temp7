from databricks.sdk import WorkspaceClient
import requests
import json

# ===== HARDCODED VALUES =====
WORKSPACE_URL = "https://adb-<workspace-id>.azuredatabricks.net"  # Replace with your workspace URL

# Models to test
MODELS = ["gpt41mini", "gpt-41", "gpt-4o"]

# ===== Initialize Databricks Client using cluster's built-in auth =====
try:
    client = WorkspaceClient(host=WORKSPACE_URL)
    print("✓ Databricks authentication successful\n")
except Exception as e:
    print(f"✗ Authentication failed: {str(e)}")
    exit()

# Get auth token from client
try:
    token = client.auth.token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
except:
    print("Warning: Could not retrieve token for API calls")
    headers = {}

# ===== Test Model Accessibility =====
print(f"Testing models: {MODELS}\n")

for model in MODELS:
    try:
        endpoint = client.serving_endpoints.get(model)
        print(f"✓ {model}: Accessible")
        print(f"  Status: {endpoint.state}")
        
        # ===== Test Model Invocation with a prompt using raw HTTP =====
        try:
            url = f"{WORKSPACE_URL}/serving-endpoints/{model}/invocations"
            payload = {
                "messages": [
                    {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
                ]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Invocation successful")
                # Extract response text
                if "choices" in result and len(result["choices"]) > 0:
                    if "message" in result["choices"][0]:
                        print(f"  Response: {result['choices'][0]['message']}")
                    elif "text" in result["choices"][0]:
                        print(f"  Response: {result['choices'][0]['text']}")
                else:
                    print(f"  Response: {result}")
            else:
                print(f"  ✗ Invocation failed: HTTP {response.status_code}")
                print(f"  Error: {response.text}")
                
        except Exception as invoke_error:
            print(f"  ✗ Invocation failed: {str(invoke_error)}")
        
        print()
    except Exception as e:
        error_str = str(e).lower()
        if "404" in str(e) or "not found" in error_str:
            print(f"✗ {model}: Not found (404)")
        elif "403" in str(e) or "forbidden" in error_str:
            print(f"✗ {model}: Forbidden - No permission (403)")
        else:
            print(f"✗ {model}: Error - {str(e)}")
        print()
