from haravan_client import HaravanClient
from prepare_content import prepare_product_content
from video_processor import generate_video
import os

def main():
    # 1. Connect
    print("Connecting to Haravan...")
    client = HaravanClient()
    
    # 2. Get Products
    products = client.get_products(limit=3) # Limit to 3 for testing
    print(f"Found {len(products)} products.")
    
    for product in products:
        try:
            # 3. Extract & Prepare
            p_data = client.extract_product_data(product)
            content = prepare_product_content(p_data)
            
            # 4. Generate Video
            if content and content['images']:
                 video_path = generate_video(content)
                 if video_path:
                     print(f"SUCCESS: Video created at {video_path}")
                 else:
                     print(f"FAILED: Could not create video for {content['title']}")
            else:
                 print(f"SKIPPING: No images or content for {p_data['title']}")
                 
        except Exception as e:
            print(f"ERROR processing product {product.get('title')}: {e}")

if __name__ == "__main__":
    main()
