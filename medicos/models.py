from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Especialidade Médica

class EspecialidadesMedicas(models.Model):
    nomeEspecialidade = models.CharField(max_length=98)
    iconeEspecialidade = models.ImageField(upload_to='icones', null=True, blank=True)

    def __str__(self):
        return self.nomeEspecialidade

# Dados do médico

class DadosMedico(models.Model):
    crm = models.IntegerField()
    nomeMedico = models.CharField(max_length=98)
    logradouro = models.CharField(max_length=44)
    rua = models.CharField(max_length=62)
    bairro = models.CharField(max_length=44)
    numero = models.IntegerField()
    cep = models.CharField(max_length=10)
    cidade = models.CharField(max_length=62)
    estado = models.CharField(max_length=44)
    rg = models.ImageField(upload_to='docs_pessoais')    
    crmID = models.ImageField(upload_to='crm')
    foto = models.ImageField(upload_to='foto_perfil')
    descricao = models.TextField()
    valor_consulta = models.FloatField(default=530)
    especialidade = models.ForeignKey(EspecialidadesMedicas, on_delete=models.DO_NOTHING, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.user.username

# É médico

def isMedico(user):
     return DadosMedico.objects.filter(user = user).exists()

# Próxima data
    
def proximaDataAberta(self):
        return DatasAbertas.objects.filter(user = self.user).filter(data__gt = datetime.now()).filter(agendado = False).order_by('data').first()
    
# Agenda médica

class DatasAbertas(models.Model):
    data = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    agendado = models.BooleanField(default=False)

    def __str__(self):
        return str(self.data)
    