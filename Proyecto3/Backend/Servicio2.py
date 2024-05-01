from flask import Flask, make_response, request
import xmltodict
import json
from datetime import datetime, timedelta
import calendar
from flask import Flask, render_template, send_file, jsonify
import re


class Informacion:
    class Cliente:
        def __init__(self, nit, nombre):
            self.nit = nit
            self.nombre = nombre

    class Banco:
        def __init__(self, codigo, nombre):
            self.codigo = codigo
            self.nombre = nombre

    class Factura:
        def __init__(self, numero_factura, nit_cliente, fecha, valor):
            self.numero_factura = numero_factura
            self.nit_cliente = nit_cliente
            self.fecha = fecha
            self.valor = valor

    class Pago:
        def __init__(self, codigo_banco, fecha, nit_cliente, valor):
            self.codigo_banco = codigo_banco
            self.fecha = fecha
            self.nit_cliente = nit_cliente
            self.valor = valor

    def __init__(self):
        self.clientes = []
        self.bancos = []
        self.facturas = []
        self.pagos = []
        self.registro_creacion = {"clientes": 0, "bancos": 0}
        self.registro_actualizacion = {"clientes": 0, "bancos": 0}
        self.registro_facturas = {"creadas": 0, "duplicadas": 0, "con_error": 0}
        self.registro_pagos = {"creados": 0, "duplicados": 0, "con_error": 0}

    def agregar_cliente(self, nit, nombre):
        try:
            for cliente in self.clientes:
                if cliente.nit == nit:
                    cliente.nombre = nombre
                    self.registro_actualizacion["clientes"] += 1
                    return
            patron = r'\b([a-zA-Z0-9-]+)-[A-zA-Z0-9-]\b'
            if re.search(patron, nit):
                cliente = self.Cliente(nit, nombre)
                self.clientes.append(cliente)
                self.registro_creacion["clientes"] += 1
        except:
            return


    def agregar_banco(self, codigo, nombre):
        try:
            _ = int(codigo)
            for banco in self.bancos:
                if banco.codigo == codigo:
                    banco.nombre = nombre
                    self.registro_actualizacion["bancos"] += 1
                    return
            banco = self.Banco(codigo, nombre)
            self.bancos.append(banco)
            self.registro_creacion["bancos"] += 1
        except:
            return
    
    def agregar_factura(self, numero_factura, nit_cliente, fecha, valor):
        try:
            _ = int(valor)
            duplicada = False
            for factura in self.facturas:
                if factura.numero_factura == numero_factura:
                    self.registro_facturas["duplicadas"] += 1
                    duplicada = True
                    return
            for cliente in self.clientes:
                if cliente.nit == nit_cliente:
                    factura = self.Factura(numero_factura, nit_cliente, fecha, valor)
                    self.facturas.append(factura)
                    if not duplicada: self.registro_facturas["creadas"] += 1
                    return
            self.registro_facturas["con_error"] += 1
        except:
            self.registro_facturas["con_error"] += 1

    def agregar_pago(self, codigo_banco, fecha, nit_cliente, valor):
        try:
            _ = int(codigo_banco)
            _ = int(valor)
            _ = datetime.strptime(fecha, "%d/%m/%Y")
            duplicada = False
            for pago in self.pagos:
                if pago.codigo_banco == codigo_banco and pago.nit_cliente == nit_cliente and pago.fecha == fecha:
                    self.registro_pagos["duplicados"] += 1
                    duplicada = True
                    return
            for banco in self.bancos:
                if banco.codigo == codigo_banco:
                    for cliente in self.clientes:
                        if cliente.nit == nit_cliente:
                            pago = self.Pago(codigo_banco, fecha, nit_cliente, valor)
                            self.pagos.append(pago)
                            if not duplicada: self.registro_pagos["creados"] += 1
                            return
            self.registro_pagos["con_error"] += 1
        except:
            self.registro_pagos["con_error"] += 1

    def grabarConfiguracion_response(self):
        return {
            "clientes": {
                "creados": self.registro_creacion["clientes"],
                "actualizados": self.registro_actualizacion["clientes"],
            },
            "bancos": {
                "creados": self.registro_creacion["bancos"],
                "actualizados": self.registro_actualizacion["bancos"],
            }
        }
    def grabarTransaccion_response(self):
        return {
            "facturas": {
                "nuevasFacturas": self.registro_facturas["creadas"],
                "facturasDuplicadas": self.registro_facturas["duplicadas"],
                "facturasConError": self.registro_facturas["con_error"],
            },
            "pagos": {
                "nuevosPagos": self.registro_pagos["creados"],
                "pagosDuplicados": self.registro_pagos["duplicados"],
                "pagosConError": self.registro_pagos["con_error"],
            }
        }
    
    def devolverResumenPagos_response(self, fecha):
        mes_busqueda, año_busqueda = map(int, fecha.split('/'))
        fecha_fin_busqueda = datetime(año_busqueda, mes_busqueda, 1)
        fecha_inicio_busqueda = datetime(año_busqueda if mes_busqueda >= 3 else año_busqueda - 1, mes_busqueda - 2 if mes_busqueda >= 3 else mes_busqueda + 10 , 1)
        bancos_res = {}
        for dato in self.pagos:
            nombre_banco = ""
            if not dato.codigo_banco in bancos_res:
                for banco in self.bancos:
                    if banco.codigo == dato.codigo_banco:
                        nombre_banco = banco.nombre
                        break
                bancos_res[nombre_banco] = {}
                for i in range(3):
                    mes = (fecha_inicio_busqueda.month + i) if (fecha_inicio_busqueda.month + i) <= 12 else (fecha_inicio_busqueda.month + i - 12)
                    bancos_res[nombre_banco][calendar.month_name[mes]] = 0
            _, mes, año = map(int, dato.fecha.split('/'))
            fecha_dato = datetime(año, mes, 1)
            if fecha_inicio_busqueda <= fecha_dato <= fecha_fin_busqueda:
                bancos_res[nombre_banco][calendar.month_name[mes]] += float(dato.valor)
        return bancos_res


    def devolverEstadoCuenta_response(self, nit):
        cliente = nit
        saldo_actual = 0
        transacciones = []
        for _cliente in self.clientes:
            if _cliente.nit == nit:
                cliente = nit + " " + _cliente.nombre
                break
        for factura in self.facturas:
            if factura.nit_cliente == nit:
                saldo_actual -= float(factura.valor)
                transacciones.append({
                    "Fecha": factura.fecha,
                    "Tipo": "Cargo",
                    "Valor": "Q." + factura.valor + " " + factura.numero_factura
                })
        for pago in self.pagos:
            if pago.nit_cliente == nit:
                saldo_actual += float(pago.valor)
                transacciones.append({
                    "Fecha": pago.fecha,
                    "Tipo": "Abono",
                    "Valor": "Q." + pago.valor + " " + pago.codigo_banco
                })
        transacciones_orden = sorted(transacciones, key=lambda x: x['Fecha'])
        transacciones = {}
        for i, transaccion in enumerate(transacciones_orden):
            transacciones[i] = transaccion
        return {
            "Cliente": cliente,
            "SaldoActual": saldo_actual,
            "Transacciones": 0 if transacciones_orden == [] else transacciones
        }


app = Flask(__name__)
info = Informacion()

def dict_to_xml(data, nombre = 'respuesta'):
    def dict_to_xml_helper(data):
        xml = []
        for key, value in data.items():
            if isinstance(value, dict):
                xml.append('<{0}>{1}</{0}>'.format(key, dict_to_xml_helper(value)))
            else:
                xml.append('<{0}>{1}</{0}>'.format(key, value))
        return ''.join(xml)

    return '<{1}>{0}</{1}>'.format(dict_to_xml_helper(data), nombre)

@app.route('/grabarConfiguracion',  methods=['POST'])
def grabarConfiguracion():
    respuesta = {}
    if 'file' not in request.files:
        respuesta = {'estado': 'error', 'mensaje': 'No se proporcionó ningún archivo XML'}
    else:
        try:
            xml_file = request.files['file']
            xml_content = xml_file.read()
            datos = json.loads(json.dumps(xmltodict.parse(xml_content)))["config"]
            for cliente_data in datos["clientes"].values():
                if type(cliente_data) != list:
                    cliente_data = [cliente_data]
                for cliente in cliente_data:
                    info.agregar_cliente(cliente["NIT"], cliente["nombre"])
            for banco_data in datos["bancos"].values():
                if type(banco_data) != list:
                    banco_data = [banco_data]
                for banco in banco_data:
                    info.agregar_banco(banco["codigo"], banco["nombre"])
            respuesta = info.grabarConfiguracion_response()
        except:
            respuesta = {'estado': 'error', 'mensaje': 'Error al leer el formato del xml'}
    xml_data = dict_to_xml(respuesta)
    response = make_response(xml_data)
    response.headers['Content-Type'] = 'text/xml'
    return response

@app.route('/grabarTransaccion',  methods=['POST'])
def grabarTransaccion():
    respuesta = {}
    if 'file' not in request.files:
        respuesta = {'estado': 'error', 'mensaje': 'No se proporcionó ningún archivo XML'}
    else:
        try:
            xml_file = request.files['file']
            xml_content = xml_file.read()
            datos = json.loads(json.dumps(xmltodict.parse(xml_content)))["transacciones"]
            for factura_data in datos["facturas"].values():
                if type(factura_data) != list:
                    factura_data = [factura_data]
                for factura in factura_data:
                    info.agregar_factura(factura["numeroFactura"], factura["NITcliente"], factura["fecha"], factura["valor"])
            for pago_data in datos["pagos"].values():
                if type(pago_data) != list:
                    pago_data = [pago_data]
                for pago in pago_data:
                    info.agregar_pago(pago["codigoBanco"], pago["fecha"], pago["NITcliente"], pago["valor"])
            respuesta = info.grabarTransaccion_response()
        except:
            respuesta = {'estado': 'error', 'mensaje': 'Error al leer el formato del xml'}
    xml_data = dict_to_xml(respuesta)
    response = make_response(xml_data)
    response.headers['Content-Type'] = 'text/xml'
    return response

@app.route('/limpiarDatos',  methods=['POST'])
def limpiarDatos():
    info.clientes = []
    info.bancos = []
    info.facturas = []
    info.pagos = []
    info.registro_creacion = {"clientes": 0, "bancos": 0}
    info.registro_actualizacion = {"clientes": 0, "bancos": 0}
    info.registro_facturas = {"creadas": 0, "duplicadas": 0, "con_error": 0}
    info.registro_pagos = {"creados": 0, "duplicados": 0, "con_error": 0} 
    data = {
        'mensaje': 'Datos limpiados',
    }
    xml_data = dict_to_xml(data)
    response = make_response(xml_data)
    response.headers['Content-Type'] = 'text/xml'
    
    return response


@app.route('/devolverEstadoCuenta',  methods=['GET'])
def devolverEstadoCuenta():
    respuesta = {}
    if not 'nit' in request.args:
        for i, cliente in enumerate(info.clientes):
            respuesta[i] = info.devolverEstadoCuenta_response(cliente.nit)
        respuesta = dict(sorted(respuesta.items(), key=lambda x: x[1]["Cliente"]))
    else:
        try:
            respuesta = info.devolverEstadoCuenta_response(request.args['nit'])
        except:
            respuesta = {'estado': 'error', 'mensaje': 'Error al generar el estado de cuenta'}
    xml_data = dict_to_xml(respuesta)
    response = make_response(xml_data)
    response.headers['Content-Type'] = 'text/xml'
    return response

@app.route('/devolverResumenPagos',  methods=['GET'])
def devolverResumenPagos():
    respuesta = {}
    if not 'fecha' in request.args:
        respuesta = {'estado': 'error', 'mensaje': 'No se proporcionó ninguna fecha (mm/YYYY)'}
    else:
        try:
            respuesta = info.devolverResumenPagos_response(request.args['fecha'])
        except:
            respuesta = {'estado': 'error', 'mensaje': 'Error al generar el resumen de pagos'}
    xml_data = dict_to_xml(respuesta)
    response = make_response(xml_data)
    response.headers['Content-Type'] = 'text/xml'
    return response

@app.route('/getClientes',  methods=['GET'])
def getClientes():
    respuesta = {}
    for i, cliente in enumerate(info.clientes):
        respuesta[i] = {"nit": cliente.nit, "nombre": cliente.nit + " " + cliente.nombre}
    sorted_data = dict(sorted(respuesta.items(), key=lambda x: x[1]["nit"]))
    return jsonify({"respuesta": sorted_data})

@app.route('/abrir_pdf', methods=['GET'])
def abrir_pdf_flask():
    ruta_pdf = 'C:/Users/Paola/Desktop/CALIFICACIÓN/IPC2/IPC2_Proyecto3_202200220/Ensayo_P3_202200220.pdf'
    return send_file(ruta_pdf, as_attachment=True)

@app.route('/mostrar_datos_estudiante', methods=['GET'])
def mostrar_datos_estudiante_flask():
    nombre = "Maria Paola Guadalupe Dávila Valenzuela"
    carnet = "202200220"
    return f"Nombre: {nombre}, Carnet: {carnet}"


if __name__ == '__main__':
    app.run(debug=True, port=8123)  


