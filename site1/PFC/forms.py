from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, validators, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, data_required, ValidationError
from PFC.models import Usuario
from flask_login import current_user


class FormLogIn(FlaskForm):
    email = StringField("Digite seu nome de gmail: ", validators=[DataRequired(), Email()])
    senha = PasswordField("Digite sua senha: ", validators=[data_required(), Length(6, 20)])
    botao_login = SubmitField("Login")
    lembrar_dados = BooleanField("Lembrar dados para próximo Loguin?")


class FormCriarConta(FlaskForm):
    criar_nome_usuario = StringField("Digite um nome de usuário: ", validators=[DataRequired(), Length(4, 15)])
    criar_email = StringField("Digite seu email: ", validators=[Email(), DataRequired()])
    criar_senha = PasswordField("Crie uma senha: ", validators=[DataRequired(), Length(6, 20)])
    confirmar_senha = PasswordField("Confirme sua senha: ", validators=[DataRequired(), EqualTo("criar_senha")])
    botao_criar_conta = SubmitField("Criar conta")

    def validate_criar_email(self, criar_email):
        usuario = Usuario.query.filter_by(email=criar_email.data).first()
        if usuario:
            raise ValidationError("E-mail já cadastrado. Faça login ou use outro e-mail.")

    def validate_email(self, criar_email):
        email_usuario = criar_email.data.lower()
        dominios_validos = ("@gmail.com", "@hotmail.com", "@outlook.com", "@escola.pr.gov.br")

        if not email_usuario.data.endswith(dominios_validos):
            raise ValidationError("E-mail inválido. Digite um e-mail válido.")

class FormEditarConta(FlaskForm):
    editar_nome_usuario = StringField("Digite um novo nome: ", validators=[DataRequired(), Length(4, 15)])
    editar_email = StringField("Digite o novo email: ", validators=[Email(), DataRequired()])
    descricao = StringField('Descrição / Bio')
    botao_criar_conta = SubmitField("Salvar Edições")

    def validate_editar_email(self, editar_email):
        if current_user.email != editar_email.data:
            usuario = Usuario.query.filter_by(email=editar_email.data).first()
            dominios_validos = ("@gmail.com", "@hotmail.com", "@outlook.com", "@escola.pr.gov.br")

            if usuario or not editar_email.data.endswith(dominios_validos):
                raise ValidationError("E-mail inválido ou já cadastrado. Digite um e-mail válido.")

class FormEditarFoto(FlaskForm):
    foto_perfil = FileField("Atualizar foto de perfil", validators=[FileAllowed(["jpeg", "jpg", "png"])])
    botao_submit = SubmitField("Salvar Imagem")


class FormCriarPost(FlaskForm):
    titulo = StringField("Titulo do Post: ", validators=[DataRequired(), Length(3, 50)])
    corpo = TextAreaField("Corpo do Post: ", validators=[DataRequired(), Length(0, 500)])
    imagem = FileField('Adicionar Imagem ou GIF', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    video = FileField('Adicionar Vídeo (MP4/WebM)', validators=[FileAllowed(['mp4', 'webm'])])
    criar_post = SubmitField("Postar/Editar")