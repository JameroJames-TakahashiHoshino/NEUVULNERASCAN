from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app, abort
from flask_login import login_required, current_user
from .forms import ScanForm
from .models import Report, User
from . import db
import os
from .models import Notification
from src.scanner.engine import NeuVulneraScanEngine
from src.scanner.report import ReportGenerator
import json
from .utils import find_user_avatar


def _load_user_permissions():
        """Load user permissions from a JSON file in the instance folder.

        Structure:
            {
                "<user_id>": {"can_scan": true/false}
            }
        """
        path = os.path.join(current_app.instance_path, "user_permissions.json")
        if not os.path.exists(path):
                return {}
        try:
                with open(path, "r", encoding="utf-8") as f:
                        return json.load(f)
        except Exception:
                return {}


def _save_user_permissions(data):
        os.makedirs(current_app.instance_path, exist_ok=True)
        path = os.path.join(current_app.instance_path, "user_permissions.json")
        with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

main_bp = Blueprint("main", __name__, template_folder="templates")

@main_bp.route("/")
def index():
    return render_template("home.html")


@main_bp.route("/intro")
def intro():
    return render_template("intro.html")


@main_bp.route("/pre-dashboard")
@login_required
def pre_dashboard():
    # Admin users get a dedicated pre-dashboard handoff screen.
    if current_user.is_admin:
        return render_template("admin_pre_dashboard.html")
    return render_template("pre_dashboard.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Only show reports belonging to the current user
    reports = (
        Report.query
        .filter_by(user_id=current_user.id)
        .order_by(Report.created_at.desc())
        .limit(10)
        .all()
    )
    total_scans = len(reports)

    # Count how many of the user's recent scans use:
    #  - a Google-issued SSL certificate
    #  - a non-Google SSL certificate
    #  - no usable SSL certificate (errors / missing)
    ssl_google_count = 0
    ssl_other_count = 0
    ssl_none_count = 0
    for r in reports:
        if not r.filename_json:
            continue
        try:
            with open(r.filename_json, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        ssl_info = data.get("ssl") or {}

        # If there's no SSL info or it's only an error message,
        # treat this scan as having "no SSL".
        if not ssl_info or (isinstance(ssl_info, dict) and "error" in ssl_info):
            ssl_none_count += 1
            continue

        # Collect all text-like fields from the SSL section so we can
        # robustly detect any Google-related certificate (subject, issuer,
        # or subjectAltName containing "google").
        text_parts = []

        def _collect_text(obj):
            if isinstance(obj, str):
                text_parts.append(obj)
            elif isinstance(obj, list):
                for item in obj:
                    _collect_text(item)
            elif isinstance(obj, dict):
                for value in obj.values():
                    _collect_text(value)

        _collect_text(ssl_info.get("subject"))
        _collect_text(ssl_info.get("issuer"))
        _collect_text(ssl_info.get("subjectAltName"))

        combined = " ".join(text_parts).lower()
        if "google" in combined:
            ssl_google_count += 1
        else:
            ssl_other_count += 1

    return render_template(
        "dashboard.html",
        reports=reports,
        total_scans=total_scans,
        ssl_google_count=ssl_google_count,
        ssl_other_count=ssl_other_count,
        ssl_none_count=ssl_none_count,
    )


@main_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    users = User.query.order_by(User.id).all()
    total_users = len(users)
    total_reports = Report.query.count()

    perms = _load_user_permissions()

    users_data = []
    for u in users:
        avatar = find_user_avatar(current_app.static_folder, u.id)
        reports = sorted(u.reports, key=lambda r: r.created_at or 0, reverse=True)
        last_scan_time = reports[0].created_at if reports else None
        settings = perms.get(str(u.id), {})
        can_scan = settings.get("can_scan", True)

        users_data.append({
            "user": u,
            "avatar": avatar,
            "reports_count": len(reports),
            "last_scan_time": last_scan_time,
            "can_scan": can_scan,
        })

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_reports=total_reports,
        users_data=users_data,
    )


@main_bp.route("/admin/user/<int:user_id>")
@login_required
def admin_user_detail(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    avatar = find_user_avatar(current_app.static_folder, user.id)

    reports = (
        Report.query
        .filter_by(user_id=user.id)
        .order_by(Report.created_at.desc())
        .limit(20)
        .all()
    )
    notifications = (
        Notification.query
        .filter_by(user_id=user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )

    perms = _load_user_permissions()
    settings = perms.get(str(user.id), {})
    can_scan = settings.get("can_scan", True)

    return render_template(
        "admin_user_detail.html",
        user=user,
        avatar=avatar,
        reports=reports,
        notifications=notifications,
        can_scan=can_scan,
    )


@main_bp.route("/admin/user/<int:user_id>/toggle-scan", methods=["POST"])
@login_required
def admin_toggle_scan(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)

    # Prevent the admin from accidentally disabling themselves
    if user.id == current_user.id:
        flash("You cannot change your own scan permissions.", "warning")
        return redirect(url_for("main.admin_dashboard"))

    perms = _load_user_permissions()
    settings = perms.get(str(user.id), {})
    current = settings.get("can_scan", True)
    settings["can_scan"] = not current
    perms[str(user.id)] = settings
    _save_user_permissions(perms)

    if settings["can_scan"]:
        flash(f"Scan permission ENABLED for {user.username}.", "success")
    else:
        flash(f"Scan permission DISABLED for {user.username}.", "info")

    return redirect(url_for("main.admin_dashboard"))

@main_bp.route("/scan", methods=["GET","POST"])
@login_required
def scan():
    form = ScanForm()
    # Check whether this user is allowed to run scans (admin-controlled).
    perms = _load_user_permissions()
    user_settings = perms.get(str(current_user.id), {})
    if not user_settings.get("can_scan", True):
        flash("You do not have permission to run scans. Please contact the administrator.", "danger")
        return redirect(url_for("main.dashboard"))
    if form.validate_on_submit():
        target = form.target.data
        engine = NeuVulneraScanEngine(target)
        results = engine.run_all()

        # generate and save reports
        rgen = ReportGenerator(target, results)
        json_file = rgen.save_json()
        txt_file = rgen.save_txt()

        # store in DB, tied to the current user
        rep = Report(
            target=target,
            filename_json=json_file,
            filename_txt=txt_file,
            user_id=current_user.id,
        )
        db.session.add(rep)
        # Log notification for this user
        if current_user.is_authenticated:
            note = Notification(
                user_id=current_user.id,
                message=f"Scan completed for {target}",
            )
            db.session.add(note)
        db.session.commit()

        flash("Scan completed and saved.", "success")
        return redirect(url_for("main.report_view", report_id=rep.id))
    return render_template("scan.html", form=form)

@main_bp.route("/reports")
@login_required
def reports():
    page = request.args.get("page", 1, type=int)
    pagination = (
        Report.query
        .filter_by(user_id=current_user.id)
        .order_by(Report.created_at.desc())
        .paginate(page=page, per_page=10)
    )
    return render_template("reports.html", pagination=pagination)

@main_bp.route("/report/<int:report_id>")
@login_required
def report_view(report_id):
    # Regular users can only view their own reports.
    # Admins are allowed to view any report.
    if current_user.is_admin:
        rep = Report.query.filter_by(id=report_id).first_or_404()
    else:
        rep = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    # read json content
    try:
        with open(rep.filename_json, "r") as f:
            data = json.load(f)
    except Exception:
        data = {"error": "Could not load JSON."}
    return render_template("report_view.html", report=rep, data=data)

@main_bp.route("/report/delete/<int:report_id>", methods=["POST"])
@login_required
def report_delete(report_id):
    # Ensure users can only delete their own reports
    rep = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    # delete files if exist
    for fn in (rep.filename_json, rep.filename_txt):
        try:
            os.remove(fn)
        except Exception:
            pass
    db.session.delete(rep)
    # Log notification for this user
    if current_user.is_authenticated:
        note = Notification(
            user_id=current_user.id,
            message=f"Deleted report for {rep.target}",
        )
        db.session.add(note)
    db.session.commit()
    flash("Report deleted.", "info")
    return redirect(url_for("main.reports"))


@main_bp.route("/report/<int:report_id>/export/<string:fmt>")
@login_required
def report_export(report_id, fmt):
    """Export a report in various formats for download.

    Supported formats:
      - txt, json (existing stored files)
      - csv (simple tabular export of JSON data)
      - pdf (readable PDF with sections)
      - evtx (text-based export with .evtx extension, not a native Windows Event Log)
    """
    rep = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()

    fmt = (fmt or "").lower()

    # Direct file-based formats that already exist
    if fmt == "txt" and rep.filename_txt:
        path = os.path.abspath(rep.filename_txt)
        return send_from_directory(os.path.dirname(path), os.path.basename(path), as_attachment=True)
    if fmt == "json" and rep.filename_json:
        path = os.path.abspath(rep.filename_json)
        return send_from_directory(os.path.dirname(path), os.path.basename(path), as_attachment=True)

    # For derived formats, load the JSON results first
    try:
        with open(rep.filename_json, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        flash("Could not load JSON to generate export.", "error")
        return redirect(url_for("main.report_view", report_id=rep.id))

    base_abs = os.path.splitext(os.path.abspath(rep.filename_json))[0]
    target_path = None

    if fmt == "csv":
        import csv

        target_path = base_abs + ".csv"
        if not os.path.exists(target_path):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["section", "key", "value"])
                for section, value in data.items():
                    if isinstance(value, dict):
                        for key, v in value.items():
                            writer.writerow([section, key, json.dumps(v)])
                    elif isinstance(value, list):
                        for idx, v in enumerate(value):
                            writer.writerow([section, idx, json.dumps(v)])
                    else:
                        writer.writerow([section, "", json.dumps(value)])
    elif fmt == "pdf":
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        target_path = base_abs + ".pdf"
        if not os.path.exists(target_path):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            c = canvas.Canvas(target_path, pagesize=letter)
            width, height = letter
            textobject = c.beginText(40, height - 50)
            textobject.setFont("Helvetica", 10)

            created = rep.created_at.strftime("%Y-%m-%d %H:%M:%S") if rep.created_at else ""
            textobject.textLine("NEU VULNERA SCAN REPORT")
            textobject.textLine("========================")
            textobject.textLine(f"Target: {rep.target}")
            if created:
                textobject.textLine(f"Created: {created}")
            textobject.textLine("")

            for section, value in data.items():
                textobject.textLine("")
                textobject.textLine(f"--- {section.upper()} ---")
                for line in json.dumps(value, indent=2).splitlines():
                    textobject.textLine(line)
                    if textobject.getY() < 50:
                        c.drawText(textobject)
                        c.showPage()
                        textobject = c.beginText(40, height - 50)
                        textobject.setFont("Helvetica", 10)

            c.drawText(textobject)
            c.save()
    elif fmt == "evtx":
        # Note: this is a text-based export with a .evtx extension,
        # not a native Windows Event Log format.
        target_path = base_abs + ".evtx"
        if not os.path.exists(target_path):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                created = rep.created_at.strftime("%Y-%m-%d %H:%M:%S") if rep.created_at else ""
                f.write("NEU VULNERA SCAN REPORT (EVTX export - text)\n")
                f.write("=================================================\n")
                f.write(f"Target: {rep.target}\n")
                if created:
                    f.write(f"Created: {created}\n")
                f.write("\n")
                for section, value in data.items():
                    f.write(f"\n--- {section.upper()} ---\n")
                    f.write(json.dumps(value, indent=2))
                    f.write("\n")
    else:
        flash("Unsupported export format.", "error")
        return redirect(url_for("main.report_view", report_id=rep.id))

    if not target_path or not os.path.exists(target_path):
        flash("Could not generate the requested export.", "error")
        return redirect(url_for("main.report_view", report_id=rep.id))

    return send_from_directory(os.path.dirname(target_path), os.path.basename(target_path), as_attachment=True)

@main_bp.route("/download/<path:filename>")
@login_required
def download_file(filename):
    # serve files from reports/ directory
    directory = os.path.abspath("reports")
    return send_from_directory(directory, filename, as_attachment=True)
