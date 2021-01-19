import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from apps.utilidades_reporte import GeneradorDeGraficas

from app import cache

municipios_de_regiones = {
    "32ADG0011N" : ['Calera', 'Morelos', 'Pánuco', 'Vetagrande', 'Villa de cos', 'Zacatecas'],
    "32ADG0012M" : ['Cañitas de Felipe Pescador', 'Fresnillo', 'General Enrique Estrada', 'Valparaíso'],
    "32ADG0013L" : ['Apozol', 'Huanusco', 'Jalpa', 'Juchipila', 'Mezquital del oro', 'Moyahua de Estrada', 'Tabasco'],
    "32ADG0014K" : ['Atolinga', 'Benito Juárez', 'Momax', 'Santa María de la paz', 'Tepechitlán', 'Teúl de González Ortega', 'Tlaltenango de Sánchez Román', 'Trinidad García de la Cadena'],
    "32ADG0015J" : ['General Francisco r Murguía', 'Juan Aldama', 'Miguel Auza', 'Río Grande'],
    "32ADG0016I" : ['Concepción del oro', 'El Salvador', 'Mazapil', 'Melchor Ocampo'],
    "32ADG0017H" : ['Pinos', 'Villa Hidalgo'],
    "32ADG0018G" : ['El Plateado de Joaquín Amaro', 'Jerez', 'Monte Escobedo', 'Susticacán', 'Tepetongo', 'Villanueva'],
    "32FSR0001J" : ['Loreto', 'Noria de Ángeles', 'Villa García', 'Villa González Ortega'],
    "32ADG0021U" : ['Cuauhtémoc', 'Genaro Codina', 'General Pánfilo Natera', 'Guadalupe', 'Luis Moya', 'Ojocaliente', 'Trancoso'],
    "32ADG0022T" : ['Chalchihuites', 'Jiménez del Teul', 'Sain Alto', 'Sombrerete'],
    "32ADG0010O" : ['Calera', 'General Enrique Estrada', 'Morelos', 'Pánuco', 'Villa de cos', 'Zacatecas'],
    "32ADG0025Q" : ['Cañitas de Felipe Pescador', 'Fresnillo'],
    "32ADG0003E" : ['Apozol', 'Huanusco', 'Jalpa', 'Juchipila', 'Mezquital del oro', 'Moyahua de Estrada', 'Tabasco'],
    "32ADG0004D" : ['Atolinga', 'Benito Juárez', 'Momax', 'Santa María de la paz', 'Tepechitlán', 'Teúl de González Ortega', 'Tlaltenango de Sánchez Román', 'Trinidad García de la Cadena'],
    "32ADG0005C" : ['General Francisco r Murguía', 'Juan Aldama', 'Miguel Auza', 'Río Grande'],
    "32ADG0006B" : ['Concepción del oro', 'El Salvador', 'Mazapil', 'Melchor Ocampo'],
    "32ADG0007A" : ['Pinos', 'Villa Hidalgo'],
    "32ADG0008Z" : ['El Plateado de Joaquín Amaro', 'Jerez', 'Monte Escobedo', 'Susticacán', 'Tepetongo', 'Villanueva'],
    "32ADG0009Z" : ['Loreto', 'Noria de Ángeles', 'Villa García', 'Villa González Ortega'],
    "32ADG0019F" : ['Cuauhtémoc', 'Genaro Codina', 'General Pánfilo Natera', 'Guadalupe', 'Luis Moya', 'Ojocaliente', 'Trancoso', 'Vetagrande'],
    "32ADG0020V" : ['Chalchihuites', 'Jiménez del Teul', 'Sain Alto', 'Sombrerete'],
    "32ADG0023S" : ['Apulco', 'Nochistlán de Mejía'],
    "32ADG0026P" : ['Valparaíso']
}

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
                type = "submit",
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
