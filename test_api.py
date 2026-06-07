import json
import urllib.request
import time

def test_score_lead():
    url = "http://127.0.0.1:8000/score-lead"
    data = {
        "name": "Jane Smith",
        "company": "Global Logistics Ltd",
        "budget": 150000,
        "requirements": "We are looking for a comprehensive AI-driven route optimization engine to be integrated into our fleet management software. This is a high-priority project for Q3."
    }
    
    json_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=json_data, headers={"Content-Type": "application/json"})
    
    print("Testing Groq-powered Lead Scorer API...")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                print("\nAI Response Received:")
                print(json.dumps(result, indent=2))
                
                # Assert structural integrity
                assert "lead_score" in result
                assert isinstance(result["lead_score"], int)
                assert 1 <= result["lead_score"] <= 10
                
                assert "urgency" in result
                assert result["urgency"] in ["low", "medium", "high"]
                
                assert "summary" in result
                assert isinstance(result["summary"], str)
                assert len(result["summary"]) > 0
                
                assert "recommended_action" in result
                assert isinstance(result["recommended_action"], str)
                assert len(result["recommended_action"]) > 0
                
                print("\nAI Integration Test Passed!")
                return
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            print(f"HTTP Error {e.code}: {error_body}")
            if i < max_retries - 1:
                print(f"Retrying (Attempt {i+1}/{max_retries})...")
                time.sleep(3)
            else:
                exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            if i < max_retries - 1:
                print(f"Retrying (Attempt {i+1}/{max_retries})...")
                time.sleep(3)
            else:
                exit(1)

if __name__ == "__main__":
    test_score_lead()
