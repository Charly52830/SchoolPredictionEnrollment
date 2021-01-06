import json
import requests
import getpass
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime

def actualizar_datos_generales(archivo_credenciales = None, direccion = None) :
    """Función para actualizar los datos generales de las escuelas. Se conecta con
    el servidor de base de datos para obtener los datos, se guardan en el archivo
    DatosGenerales.json
    
    Los datos generales que se obtienen de una escuela son:
    - primer año en el que aparece la escuela (int)
    - matrícula (año con año) (list)
    - promedio de alumnos por grupo en todos los años (float)
    - nombre de la escuela (str)
    - nivel de la escuela (str)
    - latitud (float)
    - longitud (float)
    - municipio (str)
    - clave de la región (str)
    
    Ver FuncionesOrient/DatosEscuela.js y DatosDeTodasLasEscuelas.js para conocer
    cómo se obtienen los datos de la base de datos.
    
    Args:
        archivo_credenciales (str, opcional): nombre del archivo json en el 
            equipo en el que se encuentran las credenciales de acceso a la base 
            de datos. Si no se proporciona entonces el programa solicitará el 
            usuario y contraseña.
            
            Formato del archivo:
            {"username":"TU_USUARIO","password":"TU_CONTRASEÑA"}
        
        direccion (str, opcional): dirección HTTP de la base de datos a la que se 
            realiza la petición. Si no se proporciona se utilizará la dirección 
            por defecto.
    """
    
    # Obtener credenciales
    if archivo_credenciales :
        f = open(archivo_credenciales)
        credenciales = json.loads(f.read())
        username = credenciales["username"]
        password = credenciales["password"]
    else :
        print("Porfavor escriba a continuación las credenciales de acceso a la base de datos")
        print("Username: ", end = '')
        username = input()
        password = getpass.getpass()
    
    # Editar aquí la dirección por defecto en caso de que cambie    
    direccion = direccion or 'http://e.seduzac.microbit.com:2480/function/fution1_1/DatosDeTodasLasEscuelas'
    
    try :
        print("Dirección de consulta:")
        print(direccion)
        print("Solicitud en curso")
    
        # Realizar solicitudd HTTP GET
        respuesta = requests.get(
            direccion,
            data={},
            auth=(username, password)
        )
        
        datos = json.loads(respuesta.text)
        
        # Evaluar el estatus de la respuesta
        if 'errors' in datos :
            codigo_error = datos["errors"][0]["code"]
            
            print("Ocurrió un error durante la descarga de los datos")
            print("Codigo de error: ", codigo_error)
            if codigo_error == 401 :
                print("Credenciales inválidas, vuelvalo a intentar escribiendo correctamente las credenciales")
            elif codigo_error == 500 :
                print("Dirección inválida")
            
        else :
            # Guardar los datos en un archivo local.
            text_file = open("DatosGenerales.json", "w")
            text_file.write(respuesta.text)
            text_file.close()
                
            print("Datos descargados y guardados en el archivo DatosGenerales.json")
        
    except requests.exceptions.ConnectionError :
        print("Ocurrió un error durante la descarga de los datos")
        print("Porfavor revise que la dirección y las credenciales de acceso sean correctas y vuelva a intentarlo más tarde")

def informacion() :
    """Muestra la información general de este script, así como de los comandos y
    cómo utilizarlos.
    """
    
    info = """
    Este script se utiliza para actualizar la información de los datos de la aplicación.
    A continuación se listan los comandos y sus parámetros:
    
    Comandos disponibles:
    
    info:
    
        Muestra este mensaje de información del programa.
        
        Ejemplo de uso:
        
        $ python3.6 UpdateScript.py info
    
    actualizar_datos_generales:
    
        Descarga de la base de datos los datos generales de las escuelas.
        
        Parámetros disponibles:
        
            archivo_credenciales (opcional):
                Nombre del archivo en el equipo en el que se encuentran las credenciales
                de acceso a la base de datos.
                
                Formato del archivo:
                {"username":"TU_USUARIO","password":"TU_CONTRASEÑA"}
                
                Si no se proporciona entonces el programa solicitará el usuario y contraseña
            
            direccion (opcional):
                Dirección HTTP de la base de datos a la que se realiza la petición.
                
                Si no se proporciona se utilizará la dirección por defecto.
        
        Ejemplo de uso:
        
        $ python3.6 UpdateScript.py actualizar_datos_generales archivo_credenciales="credenciales.json" direccion="http://e.seduzac.microbit.com:2480/function/fution1_1/DatosDeTodasLasEscuelas"

    actualizar_proyeccion :
        
        Realiza la proyección de matrícula de todas las escuelas que se encuentren
        en el archivo DatosGenerales.json. Se recomienda ejecutar este comando en
        un equipo de alta gama, ya que se ejecutarán distintos algoritmos como
        redes neuronales que necesitan muchos recursos para realizar los cálculos 
        necesarios.
        
        Tiempo estimado para 4035 escuelas:
        
        +--------+---------+------------------+----------------------+-------------+
        | Equipo | Memoria | Procesador       | Tarjeta gráfica      | Tiempo      |
        +--------+---------+------------------+----------------------+-------------+
        | 1      | 16 Gb   | i7 7a generación | Tarjeta de baja gama | 165 minutos |
        +--------+---------+------------------+----------------------+-------------+
        | 2      | 4 Gb    | AMD E1-6010      | Tarjeta de baja gama | 24 horas    |
        +--------+---------+------------------+----------------------+-------------+
        
        Este comando tiene la capacidad de reanudar el trabajo en donde se quedó
        en caso de que la ejecución haya sido interrumpida. Los datos de la 
        proyección se guardan en el archivo .ProyeccionMatricula.csv.
        
        Cuando este comando comienza una nueva proyección realiza un respaldo en 
        el directorio .respaldos_proyeccion en caso de que exista previamente un
        archivo .ProyeccionMatricula.csv
        
        Parámetros disponibles:
            
            modo (opcional):
                Especifica la acción a realizar por este comando. El modo por 
                defecto es reanudar.
                
                reanudar: reanuda el cómputo en donde se quedó.
                nueva_proyeccion: realiza un respaldo y comienza una nueva proyección.
                forzar_nueva_proyeccion: realiza un respaldo y forza el comienzo 
                    de una nueva proyección.
        
        Ejemplo de uso:
        
        $ python3.6 UpdateScript.py actualizar_proyeccion modo="nueva_proyeccion"

    actualizar_datos_estado :
    
        Genera el archivo DatosEscuelas.json el cual contiene los datos generales
        de las escuelas junto con los datos de la proyección. Este archivo es
        consumido por la aplicación de Dash en el directorio AppDash/.
        
        Sin parámetros disponibles.
        
        Ejemplo de uso:
        
        $ python3.6 UpdateScript.py actualizar_datos_estado
    """
    
    print(info)

def actualizar_proyeccion(modo = "reanudar") :
    """Realiza la proyección de matrículas de todas las escuelas que se encuentren
    en el archivo DatosGenerales.json
    
    Args:
        modo (str, opcional): Especifica la acción a realizar por este comando. 
            El modo por defecto es reanudar.
            
            reanudar: reanuda el cómputo en donde se quedó.
            nueva_proyeccion: realiza un respaldo y comienza una nueva proyección.
            forzar_nueva_proyeccion: realiza un respaldo y forza el comienzo 
                de una nueva proyección.
    """
    
    if modo not in ["reanudar", "nueva_proyeccion", "forzar_nueva_proyeccion"] :
        raise TypeError
    
    try :
        f = open("DatosGenerales.json")
        escuelas = json.load(f)['result'][0]
        
        # Borrar registros que no son escuelas
        if '@type' in escuelas :
            escuelas.pop('@type')
        if '@version' in escuelas :
            escuelas.pop('@version')
        
    except FileNotFoundError :
        info = """
        No se encontró el archivo DatosGenerales.json, para obtenerlo ejecuta el siguiente comando:

        $ python3.6 UpdateScript.py actualizar_datos_generales
        """
        print(info)
        return
    
    if modo == "nueva_proyeccion" :
        info = """
        Antes de actualizar la proyección de matrícula se recomienda actualizar los
        datos generales con el comando:

        $ python3.6 UpdateScript.py actualizar_datos_generales

        ¿Desea continuar? (Y/n) """
        print(info, end = '')
        
        respuesta = input().lower()
        
        if respuesta not in ["y", "yes"] :
            print("Cancelando operacion")
            return
        else :
            modo = "forzar_nueva_proyeccion"
    
    if modo == "forzar_nueva_proyeccion" :
        # Crear un respaldo de los datos actuales si es que existen
        try :
            csv_proyeccion_matricula = open(".ProyeccionMatricula.csv", "r")
        except FileNotFoundError :
            print("No se encontró ningún archivo con información previa de proyección de matrícula")
            print("Omitiendo respaldo")
        else :
            now = datetime.now()
            nombre_nuevo_respaldo = "Respaldo_%02d-%02d-%02d_%02d:%02d:%02d.csv" % (
                now.day, 
                now.month, 
                now.year, 
                now.hour, 
                now.minute, 
                now.second
            )
            if not os.path.exists('.respaldos_proyeccion') :
                os.makedirs('.respaldos_proyeccion')
            nuevo_respaldo = open(".respaldos_proyeccion/%s" % (nombre_nuevo_respaldo), "w+")
            nuevo_respaldo.write(csv_proyeccion_matricula.read())
            nuevo_respaldo.close()
            csv_proyeccion_matricula.close()
            print("Respaldo realizado con nombre %s" % (nombre_nuevo_respaldo))
        
        # Crear nuevo archivo .ProyeccionMatricula.csv
        csv_proyeccion_matricula = open(".ProyeccionMatricula.csv", "w+")
        csv_proyeccion_matricula.write('')
        csv_proyeccion_matricula.close()
        print("Nuevo archivo de proyección de matrícula creado")
    
    # Contar el número de lineas en el archivo para retomar trabajo previo
    num_lines = 0
    with open(".ProyeccionMatricula.csv", 'r') as csv_proyeccion_matricula :
        for line in csv_proyeccion_matricula :
            num_lines += 1
    
    csv_proyeccion_matricula = open(".ProyeccionMatricula.csv", "a+")
    
    if num_lines == 0 :
        # Insertar cabecera al nuevo archivo
        csv_proyeccion_matricula.write("cct,proyeccion_1,proyeccion_2,proyeccion_3,proyeccion_4,proyeccion_5,mae,rmse,mape,rp,metodo\n")
        num_lines = 1
    
    ccts = list(escuelas.keys())
    print("Total de escuelas: %d" % (len(escuelas)))
    print("Empezando en la escuela %d" % (num_lines))
    
    from Proyeccion.Metodos.ExpertsOpinion import evaluate_and_predict_ep
    from Proyeccion.Metodos.AutoARIMA import evaluate_and_predict_arima
    from Proyeccion.Metodos.LinearRegression import evaluate_and_predict_slr
    
    for i in range(num_lines - 1, len(escuelas)) :
        cct = ccts[i]
        matricula = np.array(escuelas[cct]['matricula'])
        matricula_por_grupo = escuelas[cct]['prom_alumnos_grupo']
        
        # Obtener predicción futura e histórica
        if len(matricula) > 8 :
            proy_matricula_futura, proy_matricula_historica = evaluate_and_predict_ep(matricula)
            matricula_historica_real = matricula[5:]
            metodo = 'EP'
        elif len(matricula) > 4 :
            proy_matricula_futura, proy_matricula_historica = evaluate_and_predict_arima(matricula, OFFSET_ANIOS = 0)
            matricula_historica_real = matricula
            metodo = 'ARIMA'
        elif len(matricula) > 1 :
            proy_matricula_futura, proy_matricula_historica = evaluate_and_predict_slr(matricula)
            matricula_historica_real = matricula
            metodo = 'SLR'
        else :
            proy_matricula_futura = np.array([matricula[0]] * 5)
            proy_matricula_historica = np.array(matricula)
            matricula_historica_real = matricula
            metodo = 'NF'
        
        # Calcular los errores
        mae = np.abs(proy_matricula_historica - matricula_historica_real).mean()
        rmse = np.sqrt(np.square(proy_matricula_historica - matricula_historica_real).mean())
        mape = np.abs((proy_matricula_historica - matricula_historica_real) / matricula_historica_real).mean()
        pr = (np.abs(proy_matricula_historica - matricula_historica_real) >= matricula_por_grupo).mean()
        
        proy_matricula_futura = proy_matricula_futura.astype(np.int)
        
        # Escribir nuevo renglón
        csv_proyeccion_matricula.write("%s,%d,%d,%d,%d,%d,%.2lf,%.2lf,%.2lf,%.2lf,%s\n" % (
            cct,
            proy_matricula_futura[0],
            proy_matricula_futura[1],
            proy_matricula_futura[2],
            proy_matricula_futura[3],
            proy_matricula_futura[4],
            mae,
            rmse,
            mape,
            pr,
            metodo
        ))
        
        print("Escuela %d/%d terminada" % (i + 1, len(escuelas)))

    csv_proyeccion_matricula.close()
    print("Todas las escuelas han sido proyectadas")
    
def actualizar_datos_estado() :
    """Genera el archivo DatosEscuelas.json el cual contiene los datos generales
    de las escuelas junto con los datos de la proyección. Este archivo es
    consumido por la aplicación de Dash en el directorio AppDash/.
    """
    
    try :
        csv_proyeccion_matricula = pd.read_csv(".ProyeccionMatricula.csv")
        f = open("DatosGenerales.json", "r")
        escuelas = json.load(f)['result'][0]
        
        # Borrar registros que no son escuelas
        if '@type' in escuelas :
            escuelas.pop('@type')
        if '@version' in escuelas :
            escuelas.pop('@version')
        
        assert(csv_proyeccion_matricula.shape[0] == len(escuelas))
        
    except FileNotFoundError :
        print("Error al cargar los datos.")
        print("Para generarlos ejecuta los siguientes comandos")
        print("$ python3.6 UpdateScript.py actualizar_datos_generales")
        print("$ python3.6 UpdateScript.py actualizar_proyeccion")

    datos_completos_escuelas = dict()
    for i in range(csv_proyeccion_matricula.shape[0]) :
        row = np.array(csv_proyeccion_matricula.loc[i])
        cct = row[0]
        
        escuela = {
            "primer_anio" : int(escuelas[cct]["primer_anio"]),
            "matricula" : escuelas[cct]["matricula"],
            "pred" : list(map(int, row[1:6])),
            "mae" : row[6],
            "rmse" : row[7],
            "mape" : row[8],
            "rp" : row[9],
            "metodo" : row[10],
            "PAG" : escuelas[cct]["prom_alumnos_grupo"],
            "nombre" : escuelas[cct]["nombre"],
            "nivel" : escuelas[cct]["nivel"],
            "mun" : escuelas[cct]["mun"],
            "lat" : escuelas[cct]["lat"],
            "lng" : escuelas[cct]["lng"],
            "region" : escuelas[cct]["region"]
        }
        datos_completos_escuelas[cct] = escuela
    
    with open("DatosEscuelas.json", "w+") as outfile:  
        json.dump(datos_completos_escuelas, outfile, separators=(',', ':')) 
    print("Datos guardados en el archivo DatosEscuelas.json")

def comando_no_encontrado() :
    info = """
    No se encontró el comando especificado.

    Comandos disponibles:
    - info
    - actualizar_datos_generales
    - actualizar_proyeccion
    - actualizar_datos_estado

    Uso:

    $ python3.6 UpdateScript.py info
    """
    print(info)
    
def cargar_parametros() :
    parametros = dict()
    if len(sys.argv) <= 2 :
        return parametros
    
    for arg in sys.argv[2:] :
        parametro, valor = arg.split('=')
        parametros[parametro] = valor
    
    return parametros

def cargar_comando() :
    if len(sys.argv) == 1 :
        return informacion

    comando = sys.argv[1]
    if comando == "info" :
        return informacion
    elif comando == "actualizar_datos_generales" :
        return actualizar_datos_generales
    elif comando == "actualizar_proyeccion" :
        return actualizar_proyeccion
    elif comando == "actualizar_datos_estado" :
        return actualizar_datos_estado
    else :
        return comando_no_encontrado

if __name__ == "__main__" :    
    comando = cargar_comando()
    parametros = cargar_parametros()
    try :
        if comando == comando_no_encontrado :
            comando()
        else :
            comando(**parametros)
    except TypeError :
        print("Error: Se especificó incorrectamente alguno de los parametros")
