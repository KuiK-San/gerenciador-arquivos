from flask import Flask, request, jsonify, render_template, redirect, session, send_file, url_for
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return '<a href="/gerenciador-arquivos">Gerenciador de arquvos</a>'

@app.route('/gerenciador-arquivos', defaults={'path': ''}, methods=['GET'])
@app.route('/gerenciador-arquivos/<path:path>', methods=['GET'])
def gerenciador(path):

    data_max = request.args.get('dataMax', None)
    data_min = request.args.get('dataMin', None)
    ordem = request.args.get('ordem', 'A-Z')

    base_path = os.path.join('static', 'folders')
    
    if os.path.isfile(os.path.join(base_path, path)):
        if os.path.exists(os.path.join(base_path, path)):
            return send_file(os.path.join(base_path, path))
        else:
            error_message = "O arquivo não existe."
            session['error'] = error_message
            return redirect(url_for('index'))

    elif path == '':
        pastas = os.listdir(base_path)
    else:
        path_to_check = os.path.join(base_path, path)
        if os.path.exists(path_to_check) and os.path.isdir(path_to_check):
            pastas = os.listdir(path_to_check)
        else:
            error_message = "O diretório não existe."
            session['error'] = error_message
            return redirect(url_for('index'))

    error_message = session.get('error')
    pastasComp = []

    for pasta in pastas:
        arquivo = os.path.isfile(os.path.join(base_path, path, pasta))

        if not arquivo:
            itens = len(os.listdir(os.path.join(base_path, path, pasta)))
        else:
            itens = False

        criacao = os.path.getctime(os.path.join(base_path, path, pasta))
        criacao = datetime.fromtimestamp(criacao).strftime('%Y-%m-%d %H:%M:%S')

        if (data_min is None or criacao >= data_min) and (data_max is None or criacao <= data_max):
            pastasComp.append({'nome': pasta, 'path': f'{path}/{pasta}', 'isFile': arquivo, 'itens': itens, 'criacao': criacao})

    if ordem == 'Z-A':
        pastasComp = sorted(pastasComp, key=lambda x: x['nome'], reverse=True)
    elif ordem == 'data-asc':
        pastasComp = sorted(pastasComp, key=lambda x: x['criacao'])
    elif ordem == 'data-desc':
        pastasComp = sorted(pastasComp, key=lambda x: x['criacao'], reverse=True)
    else:
        pastasComp = sorted(pastasComp, key=lambda x: x['nome'])

    if error_message:
        session.pop('error', None)
        return render_template('gerenciador.html', error_message=error_message, path=path)
    if path == '':
        return render_template('gerenciador.html', pastas=pastasComp, path=path)

    return render_template('gerenciador.html', pastas=pastasComp, enviar=True, path=path)


# Rota para criar uma pasta
@app.route('/create-folder', methods=['GET'])
def create_folder():
    folder_name = request.args.get('name')
    path = request.args.get('path')
    
    if path != 'undefined':
        folder_name = os.path.join(path, folder_name)

    # Verifica se o nome da pasta foi fornecido
    if not folder_name:
        session['error'] = 'Nome da pasta é necessário'
        return redirect('/')
    
    folder_path = os.path.join('static','folders', folder_name)

    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        session['error'] = f'Erro ao criar a pasta: {str(e)}'
        return redirect('/')
    
    if path == '':
        return redirect(f'/gerenciador-arquivos')


    return redirect(f'/gerenciador-arquivos/{path}')

@app.route('/create-file', methods=['POST'])
def create_file():
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado'
    
    file = request.files['file']
    path = request.form['path']

    if file.filename == '':
        return 'Arquivos sem nome'
    
    file.save(os.path.join('./static/folders', path, file.filename))
    return redirect(f'/gerenciador-arquivos/{path}')




if __name__ == '__main__':
    app.run(debug=True)
