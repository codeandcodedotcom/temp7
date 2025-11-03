import json
import sys
import os

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

        # Pretty print JSON
        formatted_json = json.dumps(data, indent=4)

        # Create output file name
        base, ext = os.path.splitext(file_path)
        output_file = f"{base}_formatted{ext}"

        # Write formatted JSON to new file
        with open(output_file, "w") as outfile:
            outfile.write(formatted_json)

        print(f"📝 Formatted JSON written to: {output_file}")

    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except json.JSONDecodeError as e:
        print("❌ Invalid JSON!")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
