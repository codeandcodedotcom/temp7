# save as dump_jwt.py and run: python dump_jwt.py "<ACCESS_TOKEN>"
import sys, base64, json
tok = sys.argv[1]
parts = tok.split('.')
def dec(p): return json.loads(base64.urlsafe_b64decode(p + '=' * (-len(p)%4)).decode())
print("HEADER:", json.dumps(dec(parts[0]), indent=2))
print("PAYLOAD:", json.dumps(dec(parts[1]), indent=2))
