from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import estadoVehiculo
import datetime
import csv


# Create your views here.
def index(request):
    return render(request,"iotVehiculos/index.html")

def registrarDatos(request):
    datoMensaje = str(request.GET.get('mensaje'))
    datoTiempo = str(request.GET.get('tiempo'))
    if datoMensaje == 'N':
        datoMensaje = '0'
    elif datoMensaje == 'Y':
        datoMensaje = '1'
    else:
        return JsonResponse({ 'resp':'ok' })
    tiempoRegistro = datetime.datetime.strptime(datoTiempo,"%Y-%m-%dT%H:%M:%S")
    estadoVehiculo(registroTiempo=tiempoRegistro,registroInformacion=datoMensaje).save()
    return JsonResponse({ 'resp':'ok' })

def enviarDatos(request):
    arregloTiempos = []
    arregloInfos = []
    hora_actual = datetime.datetime.now() - datetime.timedelta(hours=5)
    hora_anterior = hora_actual - datetime.timedelta(hours=1)
    registrosEnvio = estadoVehiculo.objects.all().order_by('registroTiempo').filter(registroTiempo__range = [hora_anterior.strftime("%Y-%m-%d %H:%M:%S"),hora_actual.strftime("%Y-%m-%d %H:%M:%S")])
    if len(registrosEnvio) == 0:
        try:
            last_register = estadoVehiculo.objects.all().order_by('-registroTiempo').first()
            ultimo_valor = last_register.registroInformacion
        except:
            ultimo_valor = '0'
        arregloTiempos.append(datetime.datetime.strftime(hora_anterior,"%Y-%m-%d %H:%M:%S"))
        arregloInfos.append(ultimo_valor)
        arregloTiempos.append(datetime.datetime.strftime(hora_actual,"%Y-%m-%d %H:%M:%S"))
        arregloInfos.append(ultimo_valor)
    else:
        try:
            registro_previo = estadoVehiculo.objects.get(id=str(int(registrosEnvio.first().id) - 1))
        except:
            registro_previo = registrosEnvio.first()
        
        ultimo_registro = registrosEnvio.last()
        
        arregloTiempos.append(datetime.datetime.strftime(hora_anterior,"%Y-%m-%d %H:%M:%S"))
        arregloInfos.append(registro_previo.registroInformacion)

        for reg in registrosEnvio:
            arregloTiempos.append(datetime.datetime.strftime(reg.registroTiempo,"%Y-%m-%d %H:%M:%S"))
            arregloInfos.append(reg.registroInformacion)
        
        arregloInfos.append(ultimo_registro.registroInformacion)
        arregloTiempos.append(datetime.datetime.strftime(hora_actual,"%Y-%m-%d %H:%M:%S"))
    
    return JsonResponse({
        'informacionVehiculo':arregloInfos,
        'registroTiempos':arregloTiempos
    })

def descargarDatos(request):
    output = []
    response = HttpResponse (content_type='text/csv')
    writer = csv.writer(response)
    query_set = estadoVehiculo.objects.all().order_by('-registroTiempo')

    #Header
    writer.writerow(['Fecha', 'Hora', 'Encendido'])
    dato_ant = '0'
    for entry in query_set:
        dato = entry.registroInformacion
        timestamp = entry.registroTiempo
        if dato != dato_ant:
            day_str = datetime.datetime.strftime(timestamp,"%Y-%m-%d")
            hour_str = datetime.datetime.strftime(timestamp - datetime.timedelta(seconds=1),"%H:%M:%S")
            output.append([day_str, hour_str, dato_ant])
        day_str = datetime.datetime.strftime(timestamp,"%Y-%m-%d")
        hour_str = datetime.datetime.strftime(timestamp,"%H:%M:%S")
        output.append([day_str, hour_str, dato])
        dato_ant = dato
        
    #CSV Data
    writer.writerows(output)
    return response
