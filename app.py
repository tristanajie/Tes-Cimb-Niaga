import os
from datetime import date, datetime

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import case
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    due_date = db.Column(db.Date, nullable=True)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def parse_due_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError("Format tanggal tenggat tidak valid.") from None


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    )
    if test_config:
        app.config.update(test_config)
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY belum diatur. Salin .env.example menjadi .env dan isi nilainya.")
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("DATABASE_URL belum diatur. Salin .env.example menjadi .env dan isi nilainya.")

    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        status_filter = request.args.get("status", "all")
        query = Task.query
        if status_filter == "pending":
            query = query.filter_by(is_completed=False)
        elif status_filter == "completed":
            query = query.filter_by(is_completed=True)
        else:
            status_filter = "all"

        tasks = query.order_by(
            Task.is_completed.asc(),
            case((Task.due_date.is_(None), 1), else_=0),
            Task.due_date.asc(),
            Task.created_at.desc(),
        ).all()
        return render_template("index.html", tasks=tasks, status_filter=status_filter)

    @app.post("/tasks")
    def create_task():
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title:
            flash("Judul tugas wajib diisi.", "error")
            return redirect(url_for("index"))
        if len(title) > 200:
            flash("Judul tugas maksimal 200 karakter.", "error")
            return redirect(url_for("index"))

        try:
            due_date = parse_due_date(request.form.get("due_date", "").strip())
            db.session.add(Task(title=title, description=description, due_date=due_date))
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "error")
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.exception("Gagal menyimpan tugas baru.")
            flash("Tugas gagal disimpan. Periksa koneksi database dan coba lagi.", "error")
        else:
            flash("Tugas berhasil ditambahkan.", "success")
        return redirect(url_for("index"))

    @app.get("/tasks/<int:task_id>/edit")
    def edit_task(task_id):
        task = db.get_or_404(Task, task_id)
        return render_template("edit.html", task=task)

    @app.post("/tasks/<int:task_id>/edit")
    def update_task(task_id):
        task = db.get_or_404(Task, task_id)
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title:
            flash("Judul tugas wajib diisi.", "error")
            return redirect(url_for("edit_task", task_id=task.id))
        if len(title) > 200:
            flash("Judul tugas maksimal 200 karakter.", "error")
            return redirect(url_for("edit_task", task_id=task.id))

        try:
            task.due_date = parse_due_date(request.form.get("due_date", "").strip())
            task.title = title
            task.description = description
            db.session.commit()
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "error")
            return redirect(url_for("edit_task", task_id=task.id))
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.exception("Gagal memperbarui tugas %s.", task.id)
            flash("Perubahan gagal disimpan. Periksa koneksi database dan coba lagi.", "error")
            return redirect(url_for("edit_task", task_id=task.id))

        flash("Tugas berhasil diperbarui.", "success")
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/toggle")
    def toggle_task(task_id):
        task = db.get_or_404(Task, task_id)
        task.is_completed = not task.is_completed
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.exception("Gagal mengubah status tugas %s.", task.id)
            flash("Status tugas gagal diperbarui.", "error")
        else:
            flash("Status tugas berhasil diperbarui.", "success")
        return redirect(url_for("index"))

    @app.post("/tasks/<int:task_id>/delete")
    def delete_task(task_id):
        task = db.get_or_404(Task, task_id)
        try:
            db.session.delete(task)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.exception("Gagal menghapus tugas %s.", task.id)
            flash("Tugas gagal dihapus.", "error")
        else:
            flash("Tugas berhasil dihapus.", "success")
        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    create_app().run(debug=os.getenv("FLASK_DEBUG") == "1")
