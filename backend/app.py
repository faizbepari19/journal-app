import os
import ssl
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import db, migrate, bcrypt, jwt

# Load environment variables
load_dotenv()

# Configure SSL bypass for development
def configure_ssl_bypass():
    """Configure SSL bypass for development environment"""
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Disable SSL verification
    ssl._create_default_https_context = ssl._create_unverified_context
    
    # Set environment variables for SSL bypass
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = ''
    os.environ['GRPC_VERBOSITY'] = 'ERROR'
    
    print("🔓 SSL certificate verification disabled for development")

# Apply SSL bypass
configure_ssl_bypass()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Import models to ensure they're registered with SQLAlchemy
    from models import User, Entry
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.entry_routes import entry_bp
    from routes.ai_routes import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(entry_bp, url_prefix='/api/entries')
    app.register_blueprint(ai_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
