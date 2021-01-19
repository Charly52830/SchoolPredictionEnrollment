import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from apps.utilidades_reporte import GeneradorDeGraficas

from app import cache

class ElementosLayoutPrincipal :
    
    def __init__(self, titulo, label_dropdown, boton_regresar, boton_avanzar) :
        # (str)
        self.titulo = titulo
        # (str)
        self.label_dropdown = label_dropdown
        # (dbc.Button)
        self.boton_regresar = boton_regresar
        # (dbc.Button o html.Form)
        self.boton_avanzar = boton_avanzar

class Nodo :
    
    def __init__(self, layout, id, serie_individual = None, grafica_general = None) :
        # (ElementosLayoutPrincipal)
        self.layout = layout
        # (str)
        self.id = id
        # (dict)
        self.serie_individual = serie_individual
        
        self.hijos = dict()
        self.padre = None
        
        # En caso de necesitar sobreescribir la gráfica general
        self.grafica_general = grafica_general
    
    def agregar_hijo(self, hijo) :
        nombre_hijo = hijo.serie_individual['nombre']
        self.hijos[nombre_hijo] = hijo
        hijo.padre = self
    
    def generar_scatterplot_general(self) :
        if not self.grafica_general :
            series = dict()
            for hijo in self.hijos :
                series[hijo] = self.hijos[hijo].serie_individual
            return GeneradorDeGraficas.generar_scatterplot(series, title = self.layout.titulo)
        return self.grafica_general

class FabricaNodosRegion :
    
    def generar_nodo(id_region) :
        layout = ElementosLayoutPrincipal(
            titulo = 'Matrícula de los municipios de la región %s' % (cache['regiones'][id_region]['nombre']),
            label_dropdown = 'Selecciona un municipio:',
            boton_regresar = dbc.Button([
                'Ver regiones ',
                html.I(className="fas fa-minus")],
                type = "button",
                style = {
                    "padding" : "0.2rem",
                    "margin" : "0.2rem 0.2rem 0.2rem 0.2rem",
                    "background" : "#FF0055",
                    "border-color" : "#FF0055"
                },
                id = 'zoom-out'
            ),
            boton_avanzar = dbc.Button([
                'Ver escuelas ',
                html.I(className="fas fa-plus")],
                type = "button",
                style = {
                    "padding" : "0.2rem",
                    "margin" : "0.2rem 0.2rem 0.2rem 0.2rem",
                    "background" : "#1199EE",
                    "border-color" : "#1199EE"
                },
                id = 'zoom-in'
            )
        )
        
        nodo = Nodo(
            layout = layout,
            id = id_region,
            serie_individual = cache['regiones'][id_region],
        )
        
        return nodo

class FabricaNodosMunicipio :
    
    def generar_nodo(id_municipio) :
        
        nodo = Nodo(
            layout = None,
            id = id_municipio,
            serie_individual = cache['municipios'][id_municipio],
        )
        
        return nodo
