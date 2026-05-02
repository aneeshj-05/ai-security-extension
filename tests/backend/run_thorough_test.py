import asyncio
import sys
import os

# Ensure the backend directory is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.services.phishing_service import analyze_url

TEST_URLS = [
    # 1. Trusted Domain (Should bypass ML)
    "https://google.com/search?q=very+long+query+with+special+chars&&%!",
    
    # 2. Known Benign (Not highly ranked, tests ML and Heuristics)
    "https://some-small-local-bakery-shop.com/about-us",
    
    # 3. Typosquatting (Should hit Heuristics override, Score 100)
    "https://paypa1.com/login",
    
    # 4. IP Address Phishing
    "http://192.168.1.100/secure/login.php",
    
    # 5. Subdomain Chaining
    "https://secure-update.billing.apple-support-portal.info",
    
    # 6. ML-Specific Phishing (Suspicious TLD + Keywords, but normal length)
    "https://account-verify-secure.xyz",
    
    # 7. Deep Path Benign
    "https://python.org/doc/versions/3.12/library/asyncio.html"
]

async def run_tests():
    print("="*60)
    print(" THOROUGH AI SECURITY PIPELINE TEST ".center(60))
    print("="*60)
    
    for url in TEST_URLS:
        print(f"\nAnalyzing: {url}")
        result = await analyze_url(url)
        
        status = "🔴 PHISHING" if result["is_phishing"] else "🟢 SAFE"
        score = result["risk_score"]
        verdict = result["verdict"]
        ml_conf = f"{round(result['ml_confidence'] * 100)}%" if result["ml_confidence"] is not None else "N/A (Bypassed)"
        
        print(f"  Result:        {status}")
        print(f"  Risk Score:    {score}/100")
        print(f"  Verdict:       {verdict}")
        print(f"  ML Confidence: {ml_conf}")
        if result["reasons"]:
            print("  Reasons:")
            for r in result["reasons"]:
                print(f"   - {r}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(run_tests())
