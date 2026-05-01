from app.utils.whois_lookup import get_domain_age_days

test_domains = [
    "google.com",
    "amazon.com",
    "paypal.com",
    "facebook.com",
    "secure-login-verify.xyz",
    "googll.com",
]

for domain in test_domains:
    days = get_domain_age_days(domain)
    if days == -1:
        status = "WHOIS failed / domain doesn't exist"
    elif days < 180:
        status = f"⚠️  NEW DOMAIN — only {days} days old → rule fires"
    else:
        years = days // 365
        status = f"✅ Safe age — {days} days ({years} years old)"

    print(f"{domain:<35} → {status}")
