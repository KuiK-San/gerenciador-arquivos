from flask import Flask, request, jsonify, render_template, redirect, session
import os

app = Flask(__name__)


@app.route('/gerenciador-arquivos/', defaults={'path': ''}, methods=['GET'])
@app.route('/gerenciador-arquivos/<path:path>', methods=['GET'])
def index(path):
    print(path)
    if path == '':
        pastas = os.listdir('./folders')
    else:
        pastas = os.listdir(f'./folders/{path}')

    error_message = session.get('error')
    pastasComp = []

    for pasta in pastas:
        pastasComp.append({'nome': pasta, 'path': f'{path}/{pasta}'})

    if error_message:
        session.pop('error', None)
        return render_template('gerenciador.html', error_message=error_message)
    if path == '':
      return render_template('gerenciador.html', pastas=pastasComp)
      

    return render_template('gerenciador.html', pastas=pastasComp, enviar=True)

# Rota para criar uma pasta
@app.route('/create-folder', methods=['GET'])
def create_folder():
    folder_name = request.args.get('name')
    print(folder_name)
    
    # Verifica se o nome da pasta foi fornecido
    if not folder_name:
        session['error'] = 'Nome da pasta é necessário'
        return redirect('/')
    
    # Define o caminho da pasta e cria
    folder_path = os.path.join('folders', folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        session['error'] = 'A pasta já existe'
    
    return redirect('/gerenciador-arquivos')

if __name__ == '__main__':
    app.run(debug=True)
