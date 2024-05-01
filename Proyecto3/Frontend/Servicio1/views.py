from django.shortcuts import render
from django.http import JsonResponse
import requests
import xmltodict
import json
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings
import os




def api_call(url):
    response = requests.get(url)
    print(response)
    return response

def inicio(request):
    return render(request, 'inicio.html')

@require_http_methods(["GET", "POST"])
def grabarTransaccion(request):
    if request.method == 'POST' and request.FILES.get('xml_file'):
        xml_file = request.FILES['xml_file']
        files = {'file': xml_file}
        response = requests.post('http://localhost:8123/grabarTransaccion', files=files)
        xml_data = response.text
        print(xml_data)
        data = json.loads(json.dumps(xmltodict.parse(xml_data)))
        if not 'estado' in data["respuesta"]:
            data = {'respuesta': {'xml': xml_data, 'json': data}}
        return JsonResponse(data=data, status=200)
    return JsonResponse(data={'data':{"estado": "Error", "mensaje": "Debe de cargar un archivo"}}, status=200)

@require_http_methods(["GET", "POST"])
def grabarConfiguracion(request):
    if request.method == 'POST' and request.FILES.get('xml_file'):
        xml_file = request.FILES['xml_file']
        files = {'file': xml_file}
        response = requests.post('http://localhost:8123/grabarConfiguracion', files=files)
        xml_data = response.text
        print(xml_data)
        data = json.loads(json.dumps(xmltodict.parse(xml_data)))
        if not 'estado' in data["respuesta"]:
            data = {'respuesta': {'xml': xml_data, 'json': data}}
        return JsonResponse(data=data, status=200)
    return JsonResponse(data={'data':{"estado": "Error", "mensaje": "Debe de cargar un archivo"}}, status=200)

@require_http_methods(["GET"])
def limpiarDatos(request):
    response = requests.post('http://localhost:8123/limpiarDatos')
    xml_data = response.text
    print(xml_data)
    return JsonResponse(data=json.loads(json.dumps(xmltodict.parse(xml_data))), status=200)

@require_http_methods(["GET", "POST"])
def devolverEstadoCuenta(request):
    if request.method == 'POST': 
        nit = ""
        if request.POST.get('nit'): nit = "?nit=" + request.POST.get('nit')
        response = requests.get('http://localhost:8123/devolverEstadoCuenta' + nit)
        xml_data = response.text
        print(xml_data)
        return JsonResponse(data=xml_data, status=200, safe=False)

@require_http_methods(["GET", "POST"])
def devolverResumenPagos(request):
    if request.method == 'POST' and request.POST.get('fecha'):
        fecha = "?fecha=" + request.POST.get('fecha')
        response = requests.get('http://localhost:8123/devolverResumenPagos' + fecha)
        xml_data = response.text
        print(xml_data)
        return JsonResponse(data=xml_data, status=200, safe=False)
    return JsonResponse(data={'data':{"estado": "Error", "mensaje": "Debe de ingresar una fecha"}}, status=200)

@require_http_methods(["GET"])
def getClientes(request):
    response = requests.get('http://localhost:8123/getClientes')
    data = response.json()
    print(data)
    return JsonResponse(data)

def abrir_pdf(request):
    return render(request, 'inicio.html')

def open_file(request):
    file_path = os.path.join(settings.MEDIA_ROOT, "Ensayo_P3_202200220.pdf")
    print(file_path)
    print("holis desde openfile")
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404

def mostrar_datos_estudiante(request):
    return render(request, 'inicio.html')

