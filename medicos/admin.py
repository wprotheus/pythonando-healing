from django.contrib import admin
from .models import EspecialidadesMedicas, DadosMedico, DatasAbertas

# Register your models here.

admin.site.register(EspecialidadesMedicas)
admin.site.register(DadosMedico)
admin.site.register(DatasAbertas)
