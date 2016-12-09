from django.core.urlresolvers import reverse
from django.views.generic import FormView

from optimizacion.forms import ProcesamientoForm
from optimizacion.simplex import Simplex


class ProcesamientoView(FormView):
    template_name = "optimizacion/optimizacion_process.html"
    form_class = ProcesamientoForm
    variables = None
    total_restricciones = []

    def get_context_data(self, **kwargs):
        context = super(ProcesamientoView, self).get_context_data(**kwargs)
        # Adicionar al contexto lo que se requiera en el template

        return context

    def form_valid(self, form):
        k, tis, b, matriz_utilidad = form.get_clean_archivo()
        #  Uso de funcionalidades tipo helper para pre proceso y calculo de resultado
        self.variables = pre_procesamiento_variables(k, b)
        self.total_restricciones += pre_procesamiento_r1(self.variables)
        self.total_restricciones += pre_procesamiento_r2(self.variables)
        print(self.total_restricciones) # En caso de querer verificar el conjunto de restricciones
        return super(ProcesamientoView, self).form_valid(form)

    def get_success_url(self):
        return reverse('optimizacion:inicio')


#  Toda funcionalidad helper para pre procesar y calcular el resultado

def funcion_objetivo(variables, utilidades):
    pass


def pre_procesamiento_variables(k, b):
    """
    Autor: Daniel Correa

    Permite obtener todas las variables de descion en forma matricial para generacion de restricciones

    Explicacion:
    Recorre un rango i de 0 hasta k.
    Para cada i genera una variable de descion 1x_i de tal forma que cada fila contenga variables
    desde 1x_(i*b +1) hasta x_(((i+1)*b)+1)
    El rango de python no es inclusivo para el ultimo valor (porque arranca en 0), por eso se suma 1 en al final
    Ej: Para un k=2 y b=3, con un i=0 va desde 1 hasta 3+1, con un i=1 va desde 4 hasta 6+1

    :param k: cantidad de parcelas
    :param b: cantidad de instantes
    :return: Matriz de k filas y b columnas con variables de descion
    """
    variables = []
    for i in range(k):
        restriccion = ['1x_'+str(j) for j in range(i*b + 1, ((i+1)*b)+1)]
        variables.append(restriccion)
    return variables


def pre_procesamiento_r1(variables):
    """
    Autor: Daniel Correa

    Permite obtener las restricciones en formato de solver para el primer conjunto de restricciones del modelo

    R1: Sum j=1 hasta b x1,j = 1 desde 1 hasta k

    Explicacion:
    Para cada fila de variables genera una cadena en formato R1 para solver
    Ej: Para una fila [1x_1, 1x_2, 1x_3] genera 1x_1 + 1x_2 + 1x_3 = 1

    :param variables: matriz con variables de descion
    :return: Arreglo con restricciones en formato solver
    """
    resultado = []
    for fila in variables:
        restriccion = ' + '.join(fila)
        restriccion += ' = 1'
        resultado.append(restriccion)
    return resultado


def pre_procesamiento_r2(variables):
    """
    Autor: Daniel Correa

    Permite obtener las restricciones en formato de solver para el primer conjunto de restricciones del modelo

    R2: Sum i=1 hasta k xi,1 <= 1 desde 1 hasta b

    Explicacion:
    Se inicializa el resultado con la primera fila.
    Para cada fila restante pega el valor de resultado y fila en la misma posicion con un + en el medio.
    Agrega el valor <= 1 para cada elemento de resultado
    Ej: Para dos filas [['1x_1', '1x_2'], ['1x_3', '1x_4']] genera las restricciones 1_x1 + 1x_3 <= 1 y 1x_2 + 1x_4 <= 1

    :param variables: matriz con variables de descion
    :return: Arreglo con restricciones en formato solver
    """
    resultado = variables[0]
    for fila in variables[1:]:
        resultado = [' + '.join(valores) for valores in zip(resultado, fila)]
    resultado = ['%s <= 1' % valor for valor in resultado]
    return resultado
