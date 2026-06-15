from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from .forms import LoginForm, RegistrationForm, ForgotPasswordForm, AdminLoginForm
from .models import User
from .models import Notification
from . import db
from flask_login import login_user, logout_user, login_required, current_user
import os

from .utils import ALLOWED_AVATAR_EXTENSIONS, find_user_avatar

auth_bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("main.pre_dashboard"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    form = AdminLoginForm()

    if request.method == "POST":
        # Read raw values directly to avoid over-strict form validation issues.
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        favorite_color = (request.form.get("favorite_color") or "").strip().lower()
        age = (request.form.get("age") or "").strip()
        email = (request.form.get("email") or "").strip().lower()

        if not username or not password or not favorite_color or not age or not email:
            flash("Please fill in all admin login fields.", "danger")
            return render_template("admin_login.html", form=form)

        user = User.query.filter_by(username=username).first()

        if not user or not user.is_admin or not user.check_password(password):
            flash("Invalid admin credentials", "danger")
            return render_template("admin_login.html", form=form)

        # Extra security questions for the admin account.
        # In a real deployment these should come from secure config or DB.
        expected_color = os.environ.get("NEU_ADMIN_FAV_COLOR", "red").strip().lower()
        expected_age = os.environ.get("NEU_ADMIN_AGE", "21").strip()
        expected_email = os.environ.get("NEU_ADMIN_EMAIL", "jamerojames425@gmail.com").strip().lower()

        color_ok = favorite_color == expected_color
        age_ok = age == expected_age
        email_ok = email == expected_email

        if not (color_ok and age_ok and email_ok):
            flash("Admin security answers are incorrect.", "danger")
            return render_template("admin_login.html", form=form)

        login_user(user, remember=False)
        flash("Welcome, admin.", "success")
        return redirect(url_for("main.pre_dashboard"))

    return render_template("admin_login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(username=form.username.data).first()
        if existing:
            flash("Username already taken", "danger")
        else:
            user = User(username=form.username.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        # In a real app, you would look up the user by email and
        # send a reset link instead of revealing whether the email exists.
        flash("If this email is registered, password reset instructions have been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    was_admin = getattr(current_user, "is_admin", False)
    logout_user()
    if was_admin:
        return render_template("admin_logout.html")
    return render_template("logout.html")


def _allowed_avatar_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Simple profile page for managing avatar image.

    Users can upload a JPG, PNG, or WEBP image. The selected file is stored
    under the app's static/profile_pics directory as ``user_<id>.<ext>``.
    """
    avatar_url = find_user_avatar(current_app.static_folder, current_user.id)

    if request.method == "POST":
        file = request.files.get("avatar")

        if not file or file.filename == "":
            flash("Please choose an image file to upload.", "warning")
            return redirect(url_for("auth.profile"))

        if not _allowed_avatar_file(file.filename):
            flash("Invalid file type. Please upload a JPG, PNG, or WEBP image.", "danger")
            return redirect(url_for("auth.profile"))

        upload_folder = os.path.join(current_app.static_folder, "profile_pics")
        os.makedirs(upload_folder, exist_ok=True)

        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"user_{current_user.id}.{ext}"
        filepath = os.path.join(upload_folder, filename)

        # Remove any older avatar variants for this user
        for allowed_ext in ALLOWED_AVATAR_EXTENSIONS:
            old_path = os.path.join(upload_folder, f"user_{current_user.id}.{allowed_ext}")
            if os.path.exists(old_path) and old_path != filepath:
                try:
                    os.remove(old_path)
                except OSError:
                    pass

        # Save the newly uploaded avatar file
        file.save(filepath)

        # Log notification for this user
        note = Notification(
            user_id=current_user.id,
            message="Updated profile picture",
        )
        db.session.add(note)
        db.session.commit()

        flash("Profile picture updated.", "success")
        return redirect(url_for("auth.profile"))

    return render_template("profile.html", avatar_url=avatar_url)


@auth_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    """Allow a logged-in user to delete their own account.

    The account is removed from the login/dashboard, but existing analyses
    and awareness activity are reassigned to the admin user so they remain
    available for review.
    """
    from .models import Report, Notification

    user = current_user

    # Find an admin user to reassign historical data to, if available.
    admin_user = User.query.filter_by(is_admin=True).first()

    if admin_user and admin_user.id != user.id:
        for rep in Report.query.filter_by(user_id=user.id).all():
            rep.user_id = admin_user.id
        for note in Notification.query.filter_by(user_id=user.id).all():
            note.user_id = admin_user.id

    # Log a notification for the admin that this user deleted their account.
    if admin_user:
        admin_note = Notification(
            user_id=admin_user.id,
            message=f"User '{user.username}' deleted their account.",
        )
        db.session.add(admin_note)

    db.session.delete(user)
    db.session.commit()

    logout_user()
    flash("Your account has been deleted.", "info")
    return redirect(url_for("auth.login"))
