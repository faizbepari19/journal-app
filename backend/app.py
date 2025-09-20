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
    
    # Ensure instance directory exists for SQLite
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False  # Disable SQL query logging to reduce noise
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire
    
    # Configure logging for development
    if os.getenv('FLASK_ENV') == 'development':
        import logging
        # Reduce SQLAlchemy logging noise - only show warnings and errors
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # CORS configuration for production
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:5174", 
                "https://journal-app-six-xi.vercel.app",
                "https://*.vercel.app",
                "https://*.netlify.app",
                "https://*.onrender.com"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
