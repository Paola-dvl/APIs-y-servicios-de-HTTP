"""
URL configuration for Frontend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from Servicio1 import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.inicio, name='Inicio'),
    path('grabarTransaccion/', views.grabarTransaccion, name='grabarTransaccion'),
    path('grabarConfiguracion/', views.grabarConfiguracion, name='grabarConfiguracion'),
    path('limpiarDatos/', views.limpiarDatos, name='limpiarDatos'),
    path('devolverEstadoCuenta/', views.devolverEstadoCuenta, name='devolverEstadoCuenta'),
    path('devolverResumenPagos/', views.devolverResumenPagos, name='devolverResumenPagos'),
    path('getClientes/', views.getClientes, name='getClientes'),
    path('abrir_pdf/', views.abrir_pdf, name='abrir_pdf'),
    path('mostrar_datos_estudiante/', views.mostrar_datos_estudiante, name='mostrar_datos_estudiante'),
    path('open_file/', views.open_file, name='open_file'),
    
]

