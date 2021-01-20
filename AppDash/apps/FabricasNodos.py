import dash_html_components as html
import dash_bootstrap_components as dbc
from apps.utilidades_reporte import GeneradorDeGraficas

from app import cache

# Lista con los municipios que controla cada región. Sirve para crear las aristas
# que unen a los nodos de una región con los de un municipio.
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
    """
    Clase que pertenece a un nodo. Contiene los 4 elementos que cambian en el layout
    principal de la aplicación de estado.
    """
    
    def __init__(self, titulo, label_dropdown, boton_regresar, boton_avanzar) :
        """
        Constructor de la clase ElementosLayoutPrincipal.
        
        Contiene como parámetros cada uno de los atributos que cambian en el 
        layout principal.
        
        Args:
            titulo (str): título para mostrar en la página de la aplicación de estado.
            label_dropdown (str): etiqueta para mostrar arriba del dropdown en el 
                layout principal.
            boton_regresar (:obj: `dash_bootstrap_components.Button`): layout del
                botón zoom-out.
            boton_avanzar (:obj: `dash_bootstrap_components.Button`): layout del
                botón zoom-in.
        """
        # (str)
        self.titulo = titulo
        # (str)
        self.label_dropdown = label_dropdown
        # (dbc.Button)
        self.boton_regresar = boton_regresar
        # (dbc.Button)
        self.boton_avanzar = boton_avanzar

class Nodo :
    """
    Clase que permite el control del layout en la aplicación de estado. Representa
    un nodo en un grafo de árbol. Guarda elementos relacionados al layout y a las
    conexiones entre nodos, lo cual, es lo que permite la navegación en la aplicación
    de estado.
    """
    
    def __init__(self, layout, id, serie_individual = None, grafica_general = None, nombre_hijos = None) :
        """
        Constructor de la clase Nodo.
        
        Contiene como parámetros los atributos básicos de la clase.
        
        Args:
            layout (:obj: `ElementosLayoutPrincipal`): objeto que contiene los
                elementos que cambian en el layout principal de la aplicación de
                estado.
            id (str): identificador único del nodo en su conjunto, es decir, la
                llave con la que se identifica una escuela, un municipio, una región
                o el estado en el diccionario cache.
            serie_individual (dict, optional): diccionario con los datos básicos
                de una serie de tiempo. Si el nodo a crear es una hoja del árbol
                entonces no se debe especificar este parámetro.
            grafica_general (:obj: `plotly.express.line`, optional): gráfica general
                que se quiera mostrar en el layout principal de la aplicación de
                estado. Este parámetro solo debe especificarse si se desea 
                sobreescribir la gráfica general a mostrar, ya que por defecto,
                la gráfica general se genera al vuelo considerando las gráficas
                individuales de todos los hijos.
            nombre_hijos (str, optional): nombre de los hijos a mostrar en las
                gráficas o tablas, por ejemplo, Regiones o Municipios.
        """
        # (ElementosLayoutPrincipal)
        self.layout = layout
        # (str)
        self.id = id
        # (dict)
        self.serie_individual = serie_individual
        # (str)
        self.nombre_hijos = nombre_hijos
        
        # Diccionario para almacenar la referencia a los nodos hijos
        self.hijos = dict()
        # Referencia a otro nodo
        self.padre = None
        
        # En caso de necesitar sobreescribir la gráfica general
        # (plotly.express.line)
        self.grafica_general = grafica_general
    
    def agregar_hijo(self, hijo) :
        """
        Método que conecta como hijo a otro nodo con el nodo actual.
        
        Args:
            hijo (:obj: `Nodo`): nodo hijo a agregarle al nodo actual
        """
        nombre_hijo = hijo.serie_individual['nombre']
        self.hijos[nombre_hijo] = hijo
        hijo.padre = self
    
    def generar_scatterplot_general(self) :
        """
        Método que genera un scatterplot con las series de tiempo individuales de
        cada uno de los hijos del nodo.
        
        Si el atributo grafica_general fue especificado, entonces devuelve la gráfica
        que contiene este atributo.
        
        """
        if not self.grafica_general :
            series = dict()
            for hijo in self.hijos :
                series[hijo] = self.hijos[hijo].serie_individual
            return GeneradorDeGraficas.generar_scatterplot(series, title = self.layout.titulo, titulo_leyenda = self.nombre_hijos)
        return self.grafica_general

class FabricaNodosRegion :
    """
    Fábrica de objetos nodos con el propósito de ocultar de la aplicación estado
    la implementación de la creación nodos de regiones.
    """
    
    def generar_nodo(id_region) :
        """
        Genera un nuevo objeto nodo que corresponde a una región en particular.
        
        La principal característica es que el botón zoom-in en el layout de estos
        nodos es de tipo submit, lo que permite la creación de reportes por
        municipio en lugar de seguir bajando por el árbol.
        
        Args:
            id_region (str): identificador de la región en cache['regiones']
        
        Returns:
            nodo (:obj: `Nodo`): nodo que contiene los datos de la región.
        
        """
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
            nombre_hijos = "Municipios"
        )
        
        return nodo

class FabricaNodosMunicipio :
    """
    Fábrica de objetos nodos con el propósito de ocultar de la aplicación estado
    la implementación de la creación nodos de municipios.
    """
    
    def generar_nodo(id_municipio) :
        """
        Genera un nuevo objeto nodo que corresponde a un municipio en particular.
        
        La principal característica es que, al ser los nodos hoja del árbol, no 
        tienen ningún layout principal que mostrar, por lo que sus atributos
        serie_individual y layout son None.
        
        Args:
            id_municipio (str): identificador de la región en cache['municipios']
        
        Returns:
            nodo (:obj: `Nodo`): nodo que contiene los datos del municipio.
        """
        nodo = Nodo(
            layout = None,
            id = id_municipio,
            serie_individual = cache['municipios'][id_municipio],
        )
        
        return nodo
