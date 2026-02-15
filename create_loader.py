import re

def create_loader():
    with open("chat_widget.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Extract CSS
    css_match = re.search(r"<style>(.*?)</style>", content, re.DOTALL)
    css_content = css_match.group(1).strip() if css_match else ""

    # Extract JS
    js_match = re.search(r"<script>(.*?)</script>", content, re.DOTALL)
    js_content = js_match.group(1).strip() if js_match else ""

    # Extract HTML (everything else inside body, roughly)
    # We can just remove style and script tags to get HTML
    html_content = re.sub(r"<style>.*?</style>", "", content, flags=re.DOTALL)
    html_content = re.sub(r"<script>.*?</script>", "", html_content, flags=re.DOTALL)
    # Remove comments
    html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)
    html_content = html_content.strip()

    # Escape backticks in CSS and HTML for template literals
    css_content = css_content.replace("`", "\\`")
    html_content = html_content.replace("`", "\\`")
    
    # JS content needs to be carefully handled. 
    # We will inject it as a function body.
    # We don't need to escape backticks in JS if we don't wrap JS in backticks?
    # Actually, we will wrap the whole thing in a function.
    
    loader_js = f"""(function() {{
  // 1. Inject CSS
  const style = document.createElement('style');
  style.textContent = `
{css_content}
  `;
  document.head.appendChild(style);

  // 2. Inject HTML
  const container = document.createElement('div');
  container.id = 'haravan-widget-root';
  container.innerHTML = `
{html_content}
  `;
  document.body.appendChild(container);

  // 3. Run Logic
  {js_content}

}})();
"""
    
    with open("widget_loader.js", "w", encoding="utf-8") as f:
        f.write(loader_js)
    
    print("widget_loader.js created successfully.")

if __name__ == "__main__":
    create_loader()
