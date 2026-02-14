from woocommerce import API
import json

URL = "https://mecobooks.com"
KEY = "ck_34f92dc77ecc6b196a6604fa29d9cf21cf3475c0"
SECRET = "cs_a03e99659fc6e5f837f7b8c8c70269e3fc99af60"

wcapi = API(
    url=URL,
    consumer_key=KEY,
    consumer_secret=SECRET,
    version="wc/v3",
    timeout=20
)

try:
    print("Fetching products...")
    products = wcapi.get("products", params={"per_page": 2}).json()
    
    if products:
        print(f"Found {len(products)} products.")
        for p in products:
            print(f"\nProduct: {p.get('name')}")
            print(f"Images raw data: {json.dumps(p.get('images'), indent=2)}")
            print(f"Meta Data keys: {[m['key'] for m in p.get('meta_data', [])]}")
            
            print(json.dumps(p.get('meta_data', []), indent=2))

            image_url = "No Image"
            if p.get("images") and len(p["images"]) > 0:
                image_url = p["images"][0].get('src')
            elif p.get("meta_data"):
                for meta in p["meta_data"]:
                    if meta.get("key") == "_ext_featured_url" and meta.get("value"):
                        image_url = meta["value"]
                        break
            
            print(f"Final Image URL: {image_url}")
    else:
        print("No products returned.")
        print(products)

except Exception as e:
    print(f"Error: {e}")
