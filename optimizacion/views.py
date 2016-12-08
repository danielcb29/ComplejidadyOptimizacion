from django.core.urlresolvers import reverse
from django.views.generic import FormView

from optimizacion.forms import ProcesamientoForm
from optimizacion.simplex import Simplex


class ProcesamientoView(FormView):
    template_name = "optimizacion/optimizacion_process.html"
    form_class = ProcesamientoForm

    def get_context_data(self, **kwargs):
        context = super(ProcesamientoView, self).get_context_data(**kwargs)
        # Adicionar al contexto lo que se requiera en el template

        return context

    def form_valid(self, form):
        k, tis, b, matriz_utilidad = form.get_clean_archivo()
        #  Uso de funcionalidades tipo helper para pre proceso y calculo de resultado
        total_restricciones = []
        total_restricciones += pre_procesamiento_r1(k, b)
        print(total_restricciones)
        return super(ProcesamientoView, self).form_valid(form)

    def get_success_url(self):
        return reverse('optimizacion:inicio')


#  Toda funcionalidad helper para pre procesar y calcular el resultado

def pre_procesamiento_r1(k, b):
    """
    Autor: Daniel Correa

    Permite obtener las restricciones en formato de solver para el primer conjunto de restricciones del modelo

    R1: Sum j=1 hasta b x1,j = 1 desde 1 hasta k

    Explicacion:
    Recorre un rango i de 0 hasta k.
    Para cada i genera una cadena con la suma de Xs de tal forma que valla desde 1x_(i*b +1) hasta x_(((i+1)*b)+1)
    El rango de python no es inclusivo para el ultimo valor (porque arranca en 0), por eso se suma 1 en al final
    Ej: Para un k=2 y b=3, con un i=0 va desde 1 hasta 3+1, con un i=1 va desde 4 hasta 6+1

    :param k: cantidad de parcelas
    :param b: cantidad de instantes
    :return: Arreglo con restricciones en formato solver
    """
    resultado = []
    for i in range(k):
        restriccion = ' + '.join(['1x_'+str(j) for j in range(i*b + 1, ((i+1)*b)+1)])
        resultado.append(restriccion)
    return resultado


def pre_procesamiento_r2(k, b):
    """
    Autor: Daniel Correa

    Permite obtener las restricciones en formato de solver para el primer conjunto de restricciones del modelo

    R2: Sum i=1 hasta k xi,1 <= 1 desde 1 hasta b

    Explicacion:

    Ej:

    :param k: cantidad de parcelas
    :param b: cantidad de instantes
    :return: Arreglo con restricciones en formato solver
    """
    pass