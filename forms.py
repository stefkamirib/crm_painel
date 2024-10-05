from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email

# Formulário para Adicionar Cliente
class ClientForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(message="Nome é obrigatório.")])
    email = StringField('Email', validators=[DataRequired(message="Email é obrigatório."), Email(message="Email inválido.")])
    phone = StringField('Telefone', validators=[DataRequired(message="Telefone é obrigatório.")])
    client_type = SelectField('Tipo de Cliente', choices=[
        ('Lead', 'Lead'),
        ('Lead Qualificado', 'Lead Qualificado'),
        ('Cliente', 'Cliente')
    ], validators=[DataRequired()])
    submit = SubmitField('Adicionar Cliente')

# Formulário para Adicionar Serviço
class ServiceForm(FlaskForm):
    service_type = StringField('Tipo de Serviço', validators=[DataRequired(message="Tipo de serviço é obrigatório.")])
    submit = SubmitField('Adicionar Serviço')

class TicketForm(FlaskForm):
    client_id = StringField('ID Cliente', validators=[DataRequired()])
    client_name = StringField('Nome do Cliente', validators=[DataRequired(message="Nome do cliente é obrigatório.")])
    client_email = StringField('Email do Cliente', validators=[DataRequired(message="Email é obrigatório."), Email(message="Email inválido.")])
    service_id = SelectField('Serviço', coerce=int, choices=[], validators=[DataRequired(message="Serviço é obrigatório.")])
    start_date = DateField('Data de Início', format='%Y-%m-%d', validators=[DataRequired(message="Data de início é obrigatória.")])
    negotiation_value = DecimalField('Valor da Negociação', places=2, validators=[DataRequired(message="Valor da negociação é obrigatório.")])
    submit = SubmitField('Criar Ticket')
    