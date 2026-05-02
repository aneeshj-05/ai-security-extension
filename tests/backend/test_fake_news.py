import sys
import os

# Ensure the backend directory is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.services.news_service import analyze_content

SAMPLES = [
    {
        "title": "Federal Reserve Maintains Interest Rates at 5.25%",
        "text": (
            "The Federal Reserve announced on Wednesday that it will maintain current interest rates "
            "following a two-day meeting of the Federal Open Market Committee. Chairman Jerome Powell "
            "stated that inflation remains the primary concern, though employment data suggests a "
            "resilient economy. The decision was expected by most Wall Street analysts and comes "
            "after three consecutive months of cooling consumer price indices."
        ),
        "description": "Factual Financial News (Expected: Safe)"
    },
    {
        "title": "SHOCKING: Secret Plot to Control Your Mind Through Toasters!",
        "text": (
            "A anonymous whistleblower has finally come forward to reveal the terrifying truth. "
            "The government is installing high-frequency mind-control chips in every toaster sold "
            "since 2021. They are using these signals to influence your political thoughts and "
            "make you crave more processed cheese. This is a massive conspiracy and the mainstream "
            "media is being paid to keep quiet. SHARE THIS URGENT TRUTH BEFORE IT'S TOO LATE!!"
        ),
        "description": "Sensationalist Conspiracy (Expected: Fake News)"
    }
]

def run_tests():
    print("="*60)
    print(" FAKE NEWS DETECTION TEST ".center(60))
    print("="*60)

    for i, sample in enumerate(SAMPLES):
        print(f"\n[{i+1}] Testing: {sample['description']}")
        print(f"    Headline: {sample['title']}")
        
        result = analyze_content(sample["title"], sample["text"])
        
        status = "🔴 FAKE NEWS" if result["is_fake_news"] else "🟢 REAL NEWS"
        score = result["risk_score"]
        ml_conf = f"{round(result['ml_confidence'] * 100)}%" if result["ml_confidence"] is not None else "N/A"
        
        print(f"    Result:        {status}")
        print(f"    Risk Score:    {score}/100")
        print(f"    ML Confidence: {ml_conf}")
        if result["reasons"]:
            print("    Reasons:")
            for r in result["reasons"]:
                print(f"     - {r}")
        print("-" * 60)

if __name__ == "__main__":
    run_tests()
