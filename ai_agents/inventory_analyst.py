
import os
import sys

# Add parent dir to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from woocommerce_client import WooCommerceClient

class InventoryAnalystAgent:
    def __init__(self):
        self.woo = WooCommerceClient()

    def analyze_stock(self):
        """
        Analyzes stock using ABC Analysis (Pareto Principle):
        - Group A (Best Sellers): Top 20% of products by sales.
        - Group C (Dead Stock): 0 Sales & In Stock.
        - Group B (Standard): The rest.
        """
        print("🤖 [Inventory Agent] Starting ABC Inventory Analysis...")
        
        # 1. Fetch Data (Fetch more items for analysis)
        products = self.woo.search_products(" ", limit=100) 
        if not products:
             products = self.woo.search_products("sách", limit=100)

        # 2. Sort by Sales
        # Ensure total_sales is int
        for p in products:
            try:
                p['total_sales'] = int(p.get('total_sales', 0))
            except:
                p['total_sales'] = 0
                
        sorted_products = sorted(products, key=lambda x: x['total_sales'], reverse=True)
        
        total_items = len(sorted_products)
        if total_items == 0:
            return {"error": "No products found"}

        # 3. Classify
        # A: Top 20%
        top_20_count = int(total_items * 0.2)
        group_a = sorted_products[:top_20_count]
        
        remaining = sorted_products[top_20_count:]
        group_c = [p for p in remaining if p['total_sales'] == 0]
        group_b = [p for p in remaining if p['total_sales'] > 0]

        report = {
            "total_scanned": total_items,
            "group_a": group_a,
            "group_b": group_b,
            "group_c": group_c,
            "missing_images": [p for p in products if "placehold.co" in p.get('image', '')]
        }
        return report

    def generate_action_plan(self, report):
        """
        Generates a strategic action plan based on ABC analysis.
        """
        if "error" in report:
            return "⚠️ Không tìm thấy dữ liệu sản phẩm để phân tích."

        plan = f"📊 **BÁO CÁO CHIẾN LƯỢC TỒN KHO (Mô hình ABC)**\n"
        plan += f"Tổng quét: {report['total_scanned']} sản phẩm.\n\n"
        
        # Group A Strategy
        plan += f"🌟 **NHÓM A - Best Sellers ({len(report['group_a'])} sp)**\n"
        plan += f"_(Chiếm 80% doanh thu - Cần ưu tiên nhập hàng & Marketing)_\n"
        for p in report['group_a'][:5]:
            plan += f"- {p['title']} (Đã bán: {p['total_sales']})\n"
        plan += "👉 **Hành động**: Kiểm tra kho ngay, nếu thấp hơn 5 cuốn -> Nhập gấp.\n\n"

        # Group C Strategy
        plan += f"❄️ **NHÓM C - Hàng Tồn / Chậm ({len(report['group_c'])} sp)**\n"
        plan += f"_(Chưa bán được cuốn nào - Cần giải phóng vốn)_\n"
        for p in report['group_c'][:5]:
             plan += f"- {p['title']}\n"
        plan += "👉 **Hành động**: \n"
        plan += "   + Tạo Combo 'Sách Mù' (49k/cuốn).\n"
        plan += "   + Tặng kèm cho đơn hàng > 200k.\n"
        plan += "   + Livestream xả kho.\n\n"
        
        # Missing Data
        if report["missing_images"]:
            plan += f"⚠️ **Cảnh báo**: Có {len(report['missing_images'])} sản phẩm thiếu ảnh, ảnh hưởng tỷ lệ chuyển đổi.\n"

        return plan

if __name__ == "__main__":
    agent = InventoryAnalystAgent()
    # Mocking data for test if no API
    # ...
    try:
        analysis = agent.analyze_stock()
        print(agent.generate_action_plan(analysis))
    except Exception as e:
        print(f"Error: {e}")
