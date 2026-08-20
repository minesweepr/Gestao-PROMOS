from app import app
from flask import render_template

@app.route('/')
def index():
    return render_template('teste.html')

@app.route('/presenca')
def presenca():
    return render_template('presenca.html')

@app.route('/planilhas')
def planilhas():
    return render_template('planilhas.html')

@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

@app.route('/informacoes_usuario')
def informacoes_usuario():
    return render_template('informacoes_usuario.html')

@app.route('/avaliacoes_usuario')
def avaliacoes_usuario():
    return render_template('avaliacoes_usuario.html')

@app.route('/editar_usuario')
def editar_usuario():
    return render_template('editar_usuario.html')

@app.route('/cadastrar_usuario')
def cadastrar_usuario():
    return render_template('cadastrar_usuario.html')