
import os
import sys

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from woocommerce_client import WooCommerceClient
from llm_service import LLMService
# from video_generator import create_video_from_product # Placeholder for future

class ContentCreatorAgent:
    def __init__(self):
        self.woo = WooCommerceClient()
        self.llm = LLMService()

    def generate_daily_content(self, platform="facebook"):
        """
        Main function to generate daily content.
        1. Picks a product from WooCommerce.
        2. Generates a caption using LLM.
        3. Returns the content (and potentially triggers video creation).
        """
        print(f"🤖 [Content Agent] Starting daily content generation for {platform}...")
        
        # 1. Select a product (Random or based on strategy)
        # For now, search for a popular keyword or random
        products = self.woo.search_products("sách", limit=20)
        
        if not products:
            return "⚠️ [Content Agent] No products found to promote."

        import random
        product = random.choice(products)
        print(f"   Selected Product: {product['title']}")

        # 2. Generate Caption
        prompt = f"""
        Bạn là một chuyên gia sáng tạo nội dung cho Tiệm Sách Anh Tuấn (mecobooks.com).
        Hãy viết một bài đăng {platform} hấp dẫn để giới thiệu cuốn sách: "{product['title']}".
        
        Thông tin sách:
        - Giá: {product['price']} VNĐ
        - Tình trạng: {product['inventory_text']}
        - Tình trạng: {product['inventory_text']}
        - Link mua hàng: {product['url']} (LƯU Ý: KHÔNG chèn link này vào bài viết, chỉ viết nội dung kêu gọi. Link sẽ được để dưới comment).
        
        Yêu cầu:
        - Tone giọng: Nhẹ nhàng, sâu sắc, tinh tế, kể chuyện (storytelling).
        - Tuyệt đối KHÔNG giật tít, KHÔNG gây sốc, KHÔNG dùng ngôn ngữ chợ búa.
        - Tập trung vào giá trị tinh thần và cảm xúc mà cuốn sách mang lại.
        - Có Call To Action nhẹ nhàng (ví dụ: "Mời bạn ghé đọc...", "Link mình để dưới comment...").
        - Sử dụng icon và hashtag phù hợp (#MecoBooks #SachHay ...).
        - Độ dài: Khoảng 150-200 từ.
        - TUYỆT ĐỐI KHÔNG CHÈN URL VÀO BÀI VIẾT.
        """
        
        caption = self.llm.generate_response(prompt)
        
        return {
            "product": product,
            "caption": caption,
            "image_url": product['image']
        }

    def send_to_webhook(self, content):
        """
        Send generated content to a Webhook (Make/n8n) for distribution.
        """
        import requests
        webhook_url = os.environ.get("MAKE_WEBHOOK_URL")

        if not webhook_url:
            print("⚠️ [Content Agent] Missing MAKE_WEBHOOK_URL. Content generated but not sent.")
            return

        print(f"🚀 [Content Agent] Sending content to Webhook...")
        
        payload = {
            "title": content['product']['title'],
            "price": content['product']['price'],
            "image_url": content['image_url'],
            "caption": content['caption'],
            "link": content['product']['url'],
            "source": "ai_agent"
        }

        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                print(f"✅ [Content Agent] Webhook trigger successful!")
            else:
                print(f"❌ [Content Agent] Webhook trigger failed: {response.text}")
        except Exception as e:
            print(f"❌ [Content Agent] Error sending to Webhook: {e}")


if __name__ == "__main__":
    agent = ContentCreatorAgent()
    content = agent.generate_daily_content()
    print("\n--- GENERATED CONTENT ---\n")
    print(content)
    
    # Test Webhook
    if content and isinstance(content, dict):
        agent.send_to_webhook(content)
