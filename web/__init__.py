from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user
import os

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ensure instance folder exists before configuring DB path
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("NEU_SECRET", "change-me"),
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "neu.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        REMEMBER_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # Ensure a place for profile pictures under the static folder
    avatar_dir = os.path.join(app.static_folder, "profile_pics")
    os.makedirs(avatar_dir, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    bcrypt.init_app(app)
    csrf.init_app(app)

    # rate limiting
    limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["30 per minute"])

    # import blueprints
    from .auth import auth_bp
    from .routes import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # security headers (simple)
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=()"
        # Prevent cached authenticated pages from being shown after logout
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # Make helpers and user context available in templates
    from .utils import find_user_avatar
    from .models import Notification

    @app.context_processor
    def inject_user_avatar():
        avatar_path = None
        notifications = []
        try:
            if current_user.is_authenticated:
                avatar_path = find_user_avatar(app.static_folder, current_user.id)
                notifications = (
                    Notification.query
                    .filter_by(user_id=current_user.id)
                    .order_by(Notification.created_at.desc())
                    .limit(10)
                    .all()
                )
        except Exception:
            avatar_path = None
            notifications = []
        return {
            "current_user_avatar": avatar_path,
            "current_user_notifications": notifications,
        }

    with app.app_context():
        db.create_all()

        # Ensure only the intended admin user exists and is marked as admin.
        from .models import User

        admin_username = "James Jamero"  # Single designated admin account

        # First, reset all users to non-admin to avoid older data where everyone was admin.
        for u in User.query.all():
            u.is_admin = False

        # Create or update the admin user. Always enforce the configured password
        # so you have a known credential even if the user existed before.
        admin = User.query.filter_by(username=admin_username).first()
        admin_password = os.environ.get("NEU_ADMIN_PASSWORD", "TakanashiHoshino123")

        if admin is None:
            admin = User(username=admin_username, is_admin=True)
            admin.set_password(admin_password)
            db.session.add(admin)
        else:
            admin.is_admin = True
            admin.set_password(admin_password)

        db.session.commit()

    return app
