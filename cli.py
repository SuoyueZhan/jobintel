import argparse
from app.rules import analyze_jd

def main():
    parser = argparse.ArgumentParser(description="Analyze JD text for clearance/citizenship language.")
    parser.add_argument("text", nargs="?", default="", help="Job description text (or use --file)")
    parser.add_argument("--file", "-f", help="Path to a text file containing the JD")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = args.text

    result = analyze_jd(text)
    print(result)

if __name__ == "__main__":
    main()
