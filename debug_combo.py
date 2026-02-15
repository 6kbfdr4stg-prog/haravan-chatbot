from woocommerce_client import WooCommerceClient
from dotenv import load_dotenv
import os

load_dotenv()

def test_combo_search():
    woo = WooCommerceClient()
    
    # Mock the list from the user's image
    raw_list = [
        "Tự truyện của Benjamin Franklin",
        "Tâm lý học về tiền (Morgan Housel)",
        "Tư duy nhanh và chậm"
    ]
    
    products = []
    print(f"Searching for list ({len(raw_list)} items): {raw_list}")
    
    for item_title in raw_list[:4]: 
        # Strip authors in brackets if common format (Name - Author) or (Name (Author))
        clean_title = item_title.split('(')[0].split('-')[0].strip()
        print(f"Searching for: '{clean_title}'")
        found = woo.search_products(clean_title, limit=1)
        if found:
            print(f"Found: {found[0]['title']}")
            products.extend(found)
        else:
            print("Not found")

    print(f"Total found: {len(products)}")

if __name__ == "__main__":
    test_combo_search()
