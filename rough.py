import json
import sys

def main():
    # Check if a filename was provided
    if len(sys.argv) != 2:
        print("Usage: python jsonlint.py <filename.json>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        print("✅ JSON is valid!")
        # Optional: Pretty print the JSON
        print(json.dumps(data, indent=4))
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except json.JSONDecodeError as e:
        print("❌ Invalid JSON!")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
