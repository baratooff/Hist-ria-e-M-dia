from flask import render_template, flash, redirect, url_for, request
from PFC.forms import FormCriarConta, FormLogIn, FormEditarConta, FormEditarFoto, FormCriarPost
from PFC import app, database, bcrypt
from PFC.models import Usuario, Post
from flask_login import logout_user, login_user, current_user, login_required
import os
from secrets import token_hex
from PIL import Image

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/posts")
def postagens():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("postagens.html", posts=posts)

@app.route("/contatos")
def contatos():
    lista_contatos = Usuario.query.all()
    return render_template("contatos.html", lista_contatos=lista_contatos)

@app.route("/login", methods=["GET", "POST"])
def login():
    form_log_in = FormLogIn()
    if form_log_in.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_log_in.email.data).first()

        if usuario and bcrypt.check_password_hash(usuario.senha, form_log_in.senha.data):
            login_user(usuario, remember=form_log_in.lembrar_dados.data)
            flash(f"Login feito no gmail {form_log_in.email.data}", "alert-success")
            par_next = request.args.get("next")

            if par_next and par_next != url_for("login") and par_next != "/login":
                return redirect(par_next)
            else:
                return redirect(url_for("home"))
        else:
            flash("Email invalido ou senha incorreta", "alert_danger")
    return render_template("loguin.html", form_login=form_log_in)

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha_cript = bcrypt.generate_password_hash(form_criarconta.criar_senha.data).decode("utf-8")
        usuario = Usuario(username=form_criarconta.criar_nome_usuario.data, email=form_criarconta.criar_email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario)
        flash(f"Conta criada no gmail {form_criarconta.criar_email.data}", "alert-primary")
        return redirect(url_for("home"))
    return render_template("cadastro.html", form_criarconta=form_criarconta)

@app.route("/usuarios")
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template("usuarios.html", lista_usuarios=lista_usuarios)

@app.route("/sair")
@login_required
def sair():
    logout_user()
    flash(f"Logout efetuado com sucesso", "alert-primary")
    return redirect(url_for("home"))

@app.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for("static", filename=f"fotos_perfil/{current_user.foto_perfil}")
    posts = Post.query.filter_by(id_usuario=current_user.id).order_by(Post.id.desc()).all()
    return render_template("perfil.html", foto_perfil=foto_perfil, posts=posts)


def salvar_midia(arquivo, pasta_destino):
    codigo = token_hex(8)
    nome_original, extensao = os.path.splitext(arquivo.filename)
    nome_ficheiro = codigo + extensao.lower()
    caminho_completo = os.path.join(app.root_path, 'static', pasta_destino, nome_ficheiro)
    arquivo.save(caminho_completo)
    return nome_ficheiro


@app.route("/post/criar", methods=["GET", "POST"])
@login_required
def postar():
    form_criar_post = FormCriarPost()
    if form_criar_post.validate_on_submit():
        nome_imagem = None
        nome_video = None
        if form_criar_post.imagem.data:
            nome_imagem = salvar_midia(form_criar_post.imagem.data, 'fotos_posts')
        if form_criar_post.video.data:
            nome_video = salvar_midia(form_criar_post.video.data, 'videos_posts')

        post = Post(
            titulo=form_criar_post.titulo.data,
            corpo=form_criar_post.corpo.data,
            autor=current_user,
            imagem=nome_imagem,
            video=nome_video
        )
        database.session.add(post)
        database.session.commit()
        flash("Post feito com sucesso.", "alert-primary")
        return redirect(url_for("home"))
    return render_template("criar_post.html", form_criarpost=form_criar_post)

@app.route("/perfil/editar_perfil", methods=["GET", "POST"])
@login_required
def editar_perfil():
    editar_conta = FormEditarConta()
    if editar_conta.validate_on_submit():
        current_user.email = editar_conta.editar_email.data
        current_user.username = editar_conta.editar_nome_usuario.data
        current_user.descricao = editar_conta.descricao.data
        database.session.commit()
        flash(f"Perfil editado com sucesso!", "alert-primary")
        return redirect(url_for("perfil"))

    elif request.method == "GET":
        editar_conta.editar_nome_usuario.data = current_user.username
        editar_conta.editar_email.data = current_user.email
        editar_conta.descricao.data = current_user.descricao

    return render_template("editar_perfil.html", form_editar_conta=editar_conta)


def salvar_foto(imagem):
    codigo = token_hex(8)
    nome_original, extensao = os.path.splitext(imagem.filename)
    nome_ficheiro = codigo + extensao.lower()
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_ficheiro)

    if extensao.lower() == '.gif':
        imagem.save(caminho_completo)
    else:
        tamanho = (300, 300)
        img = Image.open(imagem)
        img.thumbnail(tamanho)
        img.save(caminho_completo)

    return nome_ficheiro


@app.route("/perfil/editar/editar_foto", methods=["GET", "POST"])
@login_required
def editar_foto_perfil():
    form_editar_imagem = FormEditarFoto()

    if form_editar_imagem.validate_on_submit():
        if form_editar_imagem.foto_perfil.data:
            nome_foto = salvar_foto(form_editar_imagem.foto_perfil.data)
            current_user.foto_perfil = nome_foto
            database.session.commit()
            flash("Foto de perfil atualizada com sucesso!", "alert-success")
            return redirect(url_for("perfil"))

    return render_template("editar_imagem.html", form_editarimagem=form_editar_imagem)

@app.route("/aviso")
@login_required
def aviso():
    return render_template("aviso.html")


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
@login_required
def exibir_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == "GET":
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            if form.imagem.data:
                post.imagem = salvar_midia(form.imagem.data, 'fotos_posts')
            if form.video.data:
                post.video = salvar_midia(form.video.data, 'videos_posts')
            database.session.commit()
            flash("Post editado com sucesso!", "alert-success")
            return redirect(url_for("postagens"))
    else:
        form = None

    return render_template("post.html", post=post, form=form)

@app.route("/post/<int:post_id>/excluir", methods=["POST"])
@login_required
def excluir_post(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user != post.autor:
        flash("Não tens permissão para excluir este post.", "alert-danger")
        return redirect(url_for("postagens"))

    database.session.delete(post)
    database.session.commit()
    flash("Post excluído com sucesso!", "alert-danger")
    return redirect(url_for("home"))