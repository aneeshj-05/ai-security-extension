import asyncio
from app.utils.whois_lookup import get_domain_age_days

test_domains = [
    "google.com",
    "amazon.com",
    "paypal.com",
    "facebook.com",
    "secure-login-verify.xyz",
    "googll.com",
]


async def main():
    for domain in test_domains:
        result = await get_domain_age_days(domain)
        days = result["age_days"]
        if days == -1:
            status = (
                f"WHOIS unknown ({result['status']}), "
                f"resolves={result['domain_resolves']}"
            )
        elif days < 180:
            status = f"NEW DOMAIN - only {days} days old - rule fires"
        else:
            years = days // 365
            status = f"Safe age - {days} days ({years} years old)"

        print(f"{domain:<35} -> {status}")


if __name__ == "__main__":
    asyncio.run(main())
