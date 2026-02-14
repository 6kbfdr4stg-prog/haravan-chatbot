from chatbot import Chatbot

def main():
    print("Initializing Haravan AI Chatbot...")
    try:
        bot = Chatbot()
        print("-" * 50)
        print("🤖 CHATBOT: Xin chào! Tôi là trợ lý ảo của Tiệm Sách Anh Tuấn.")
        print("Tôi có thể giúp bạn tìm sách hoặc kiểm tra đơn hàng.")
        print("(Gõ 'exit' hoặc 'quit' để thoát)")
        print("-" * 50)

        while True:
            try:
                user_input = input("\n👤 BẠN: ")
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("🤖 CHATBOT: Tạm biệt! Hẹn gặp lại.")
                    break

                print("... (Đang suy nghĩ) ...")
                response = bot.process_message(user_input)
                print(f"🤖 CHATBOT: {response}")

            except KeyboardInterrupt:
                print("\n🤖 CHATBOT: Tạm biệt!")
                break
            except Exception as e:
                print(f"❌ Lỗi: {e}")

    except Exception as e:
        print(f"Critical Error during initialization: {e}")

if __name__ == "__main__":
    main()
