from app.models.schemas import HtmlCss

def generate_html_css(context: dict) -> HtmlCss:
    # generate html and css based on the context provided

    image_data = context.get("image", None)

    #generate
    if image_data:
        # In a real implementation, this would analyze the image using a model
        html = "<div class='container'><h1>Generated Title</h1></div>"
        css = ".container { width: 100%; padding: 20px; }\nh1 { color: blue; }"
    else:
        # Fallback for high-level command (e.g., "generate a simple webpage")
        html = "<div class='default'><p>Default Content</p></div>"
        css = ".default { border: 1px solid black; padding: 10px; }"

    return HtmlCss(html=html, css=css)