from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
import email_validator
from forms import ClientForm, ServiceForm, TicketForm
from datetime import datetime
import sqlite3 
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'  # Substitua pelo seu URI SQLite correto
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos de Dados
class Client(db.Model):
    __tablename__ = 'Client'
    id_client = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False)
    client_type = db.Column(db.String(50), nullable=True)

class Service(db.Model):
    __tablename__ = 'Service'
    id_item = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(120), nullable=False)

class Ticket(db.Model):
    __tablename__ = 'Ticket'
    id_ticket = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_client = db.Column(db.Integer, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(100), nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    current_phase = db.Column(db.String, db.ForeignKey('subitems.subitem_type'), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    negotiation_value = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Em andamento")  # Status field

    def __repr__(self):
        return f'<Ticket {self.id_ticket}>'

class subitems(db.Model):
    __tablename__ = 'subitems'
    id_subitem = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_item = db.Column(db.Integer, db.ForeignKey('Service.id_item'), nullable=False)  # Chave estrangeira para a tabela Service
    subitem_type = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Subitem {self.id_subitem} - Type: {self.subitem_type}>'
    

# Chamada explícita para criar tabelas
with app.app_context():
    db.create_all()
    print("Banco de dados e tabelas criados com sucesso!")

@app.route('/')
def painel():
    clients = Client.query.all()
    return render_template('painel.html', clients=clients)

@app.route('/add_client', methods=['GET', 'POST'])
def add_client():
    form = ClientForm()
    if form.validate_on_submit():
        next_id = get_next_client_id()
        new_client = Client(
            id_client=next_id,
            client_name=form.name.data,
            client_email=form.email.data,
            client_phone=form.phone.data,
            client_type=form.client_type.data
        )
        db.session.add(new_client)
        db.session.commit()
        flash(f'Cliente adicionado com sucesso com o ID {next_id}!')
        return redirect(url_for('painel'))
    return render_template('add_client.html', form=form)

@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    form = ServiceForm()
    if form.validate_on_submit():
        next_id = get_next_service_id()
        new_service = Service(
            id_item=next_id,
            service_type=form.service_type.data
        )
        db.session.add(new_service)
        db.session.commit()
        flash('Serviço adicionado com sucesso!')
        return redirect(url_for('painel'))
    return render_template('add_service.html', form=form)

@app.route('/create_ticket', methods=['GET', 'POST'])
def create_ticket():
    form = TicketForm()

    # Obter os serviços disponíveis do banco de dados
    services = Service.query.all()
    form.service_id.choices = [(service.id_item, service.service_type) for service in services]

    if form.validate_on_submit():
        next_id = get_next_ticket_id()

        # Coletar o ID do subitem com status "Em andamento"
        selected_subitem_id = None
        service_id = form.service_id.data
        phases_status = request.form.getlist('phase_status')  # Coleta os status das fases
        status = "Em andamento"

        # Verifique os status das fases e pegue o ID do subitem correspondente
        for phase in phases_status:
            if phase == "Em andamento":
                # Aqui você deve mapear o id_item para o id_subitem
                # Supondo que a relação entre service_id e subitems é a seguinte
                subitem = subitems.query.filter_by(id_item=service_id).first()
                if subitem:
                    selected_subitem_type = subitem.subitem_type
                    break

    if form.validate_on_submit():
        next_id = get_next_ticket_id()  # Altere para usar get_next_ticket_id()
        


        new_ticket = Ticket(
            id_ticket=next_id,
            id_client=form.client_id.data,
            client_name=form.client_name.data,
            client_email=form.client_email.data,
            service_id=form.service_id.data,
            current_phase=selected_subitem_type,
            start_date=form.start_date.data,
            negotiation_value=form.negotiation_value.data,
            status = "Em andamento"
        )

        try:
            db.session.add(new_ticket)
            db.session.commit()
            flash(f'Ticket criado com sucesso com o ID {new_ticket.id_ticket}!')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar o ticket: {str(e)}')

        return redirect(url_for('painel'))

    return render_template('create_ticket.html', form=form, services=services)

@app.route('/board/<int:id_client>')
def board(id_client):
    client = Client.query.get(id_client)
    services = Service.query.all()
    return render_template('board.html', client=client, services=services)

@app.route('/update_client_type', methods=['POST'])
def update_client_type():
    for client_id in request.form:
        if client_id.startswith('client_type_'):
            client_type = request.form[client_id]
            id_client = client_id.split('_')[2]  # Extrai o ID do cliente
            
            # Atualiza o tipo de cliente no banco de dados
            # Assumindo que você tenha uma função no seu modelo que atualiza o cliente
            update_client_type_in_db(id_client, client_type)
    
    flash('Tipos de cliente atualizados com sucesso!')
    return redirect(url_for('painel'))

def update_client_type_in_db(client_id, client_type):
    # Exemplo de como atualizar um cliente no banco de dados
    client = db.session.query(Client).filter(Client.id_client == client_id).first()
    if client:
        client.client_type = client_type
        db.session.commit()

def get_next_client_id():
    last_client = Client.query.order_by(Client.id_client.desc()).first()
    if last_client:
        return last_client.id_client + 1
    else:
        return 1000
    
def get_next_service_id():
    last_service = Service.query.order_by(Service.id_item.desc()).first()
    if last_service:
        return last_service.id_item + 1
    else:
        return 1
    
def get_next_ticket_id():
    last_ticket = Ticket.query.order_by(Ticket.id_ticket.desc()).first()
    if last_ticket:
        return max(last_ticket.id_ticket + 1, 10000)  # Garante que o ID comece a partir de 2000
    else:
        return 10000
    
@app.route('/view_tickets')
def view_tickets():
    tickets = Ticket.query.all()  # Busca todos os tickets no banco de dados
    return render_template('view_ticket.html', tickets=tickets)

@app.route('/update_ticket/<int:ticket_id>', methods=['POST'])
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket:
        # Atualiza os campos com base nos dados do formulário
        ticket.current_phase = request.form['current_phase']
        ticket.status = request.form['status']
        
        # Persistindo as alterações no banco de dados
        db.session.commit()
        
        # Redireciona para a página de gestão de tickets ou painel
        return redirect(url_for('view_tickets'))
    else:
        return "Ticket não encontrado", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)