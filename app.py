from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "segredo-super-seguro"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tarefas.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


# MODELOS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    tasks = db.relationship(
        "Task",
        backref="owner",
        lazy=True,
        foreign_keys='Task.owner_id'   # <-- especifica a FK correta
    )
    assigned_tasks = db.relationship(
        "Task",
        backref="assigned_to_user",
        lazy=True,
        foreign_keys='Task.assigned_to_id'
    )

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="pendente")
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ROTAS DE AUTENTICAÇÃO
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Nome de usuário já existe.", "danger")
            return redirect(url_for("register"))
        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Usuário cadastrado! Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha incorretos.", "danger")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ROTAS PRINCIPAIS
@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required
def dashboard():
    filtro = request.args.get("filtro", "todas")
    usuarios = User.query.all()
    if filtro == "minhas":
        tarefas = Task.query.filter_by(owner_id=current_user.id).order_by(Task.id.desc()).all()
    elif filtro == "atribuídas":
        tarefas = Task.query.filter_by(assigned_to_id=current_user.id).order_by(Task.id.desc()).all()
    elif filtro in ["pendente", "em andamento", "concluída"]:
        tarefas = Task.query.filter(
            ((Task.owner_id == current_user.id) | (Task.assigned_to_id == current_user.id)) &
            (Task.status == filtro)
        ).order_by(Task.id.desc()).all()
    else:
        tarefas = Task.query.filter(
            (Task.owner_id == current_user.id) | (Task.assigned_to_id == current_user.id)
        ).order_by(Task.id.desc()).all()
    return render_template(
        "dashboard.html",
        tarefas=tarefas, usuarios=usuarios, filtro=filtro
    )

@app.route("/criar", methods=["GET", "POST"])
@login_required
def criar_tarefa():
    usuarios = User.query.all()
    if request.method == "POST":
        titulo = request.form["titulo"]
        descricao = request.form["descricao"]
        status = request.form["status"]
        atribuir = request.form.get("atribuir")
        tarefa = Task(
            title=titulo, description=descricao, status=status,
            owner_id=current_user.id,
            assigned_to_id=atribuir if atribuir != "" else None
        )
        db.session.add(tarefa)
        db.session.commit()
        flash("Tarefa criada com sucesso.", "success")
        return redirect(url_for("dashboard"))
    return render_template("criar_tarefa.html", usuarios=usuarios)

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_tarefa(id):
    tarefa = Task.query.get_or_404(id)
    if tarefa.owner_id != current_user.id and (tarefa.assigned_to_id != current_user.id):
        flash("Você não tem permissão para editar esta tarefa.", "danger")
        return redirect(url_for("dashboard"))
    usuarios = User.query.all()
    if request.method == "POST":
        tarefa.title = request.form["titulo"]
        tarefa.description = request.form["descricao"]
        tarefa.status = request.form["status"]
        atribuir = request.form.get("atribuir")
        tarefa.assigned_to_id = atribuir if atribuir != "" else None
        db.session.commit()
        flash("Tarefa atualizada.", "success")
        return redirect(url_for("dashboard"))
    return render_template("editar_tarefa.html", tarefa=tarefa, usuarios=usuarios)

@app.route("/excluir/<int:id>", methods=["POST"])
@login_required
def excluir_tarefa(id):
    tarefa = Task.query.get_or_404(id)
    if tarefa.owner_id != current_user.id:
        flash("Você não tem permissão para excluir esta tarefa.", "danger")
        return redirect(url_for("dashboard"))
    db.session.delete(tarefa)
    db.session.commit()
    flash("Tarefa excluída.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # cria as tabelas dentro do contexto do app
    app.run(debug=True)
