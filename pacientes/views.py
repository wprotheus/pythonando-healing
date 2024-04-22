from django.shortcuts import render, redirect
from medicos.models import DadosMedico, EspecialidadesMedicas, DatasAbertas, isMedico
from .models import Consulta, Documento
from datetime import datetime
from django.contrib.messages import constants
from django.contrib.messages import add_message

# Create your views here.

# Home

def home(request):
    if request.method == "GET":
       medicos = DadosMedico.objects.all()
       medico_filtrar = request.GET.get('medico')
       especialidades_filtrar = request.GET.getlist('especialidades')
       
       if medico_filtrar:
           medicos = medicos.filter(nome__icontains = medico_filtrar)
        
       if especialidades_filtrar:
          medicos = medicos.filter(especialidade_id__in = especialidades_filtrar)

       especialidades = EspecialidadesMedicas.objects.all()
       return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades, 'isMedico': isMedico(request.user)})

# Escolhendo horário

def escolher_horario(request, id_dados_medicos):
    if request.method == "GET":
        medico = DadosMedico.objects.get(id = id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user = medico.user).filter(data__gte = datetime.now()).filter(agendado = False)
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'isMedico': isMedico(request.user)})
    
# Agendar horário

def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
        horario_agendado = Consulta(
        paciente = request.user,
        data_aberta = data_aberta)

        horario_agendado.save()        
        data_aberta.agendado = True
        data_aberta.save()

        add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')
        return redirect('/pacientes/minhas_consultas/')

# Minhas consultas

def minhas_consultas(request):
    if request.method == "GET":       
        minhas_consultas = Consulta.objects.filter(paciente = request.user).filter(data_aberta__data__gte = datetime.now())
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'isMedico': isMedico(request.user)})
    
# Consulta

def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id = id_consulta)
        dado_medico = DadosMedico.objects.get(user = consulta.data_aberta.user)
        documentos = Documento.objects.filter(consulta = consulta)
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'isMedico': isMedico(request.user), 'documentos': documentos})

