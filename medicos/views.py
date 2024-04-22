from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EspecialidadesMedicas, DadosMedico, DatasAbertas, isMedico
from django.contrib.messages import constants
from django.contrib.messages import add_message
from datetime import datetime, timedelta
from pacientes.models import Consulta, Documento

# Cadastrar médico

@login_required
def cadastro_medico(request):
    if isMedico(request):
        add_message(request, constants.WARNING, "Usuário já cadastrado.")
        return redirect('/medicos/abrir_horario')

    if request.method == "GET":
        especialidadesMedicas = EspecialidadesMedicas.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidadesMedicas': especialidadesMedicas})
    elif request.method == "POST":        
        dadoMedico = DadosMedico(
            crm = request.POST.get('crm'),
            crmID = request.FILES.get('crmid'),
            nomeMedico = request.POST.get('nome'),
            cep = request.POST.get('cep'),
            logradouro = request.POST.get('logradouro'),
            rua = request.POST.get('rua'),
            numero = request.POST.get('numero'),
            bairro = request.POST.get('bairro'),
            cidade = request.POST.get('cidade'),
            estado = request.POST.get('estado'),
            rg = request.FILES.get('rg'),
            foto = request.FILES.get('foto'),
            especialidade_id = request.POST.get('especialidade'),
            descricao = request.POST.get('descricao'),
            valor_consulta = request.POST.get('valor_consulta'),
            user = request.user
        )
        dadoMedico.save()
        add_message(request, constants.SUCCESS, 'Médico cadastrado com sucesso.')
        return redirect('/medicos/abrir_horario')
    
# Abrir agenda médica

@login_required
def abrir_horario(request):
    if not isMedico(request):
        add_message(request, constants.WARNING, "Acesso não permitido à abertura de agenda médica.")
        return redirect('/usuarios/logout')
    
    if request.method == "GET":
        dadosMedicos = DadosMedico.objects.get(user = request.user)
        datasAbertas = DatasAbertas.objects.filter(user = request.user)
        return render(request, 'abrir_horario.html', {'dadosMedicos': dadosMedicos, 'datasAbertas': datasAbertas, 'isMedico': isMedico(request.user)})
    elif request.method == "POST":
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, "%Y-%m-%dT%H:%M")
        
        if data_formatada <= datetime.now():
            add_message(request, constants.WARNING, 'Data deve ser maior ou igual a data atual.')
            return redirect('/medicos/abrir_horario')
        
        horario_abrir = DatasAbertas(
            data = data,
            user = request.user)
        
    horario_abrir.save()

    add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso.')
    return redirect('/medicos/abrir_horario')


def consultas_medico(request):
    if not isMedico(request.user):
        add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
 
    hoje = datetime.now().date()

    consultas_hoje = Consulta.objects.filter(data_aberta__user = request.user).filter(data_aberta__data__gte = hoje).filter(data_aberta__data__lt = hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in = consultas_hoje.values('id')).filter(data_aberta__user = request.user)
    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'isMedico': isMedico(request.user)})

# Visualizar consultas na área médico

def consulta_area_medico(request, id_consulta):
    if not isMedico(request.user):
        add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
 
    if request.method == "GET":
        consulta = Consulta.objects.get(id = id_consulta)
        return render(request, 'consulta_area_medico.html', {'consulta': consulta,'is_medico': isMedico(request.user)}) 
    elif request.method == "POST":
                    # Inicializa a consulta + link da chamada
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')
        if consulta.status == 'C':
            add_message(request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        elif consulta.status == "F":
            add_message(request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
    consulta.link = link
    consulta.status = 'I'
    consulta.save()
    add_message(request, constants.SUCCESS, 'Consulta inicializada com sucesso.')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

# Finalizar consulta

def finalizar_consulta(request, id_consulta):
    if not isMedico(request.user):
        add_message(request, constants.WARNING, "Somente médico podem encerrar consultas.")
        return redirect('/usuarios/logout')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        add_message(request, constants.ERROR, "Essa consulta não é sua.")
        return redirect('/medicos/consultas_medico/')
        
    consulta.save_base == 'F'
    consulta.save()
    return redirect('/medicos/consultas_medico/')
 
 # Adicionar documentos
 
def add_documento(request, id_consulta):
    if not isMedico(request.user):
        add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id = id_consulta)
    
    if consulta.data_aberta.user != request.user:
        add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')
    if not documento:
        add_message(request, constants.WARNING, 'Adicione o documento.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    documento = Documento(
                consulta = consulta,
                titulo = titulo,
                documento = documento)
    documento.save()
    add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
    documentos = Documento.objects.filter(consulta = consulta)
    return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'documentos': documentos,'isMedico': isMedico(request.user)}) 