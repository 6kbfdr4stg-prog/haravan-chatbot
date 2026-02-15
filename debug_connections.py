
import os
import sys
from woocommerce_client import WooCommerceClient
from llm_service import LLMService

# Mock auth if needed for testing, but better to rely on what's there or fail gracefully
# We will just try to init and search
def test_woo():
    print("--- Testing WooCommerce ---")
    wc = WooCommerceClient()
    if not wc.wcapi:
        print("SKIP: WooCommerce credentials not found in env.")
        # Attempt to see if we can just request public web if api fails? 
        # But WC client uses keys. 
        return
    
    products = wc.search_products("sách", limit=1)
    if products:
        print(f"SUCCESS: Found product: {products[0]['title']}")
    else:
        print("FAIL: Search returned no results or connection error.")

def test_llm():
    print("\n--- Testing Gemini LLM ---")
    try:
        llm = LLMService()
        resp = llm.generate_response("Say 'Hello from Gemini!'")
        print(f"SUCCESS: {resp}")
    except Exception as e:
        print(f"FAIL: LLM Error: {e}")

if __name__ == "__main__":
    test_woo()
    test_llm()
