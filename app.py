from flask import Flask, request, redirect, url_for, render_template
import sqlite3
import base64

app = Flask(__name__)

def criar_tabela():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            categoria TEXT NOT NULL,
            imagem BLOB
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    produtos = listar_produtos()
    return render_template('index.html', produtos=produtos)

def salvar_produto(nome, preco, categoria, imagem_binaria):
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO produtos (nome, preco, categoria, imagem) 
        VALUES (?, ?, ?, ?)
    ''', (nome, float(preco), categoria, imagem_binaria))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    conn.close()
    produtos_com_imagem_base64 = [
        (produto[0], produto[1], produto[2], produto[3], base64.b64encode(produto[4] or b'').decode('utf-8'))
        for produto in produtos
    ]
    return produtos_com_imagem_base64

def remover_produto(produto_id):
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
    conn.commit()
    conn.close()

def atualizar_produto(produto_id, nome, preco, categoria, imagem_binaria):
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE produtos
        SET nome = ?, preco = ?, categoria = ?, imagem = ?
        WHERE id = ?
    ''', (nome, float(preco), categoria, imagem_binaria, produto_id))
    conn.commit()
    conn.close()

@app.route('/upload', methods=['POST'])
def upload():
    if 'imagem' not in request.files:
        return redirect(request.url)
    arquivo = request.files['imagem']
    nome = request.form['nome']
    preco = request.form['preco']
    categoria = request.form['categoria']
    
    if arquivo.filename == '':
        return redirect(request.url)
    
    if arquivo:
        imagem_binaria = arquivo.read()
        salvar_produto(nome, preco, categoria, imagem_binaria)
        return redirect(url_for('index'))
    return 'Falha no upload da imagem'

@app.route('/remover/<int:produto_id>', methods=['POST'])
def remover(produto_id):
    remover_produto(produto_id)
    return redirect(url_for('index'))

@app.route('/checkout', methods=['POST'])
def checkout():
    # Aqui você pode processar o pedido, salvar no banco de dados, etc.
    # Exemplo de como pegar os dados do pedido:
    pedido = request.json
    # Faça o que for necessário com o pedido (salvar no banco, enviar e-mail, etc.)
    return 'Pedido recebido', 200


@app.route('/editar/<int:produto_id>', methods=['GET', 'POST'])
def editar(produto_id):
    if request.method == 'GET':
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos WHERE id = ?', (produto_id,))
        produto = cursor.fetchone()
        conn.close()
        
        if produto:
            produto_com_imagem_base64 = (
                produto[0], produto[1], produto[2], produto[3], 
                base64.b64encode(produto[4] or b'').decode('utf-8')
            )
            return render_template('editar.html', produto=produto_com_imagem_base64)
        return 'Produto não encontrado', 404

    elif request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        categoria = request.form['categoria']
        arquivo = request.files.get('imagem')

        if arquivo and arquivo.filename != '':
            imagem_binaria = arquivo.read()
        else:
            conn = sqlite3.connect('ecommerce.db')
            cursor = conn.cursor()
            cursor.execute('SELECT imagem FROM produtos WHERE id = ?', (produto_id,))
            imagem_binaria = cursor.fetchone()[0]
            conn.close()
        
        atualizar_produto(produto_id, nome, preco, categoria, imagem_binaria)
        return redirect(url_for('index'))

if __name__ == '__main__':
    criar_tabela()
    app.run(debug=True)
