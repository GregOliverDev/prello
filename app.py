from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, login_user, logout_user
from models import db, Workspace, Board, List, Card, Member
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///prello.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/")
def index():
    workspaces = Workspace.query.all()
    return render_template("index.html", workspaces=workspaces)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if Member.query.filter_by(username=username).first():
            return render_template('register.html', error="Usuário já existe.")
        member = Member(username=username)
        member.set_password(password)
        db.session.add(member)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        member = Member.query.filter_by(username=username).first()
        if member and member.check_password(password):
            login_user(member)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Usuário ou senha inválidos.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/workspace/create", methods=["GET", "POST"])
def create_workspace():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            workspace = Workspace(name=name)
            db.session.add(workspace)
            db.session.commit()
            return redirect(url_for("index"))
    return render_template("workspace_create.html")


@app.route("/workspace/<int:workspace_id>")
def workspace_detail(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    boards = Board.query.filter_by(workspace_id=workspace.id).all()
    return render_template("workspace_detail.html", workspace=workspace, boards=boards)


@app.route("/workspace/<int:workspace_id>/board/create", methods=["GET", "POST"])
def create_board(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if request.method == "POST":
        name = request.form.get("name")
        background = request.form.get("background") or "#e5e5e5"
        visibility = request.form.get("visibility") or "private"
        if name:
            board = Board(
                name=name,
                background=background,
                visibility=visibility,
                workspace_id=workspace.id,
            )
            db.session.add(board)
            db.session.commit()
            return redirect(url_for("workspace_detail", workspace_id=workspace.id))
    return render_template("board_create.html", workspace=workspace)


@app.route("/workspace/<int:workspace_id>/edit", methods=["GET", "POST"])
def edit_workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if request.method == "POST":
        workspace.name = request.form.get("name")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("workspace_edit.html", workspace=workspace)


@app.route("/workspace/<int:workspace_id>/delete", methods=["POST"])
def delete_workspace(workspace_id):
    workspace = Workspace.query.get_or_404(workspace_id)
    if workspace.boards:  # Se o workspace tem boards associados
        error = "Não é possível excluir o workspace. Primeiro exclua todos os boards que pertencem a este workspace."
        workspaces = Workspace.query.all()
        return render_template("index.html", workspaces=workspaces, error=error)
    db.session.delete(workspace)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/board/<int:board_id>")
def board_detail(board_id):
    board = Board.query.get_or_404(board_id)
    lists = List.query.filter_by(board_id=board.id).order_by(List.position).all()
    return render_template("board_detail.html", board=board, lists=lists)


@app.route("/board/<int:board_id>/list/create", methods=["GET", "POST"])
def create_list(board_id):
    board = Board.query.get_or_404(board_id)
    if request.method == "POST":
        name = request.form.get("name")
        position = request.form.get("position") or 1
        if name:
            new_list = List(
                name=name, position=position, board_id=board.id, closed=False
            )
            db.session.add(new_list)
            db.session.commit()
            return redirect(url_for("board_detail", board_id=board.id))
    return render_template("list_create.html", board=board)


@app.route("/board/<int:board_id>/edit", methods=["GET", "POST"])
def edit_board(board_id):
    board = Board.query.get_or_404(board_id)
    if request.method == "POST":
        board.name = request.form.get("name")
        board.background = request.form.get("background") or "#e5e5e5"
        board.visibility = request.form.get("visibility") or "private"
        db.session.commit()
        return redirect(url_for("workspace_detail", workspace_id=board.workspace_id))
    return render_template("board_edit.html", board=board)


@app.route("/board/<int:board_id>/delete", methods=["POST"])
def delete_board(board_id):
    board = Board.query.get_or_404(board_id)
    if board.lists:  # Se o board tem listas associadas
        workspace_id = board.workspace_id
        error = "Não é possível excluir o board. Primeiro exclua todas as listas que pertencem a este board."
        boards = Board.query.filter_by(workspace_id=workspace_id).all()
        workspace = Workspace.query.get_or_404(workspace_id)
        return render_template(
            "workspace_detail.html", workspace=workspace, boards=boards, error=error
        )
    workspace_id = board.workspace_id
    db.session.delete(board)
    db.session.commit()
    return redirect(url_for("workspace_detail", workspace_id=workspace_id))


@app.route("/list/<int:list_id>/card/create", methods=["GET", "POST"])
def create_card(list_id):
    lista = List.query.get_or_404(list_id)
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        position = request.form.get("position") or 1
        if name:
            card = Card(
                name=name,
                description=description,
                position=position,
                list_id=lista.id,
                archived=False,
            )
            db.session.add(card)
            db.session.commit()
            return redirect(url_for("board_detail", board_id=lista.board_id))
    return render_template("card_create.html", lista=lista)


@app.route("/list/<int:list_id>/edit", methods=["GET", "POST"])
def edit_list(list_id):
    lista = List.query.get_or_404(list_id)
    if request.method == "POST":
        lista.name = request.form.get("name")
        lista.position = request.form.get("position") or 1
        db.session.commit()
        return redirect(url_for("board_detail", board_id=lista.board_id))
    return render_template("list_edit.html", lista=lista)


@app.route("/list/<int:list_id>/delete", methods=["POST"])
def delete_list(list_id):
    lista = List.query.get_or_404(list_id)
    if lista.cards:  # Se a lista tem cards associados
        # Retorne para o board com uma mensagem de erro
        board_id = lista.board_id
        error = "Não é possível excluir a lista. Primeiro exclua todos os cards que pertencem a ela."
        # Você pode passar a mensagem de erro para o template do board
        lists = List.query.filter_by(board_id=board_id).order_by(List.position).all()
        board = Board.query.get_or_404(board_id)
        return render_template(
            "board_detail.html", board=board, lists=lists, error=error
        )
    board_id = lista.board_id
    db.session.delete(lista)
    db.session.commit()
    return redirect(url_for("board_detail", board_id=board_id))


@app.route("/card/<int:card_id>")
def card_detail(card_id):
    card = Card.query.get_or_404(card_id)
    return render_template("card_detail.html", card=card)


@app.route("/card/<int:card_id>/edit", methods=["GET", "POST"])
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    if request.method == "POST":
        card.name = request.form.get("name")
        card.description = request.form.get("description")
        card.position = request.form.get("position") or 1
        db.session.commit()
        return redirect(url_for("card_detail", card_id=card.id))
    return render_template("card_edit.html", card=card)


@app.route("/card/<int:card_id>/delete", methods=["POST"])
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    board_id = card.list.board_id
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for("board_detail", board_id=board_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False)
