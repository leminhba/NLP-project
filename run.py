from flask import Flask
from api import register_blueprints

app = Flask(__name__)

# Đăng ký các blueprint
register_blueprints(app)

if __name__ == '__main__':
    app.run(debug=True)