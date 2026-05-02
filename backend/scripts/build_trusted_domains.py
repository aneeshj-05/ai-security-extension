import argparse
from pathlib import Path


def extract_domain(line: str) -> str:
    value = line.strip().lower()

    if not value or value.startswith("#"):
        return ""

    parts = [part.strip() for part in value.split(",") if part.strip()]
    candidate = parts[-1] if parts else value

    if candidate.startswith(("http://", "https://")):
        candidate = candidate.split("://", 1)[1]

    domain = candidate.split("/", 1)[0].lstrip(".")
    return "" if domain in {"domain", "url", "hostname"} else domain


def build(input_path: Path, output_path: Path, limit: int) -> int:
    domains = []
    seen = set()

    for line in input_path.read_text().splitlines():
        domain = extract_domain(line)

        if not domain or domain in seen:
            continue

        seen.add(domain)
        domains.append(domain)

        if limit and len(domains) >= limit:
            break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(domains) + "\n")
    return len(domains)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build trusted_domains.txt from a Tranco/top-sites CSV "
            "or plain domain list."
        )
    )
    parser.add_argument("input_file")
    parser.add_argument(
        "--output",
        default="backend/app/data/trusted_domains.txt",
    )
    parser.add_argument("--limit", type=int, default=10000)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    count = build(Path(args.input_file), Path(args.output), args.limit)
    print(f"Wrote {count} domains to {args.output}")
