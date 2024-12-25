from flask import Flask, render_template_string
import markdown

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/")
        def home():
            return "Hello, FTC Scout!"

        @self.app.route('/team/<msg>')
        def team(msg):
            # Get the markdown result
            markdown_content = handle_user_messages(msg)
            return self.render(markdown_content)
        
        @self.app.route('/match/<msg>')
        def match(msg):
            # Get the markdown result
            markdown_content = handle_user_messages(msg)
            return self.render(markdown_content)

    def render(self, markdown_content: str) -> str:
        '''Convert markdown to HTML and render it in a Flask response.'''
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Replace newline characters with <br> for proper line breaks in HTML
        html_content = html_content.replace("\n", "<br />")
        
        # Render HTML content in a Flask response
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

    def run(self, debug=True):
        self.app.run(debug=debug)

if __name__ == '__main__':
    flask_app = FlaskApp().run()