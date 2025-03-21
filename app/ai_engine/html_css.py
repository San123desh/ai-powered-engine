from app.models.schemas import HtmlCss

def generate_html_css(context: dict) -> HtmlCss:
    """
    Generate HTML and CSS based on an image or high-level command.
    """
    image_data = context.get("image", None)

    if image_data:
        html = "<div class='container'><h1>Generated Title</h1></div>"
        css = ".container { width: 100%; padding: 20px; }\nh1 { color: blue; }"
    else:
        html = "<div class='default'><p>Default Content</p></div>"
        css = ".default { border: 1px solid black; padding: 10px; }"

    return HtmlCss(html=html, css=css)