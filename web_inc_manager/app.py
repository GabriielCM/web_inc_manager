import os
import json
import hashlib
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv
from io import BytesIO
from PIL import Image
from models import db, User, INC, LayoutSetting, Fornecedor, RotinaInspecao
from config import Config
import re
import chardet


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Adicionar filtro from_json ao Jinja2
app.jinja_env.filters['from_json'] = lambda s: json.loads(s)

# Adicionar filtro enumerate ao Jinja2
def jinja_enumerate(iterable):
    return enumerate(iterable)

app.jinja_env.filters['enumerate'] = jinja_enumerate

def validate_item_format(item):
    pattern = r'^[A-Z]{3}\.\d{5}$'
    return re.match(pattern, item) is not None

# Função auxiliar para salvar arquivos
def save_file(file):
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return f"uploads/{filename}"

@app.route('/set_crm_token', methods=['GET', 'POST'])
@login_required
def set_crm_token():
    if request.method == 'POST':
        crm_link = request.form['crm_link']
        token_match = re.search(r'token=([a-f0-9]+)', crm_link)
        
        if token_match:
            token = token_match.group(1)
            session['crm_token'] = token
            session['inspecao_crm_token'] = token  # Atualiza o token da inspeção também
            flash('Token CRM atualizado com sucesso!', 'success')
            return redirect(url_for('visualizar_registros_inspecao'))
        else:
            flash('Link CRM inválido. Verifique o link.', 'danger')
            return redirect(url_for('visualizar_registros_inspecao'))
    
    return render_template('set_crm_token.html')

@app.route('/gerenciar_fornecedores', methods=['GET', 'POST'])
@login_required
def gerenciar_fornecedores():
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('main_menu'))

    if request.method == 'POST':
        action = request.form.get('action')
        fornecedor_id = request.form.get('fornecedor_id')
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id) if fornecedor_id else None

        if action == 'delete':
            db.session.delete(fornecedor)
            db.session.commit()
            flash('Fornecedor excluído com sucesso!')
        elif action == 'update':
            fornecedor.razao_social = request.form['razao_social']
            fornecedor.cnpj = request.form['cnpj']
            fornecedor.fornecedor_logix = request.form['fornecedor_logix']
            db.session.commit()
            flash('Fornecedor atualizado com sucesso!')

    fornecedores = Fornecedor.query.all()
    return render_template('gerenciar_fornecedores.html', fornecedores=fornecedores)

@app.route('/cadastrar_fornecedor', methods=['GET', 'POST'])
@login_required
def cadastrar_fornecedor():
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('main_menu'))

    if request.method == 'POST':
        razao_social = request.form['razao_social']
        cnpj = request.form['cnpj']
        fornecedor_logix = request.form['fornecedor_logix']

        # Validação simples do CNPJ (pode ser melhorada)
        if Fornecedor.query.filter_by(cnpj=cnpj).first():
            flash('CNPJ já cadastrado.')
            return render_template('cadastrar_fornecedor.html')

        fornecedor = Fornecedor(
            razao_social=razao_social,
            cnpj=cnpj,
            fornecedor_logix=fornecedor_logix
        )
        db.session.add(fornecedor)
        db.session.commit()
        flash('Fornecedor cadastrado com sucesso!')
        return redirect(url_for('gerenciar_fornecedores'))

    return render_template('cadastrar_fornecedor.html')

@app.route('/rotina_inspecao', methods=['GET', 'POST'])
@login_required
def rotina_inspecao():
    # Check if CRM token is set
    if 'crm_token' not in session:
        flash('Você precisa importar o token do CRM primeiro.')
        return redirect(url_for('set_crm_token'))
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If no file is selected, filename will be empty
        if file.filename == '':
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
        
        # Check file extension
        if not file.filename.lower().endswith('.lst'):
            flash('Apenas arquivos .lst são permitidos')
            return redirect(request.url)
        
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse the .lst file
            registros = ler_arquivo_lst(filepath)
            
            if registros:
                # Store the parsed records in the session
                session['inspecao_registros'] = registros
                # Store the current CRM token with the records
                session['inspecao_crm_token'] = session['crm_token']
                flash(f'Foram importados {len(registros)} registros.')
                return redirect(url_for('visualizar_registros_inspecao'))
            else:
                flash('Nenhum registro válido foi importado.')
                return redirect(request.url)
        
        except Exception as e:
            flash(f'Erro ao importar arquivo: {str(e)}')
            return redirect(request.url)
        finally:
            # Clean up the temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return render_template('rotina_inspecao.html')

@app.route('/visualizar_registros_inspecao', methods=['GET', 'POST'])
@login_required
def visualizar_registros_inspecao():
    registros = session.get('inspecao_registros', [])
    
    if not registros:
        flash('Nenhum registro para inspeção.')
        return redirect(url_for('rotina_inspecao'))
    
    scroll_position = None
    if request.method == 'POST':
        action = request.form.get('action')
        item_index = int(request.form.get('item_index'))
        ar = int(request.form.get('ar'))
        scroll_position = request.form.get('scroll_position')  # Obter a posição de rolagem
        
        print(f"POST recebido - Action: {action}, AR: {ar}, Item Index: {item_index}, Scroll Position: {scroll_position}")
        
        registros_no_grupo = [r for r in registros if r['num_aviso'] == ar]
        print(f"Registros no grupo AR {ar}: {len(registros_no_grupo)} itens")
        
        if 0 <= item_index < len(registros_no_grupo):
            registro_global_index = registros.index(registros_no_grupo[item_index])
            if action == 'inspecionar':
                registros[registro_global_index]['inspecionado'] = True
                registros[registro_global_index]['adiado'] = False
            elif action == 'adiar':
                registros[registro_global_index]['inspecionado'] = False
                registros[registro_global_index]['adiado'] = True
            print(f"Atualizado registro {registros[registro_global_index]['item']}: {registros[registro_global_index]}")
            session['inspecao_registros'] = registros
    
    # Agrupar registros por AR
    grupos_ar = {}
    for registro in registros:
        ar = registro['num_aviso']
        if ar not in grupos_ar:
            grupos_ar[ar] = []
        grupos_ar[ar].append(registro)
    
    grupos_ar_ordenados = sorted(grupos_ar.items(), key=lambda x: x[0])
    
    # Passar scroll_position como parâmetro na URL
    if scroll_position:
        return redirect(url_for('visualizar_registros_inspecao', scroll_position=scroll_position))
    
    return render_template('visualizar_registros_inspecao.html', grupos_ar=grupos_ar_ordenados)

@app.route('/listar_rotinas_inspecao')
@login_required
def listar_rotinas_inspecao():
    rotinas = RotinaInspecao.query.all()
    # Converter registros de JSON para Python para cada rotina
    for rotina in rotinas:
        rotina.registros_python = json.loads(rotina.registros)
    return render_template('listar_rotinas_inspecao.html', rotinas=rotinas)

@app.route('/salvar_rotina_inspecao', methods=['POST'])
@login_required
def salvar_rotina_inspecao():
    registros = session.get('inspecao_registros', [])
    
    if not registros:
        flash('Nenhum registro para salvar.')
        return redirect(url_for('rotina_inspecao'))
    
    print("Registros na sessão antes da validação:", registros)
    
    for registro in registros:
        inspecionado = registro.get('inspecionado', False)
        adiado = registro.get('adiado', False)
        print(f"Registro: {registro['item']}, Inspecionado: {inspecionado}, Adiado: {adiado}")
        if not inspecionado and not adiado:
            flash('Todos os registros devem ser inspecionados ou adiados antes de salvar a rotina.', 'danger')
            return redirect(url_for('visualizar_registros_inspecao'))
    
    rotina = RotinaInspecao(
        inspetor_id=current_user.id,
        registros=json.dumps(registros)
    )
    db.session.add(rotina)
    db.session.commit()
    
    flash('Rotina de inspeção salva com sucesso!', 'success')
    session.pop('inspecao_registros', None)
    return redirect(url_for('main_menu'))

def ler_arquivo_lst(caminho):
    """
    Lê o arquivo .lst, filtra e processa os registros.
    Baseado na implementação original da classe InspecaoARFrame.
    """
    registros = []
    
    # Detect encoding
    with open(caminho, "rb") as f:
        conteudo = f.read()
    encoding = chardet.detect(conteudo)['encoding']
    
    try:
        with open(caminho, "r", encoding=encoding) as arquivo:
            for linha in arquivo:
                linha_str = linha.strip()
                if not linha_str:
                    continue
                
                # Split by multiple spaces
                campos = re.split(r"\s{2,}", linha_str)
                
                # Validate and process columns
                if len(campos) < 9:
                    continue
                
                # Consolidate columns if more than 9
                while len(campos) > 9:
                    campos[3] = campos[3] + " " + campos[4]
                    del campos[4]
                
                try:
                    data_entrada = campos[0]
                    num_aviso = int(campos[1])
                    
                    # Parse item code
                    parts_item = re.split(r"\s+", campos[2], maxsplit=1)
                    item_code = parts_item[1].strip() if len(parts_item) > 1 else parts_item[0].strip()
                    
                    descricao = campos[3]
                    
                    # Parse quantity
                    qtd_str = campos[5].replace(",", ".")
                    qtd_recebida = float(qtd_str)
                    
                    # Parse supplier
                    splitted_6 = re.split(r"\s+", campos[6], maxsplit=1)
                    fornecedor = splitted_6[1] if len(splitted_6) == 2 else "DESCONHECIDO"
                    
                    # Parse O.C.
                    oc_str = campos[-1].strip()
                    oc_int = int(oc_str)
                    
                    # Skip if O.C. is 0
                    if oc_int == 0:
                        continue
                    
                    registro = {
                        "fornecedor": fornecedor,
                        "razao_social": fornecedor,
                        "item": item_code,
                        "descricao": descricao,
                        "num_aviso": num_aviso,
                        "qtd_recebida": qtd_recebida,
                        "inspecionado": False,
                        "adiado": False,
                        "oc_value": oc_int
                    }
                    registros.append(registro)
                
                except Exception:
                    continue
        
        return registros
    
    except Exception as e:
        # Log the error or handle it appropriately
        print(f"Erro ao ler o arquivo: {e}")
        return []


@app.context_processor
def inject_settings():
    settings = {s.element: s for s in LayoutSetting.query.all()}
    return dict(settings=settings)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# Database Initialization
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="Gabriel").first():
        admin = User(username="Gabriel", password=hash_password("85629367"), is_admin=True)
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
@login_required
def cadastrar_usuario():
    if not current_user.is_admin:
        flash('Acesso negado. Somente administradores podem cadastrar novos usuários.', 'danger')
        return redirect(url_for('main_menu'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = 'is_admin' in request.form

        # Verificar se o usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe. Escolha outro.', 'danger')
            return render_template('cadastrar_usuario.html')

        # Criar novo usuário
        hashed_password = hash_password(password)
        new_user = User(username=username, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('gerenciar_logins'))

    return render_template('cadastrar_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_menu'))  # Redireciona se já estiver logado

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == hash_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main_menu'))
        flash('Usuário ou senha incorretos.')
    else:
        if 'next' in request.args:
            flash('Por favor, faça login para acessar essa página.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/main_menu')
@login_required
def main_menu():
    return render_template('main_menu.html')


@app.route('/cadastro_inc', methods=['GET', 'POST'])
@login_required
def cadastro_inc():
    representantes = ["Gabriel Rodrigues da Silva", "Marcos Vinicius Gomes Teixeira", "Aleksandro Carvalho Leão"]
    fornecedores = Fornecedor.query.all()  # Lista de fornecedores do banco de dados

    if request.method == 'POST':
        nf = int(request.form['nf'])
        representante = request.form['representante']
        fornecedor = request.form['fornecedor']
        item = request.form['item'].upper()
        quantidade_recebida = int(request.form['quantidade_recebida'])
        quantidade_com_defeito = int(request.form['quantidade_com_defeito'])

        if not validate_item_format(item):
            flash('Formato do item inválido. Deve ser 3 letras maiúsculas, ponto e 5 dígitos, ex: MPR.02199')
            return render_template('cadastro_inc.html', representantes=representantes, fornecedores=fornecedores)

        if quantidade_com_defeito > quantidade_recebida:
            flash('Quantidade com defeito não pode ser maior que a quantidade recebida.')
            return render_template('cadastro_inc.html', representantes=representantes, fornecedores=fornecedores)

        # Gerar número OC sequencial
        last_inc = INC.query.order_by(INC.oc.desc()).first()
        new_oc = (last_inc.oc + 1) if last_inc and last_inc.oc else 1

        inc = INC(
            nf=nf,
            data=datetime.today().strftime("%d-%m-%Y"),
            representante=representante,
            fornecedor=fornecedor,
            item=item,
            quantidade_recebida=quantidade_recebida,
            quantidade_com_defeito=quantidade_com_defeito,
            descricao_defeito=request.form.get('descricao_defeito', ''),
            urgencia=request.form.get('urgencia', 'Moderada'),
            acao_recomendada=request.form.get('acao_recomendada', ''),
            fotos=json.dumps([]),
            oc=new_oc,
            status="Em andamento"
        )

        # Adicionar fotos, se houver
        if 'fotos' in request.files:
            files = request.files.getlist('fotos')
            fotos = []
            for file in files:
                if file and allowed_file(file.filename):
                    filepath = save_file(file)
                    fotos.append(filepath)
            inc.fotos = json.dumps(fotos)

        db.session.add(inc)
        db.session.commit()
        flash('INC cadastrada com sucesso!')
        return redirect(url_for('visualizar_incs'))

    return render_template('cadastro_inc.html', representantes=representantes, fornecedores=fornecedores)

@app.route('/visualizar_incs')
@login_required
def visualizar_incs():
    # Obter parâmetros de filtro
    nf = request.args.get('nf')
    item = request.args.get('item')
    fornecedor = request.args.get('fornecedor')
    status = request.args.get('status')

    # Construir consulta com filtros
    query = INC.query
    if nf:
        query = query.filter_by(nf=int(nf))
    if item:
        query = query.filter(INC.item.ilike(f'%{item}%'))
    if fornecedor:
        query = query.filter(INC.fornecedor.ilike(f'%{fornecedor}%'))
    if status:
        query = query.filter_by(status=status)

    incs = query.all()
    return render_template('visualizar_incs.html', incs=incs)

@app.route('/detalhes_inc/<int:inc_id>')
@login_required
def detalhes_inc(inc_id):
    inc = INC.query.get_or_404(inc_id)
    fotos = json.loads(inc.fotos)
    return render_template('detalhes_inc.html', inc=inc, fotos=fotos)

@app.route('/editar_inc/<int:inc_id>', methods=['GET', 'POST'])
@login_required
def editar_inc(inc_id):
    inc = INC.query.get_or_404(inc_id)
    representantes = ["Gabriel Rodrigues da Silva", "Marcos Vinicius Gomes Teixeira", "Aleksandro Carvalho Leão"]
    fotos = json.loads(inc.fotos) if inc.fotos else []

    if request.method == 'POST':
        # Atualizar campos existentes
        item = request.form['item'].upper()
        if not validate_item_format(item):
            flash('Formato do item inválido. Deve ser 3 letras maiúsculas, ponto e 5 dígitos, ex: MPR.02199')
            return render_template('editar_inc.html', inc=inc, representantes=representantes, fotos=fotos)
        
        quantidade_recebida = int(request.form['quantidade_recebida'])
        quantidade_com_defeito = int(request.form['quantidade_com_defeito'])
        if quantidade_com_defeito > quantidade_recebida:
            flash('Quantidade com defeito não pode ser maior que a quantidade recebida.')
            return render_template('editar_inc.html', inc=inc, representantes=representantes, fotos=fotos)

        inc.representante = request.form['representante']
        inc.fornecedor = request.form['fornecedor']
        inc.item = item
        inc.quantidade_recebida = quantidade_recebida
        inc.quantidade_com_defeito = quantidade_com_defeito
        inc.descricao_defeito = request.form['descricao_defeito']
        inc.urgencia = request.form['urgencia']
        inc.acao_recomendada = request.form['acao_recomendada']
        inc.status = request.form['status']

        # Adicionar novas fotos
        if 'fotos' in request.files:
            files = request.files.getlist('fotos')
            for file in files:
                if file and allowed_file(file.filename):
                    filepath = save_file(file)
                    fotos.append(filepath)

        inc.fotos = json.dumps(fotos)
        db.session.commit()
        flash('INC atualizada com sucesso!')
        return redirect(url_for('visualizar_incs'))

    return render_template('editar_inc.html', inc=inc, representantes=representantes, fotos=fotos)

@app.route('/remover_foto_inc/<int:inc_id>/<path:foto>', methods=['POST'])
@login_required
def remover_foto_inc(inc_id, foto):
    inc = INC.query.get_or_404(inc_id)
    fotos = json.loads(inc.fotos) if inc.fotos else []
    if foto in fotos:
        fotos.remove(foto)
        # Opcional: remover o arquivo físico
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(foto))
        if os.path.exists(filepath):
            os.remove(filepath)
    inc.fotos = json.dumps(fotos)
    db.session.commit()
    flash('Foto removida com sucesso!')
    return redirect(url_for('editar_inc', inc_id=inc_id))

@app.route('/excluir_inc/<int:inc_id>', methods=['POST'])
@login_required
def excluir_inc(inc_id):
    inc = INC.query.get_or_404(inc_id)
    db.session.delete(inc)
    db.session.commit()
    flash('INC excluída com sucesso!')
    return redirect(url_for('visualizar_incs'))

@app.route('/expiracao_inc')
@login_required
def expiracao_inc():
    incs = INC.query.all()
    today = datetime.today().date()
    vencidas = []
    for inc in incs:
        inc_date = datetime.strptime(inc.data, "%d-%m-%Y").date()
        delta_days = {"leve": 45, "moderada": 20, "crítico": 10}.get(inc.urgencia.lower(), 45)
        expiration_date = inc_date + timedelta(days=delta_days)
        if today > expiration_date:
            days_overdue = (today - expiration_date).days
            vencidas.append((inc, days_overdue))
    return render_template('expiracao_inc.html', vencidas=vencidas)

@app.route('/gerenciar_logins', methods=['GET', 'POST'])
@login_required
def gerenciar_logins():
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('main_menu'))
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        user = User.query.get_or_404(user_id)
        if action == 'delete' and user.username != current_user.username:
            db.session.delete(user)
            db.session.commit()
            flash('Usuário excluído com sucesso!')
        elif action == 'update':
            new_password = request.form.get('new_password')
            if new_password:
                user.password = hash_password(new_password)
            user.is_admin = 'is_admin' in request.form
            db.session.commit()
            flash('Usuário atualizado com sucesso!')
    users = User.query.all()
    return render_template('gerenciar_logins.html', users=users)

@app.route('/editar_layout', methods=['GET', 'POST'])
@login_required
def editar_layout():
    if not current_user.is_admin:
        flash('Acesso negado.')
        return redirect(url_for('main_menu'))
    if request.method == 'POST':
        element = request.form['element']
        setting = LayoutSetting.query.filter_by(element=element).first()
        if not setting:
            setting = LayoutSetting(element=element)
            db.session.add(setting)
        setting.foreground = request.form['foreground']
        setting.background = request.form['background']
        setting.font_family = request.form['font_family']
        setting.font_size = int(request.form['font_size'])
        db.session.commit()
        flash('Layout atualizado com sucesso!')
    settings = {s.element: s for s in LayoutSetting.query.all()}
    return render_template('editar_layout.html', settings=settings)

@app.route('/export_csv')
@login_required
def export_csv():
    incs = INC.query.all()
    output = BytesIO()
    writer = csv.writer(output)
    writer.writerow(['nf', 'data', 'representante', 'fornecedor', 'item', 'quantidade_recebida', 'quantidade_com_defeito', 'descricao_defeito', 'urgencia', 'acao_recomendada', 'fotos', 'status'])
    for inc in incs:
        writer.writerow([inc.nf, inc.data, inc.representante, inc.fornecedor, inc.item, inc.quantidade_recebida, inc.quantidade_com_defeito, inc.descricao_defeito, inc.urgencia, inc.acao_recomendada, inc.fotos, inc.status])
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='incs.csv')

@app.route('/export_pdf/<int:inc_id>')
@login_required
def export_pdf(inc_id):
    inc = INC.query.get_or_404(inc_id)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    c.setFont("Helvetica", 12)
    details = [
        f"NF-e: {inc.nf}", f"Data: {inc.data}", f"Representante: {inc.representante}",
        f"Fornecedor: {inc.fornecedor}", f"Item: {inc.item}", f"Qtd. Recebida: {inc.quantidade_recebida}",
        f"Qtd. com Defeito: {inc.quantidade_com_defeito}", f"Descrição do Defeito: {inc.descricao_defeito}",
        f"Urgência: {inc.urgencia}", f"Ação Recomendada: {inc.acao_recomendada}", f"Status: {inc.status}"
    ]
    for line in details:
        c.drawString(50, y, line)
        y -= 20
    fotos = json.loads(inc.fotos)
    if fotos:
        c.showPage()
        x, y = 50, height - 220
        for foto in fotos:
            if os.path.exists(foto):
                c.drawImage(foto, x, y, width=200, height=200, preserveAspectRatio=True)
                x += 220
                if x > width - 200:
                    x = 50
                    y -= 220
                    if y < 50:
                        c.showPage()
                        y = height - 220
    c.save()
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'inc_{inc.nf}.pdf')

if __name__ == '__main__':
    app.run(debug=True)
