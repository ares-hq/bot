from flask import Flask, render_template_string
import markdown

# load_dotenv()
app = Flask(__name__)

@app.route("/")
def home():
    # runBot()
    return "Hello, FTC Scout!"

# Example = http://127.0.0.1:5000/query/team%2014584

@app.route('/query/<msg>')
def process(msg):
    # Get the markdown result
    markdown_content = handle_user_messages(msg)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content)
    
    # Replace newline characters with <br> for proper line breaks in HTML
    html_content = html_content.replace("\n", "<br />")
    
    # Render HTML content in a Flask response (using render_template_string for simplicity)
    return render_template_string("""
    <html>
        <head>
            <title>Team Info</title>
        </head>
        <body>
            <h1>Team Information</h1>
            <div>{{ content|safe }}</div>
        </body>
    </html>
    """, content=html_content)

if __name__ =='__main__':
    runBot()
    app.run(debug=True)