# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.views.generic import FormView

from optimizacion.forms import ProcesamientoForm
from optimizacion.simplex import Simplex
from math import floor


class ProcesamientoView(FormView):
    template_name = "optimizacion/optimizacion_process.html"
    form_class = ProcesamientoForm
    fun_obj = None
    variables = None
    total_restricciones_r1 = []
    total_restricciones_r2 = []
    total_restricciones_r3 = []


    def get_context_data(self, **kwargs):
        context = super(ProcesamientoView, self).get_context_data(**kwargs)
        # Adicionar al contexto lo que se requiera en el template
        context['has_resultados'] = False
        return context

    def form_valid(self, form):
        k, tis, b, matriz_utilidad = form.get_clean_archivo()

        #  Uso de funcionalidades tipo helper para pre proceso y calculo de resultado
        self.variables = pre_procesamiento_variables(k, b)
        self.total_restricciones_r1 = pre_procesamiento_r1(self.variables)
        self.total_restricciones_r2 = pre_procesamiento_r2(self.variables)
        self.total_restricciones_r3 = pre_procesamiento_r3(self.variables, tis, k*b)
        self.fun_obj = funcion_objetivo(self.variables, matriz_utilidad, k)

        # Procesar datos calculados con solver

        try:
            total_restricciones = self.total_restricciones_r1 + self.total_restricciones_r2 + self.total_restricciones_r3
            # total_restricciones = self.total_restricciones_r1 + self.total_restricciones_r2
            solver = Simplex(num_vars=k*b, constraints=total_restricciones, objective_function=self.fun_obj)
            solucion = solver.solution
            planificacion = planificacion_parcelas(solucion,self.variables,k,b)
            instantes = range(1,b+1)
            valor_optimo = solver.optimize_val
            msn = 'Valor factible encontrado'
        except ValueError:
            msn = 'No hay solucion factible'
            valor_optimo = None
            solucion = None
            planificacion = None
            instantes = None

        # Contexto para presentacion de resultados
        context = {
            'form': form,
            'has_resultados': True,
            'restricciones_1':self.total_restricciones_r1,
            'restricciones_2':self.total_restricciones_r2,
            'restricciones_3':self.total_restricciones_r3,
            'funcion_objetivo': self.fun_obj,
            'planificacion':planificacion,
            'valor_optimo': valor_optimo,
            'instantes': instantes,
            'solucion': solucion,
            'msn': msn
        }
        return render(self.request, self.template_name, context)


#  Toda funcionalidad helper para pre procesar y calcular el resultado

def funcion_objetivo(variables, utilidades, k):
    """
    Autor: Daniel Correa

    Permite obtener una tupla que representa la funcion objetivo

    FO: Max sum i=0 hasta k sum j=0 hasta b de Xij * Uij

    Explicacion:
    En un rango de 0 hasta k, se saca cada fila de la matriz de variables y la matriz de utilidad.
    Se asignan los coeficientes de utilidad a las variables de la funcion objetivo (Xij * Uij)
    Se guardan esos coeficientes en un arreglo
    Se retorna una tupla con la expresion maximize y todos los valores del arreglo en una expresion +
    Ej: Para unas variables [['1x_1','1x_2','1x_3],['1x_4','1x_5','1x_6]]
    unas utilidades [[1,2,3],[4,5,6]] y un k=2 se obtiene como resultado
    ('maximize', '1x_1+2x_2+3x_3+4x_4+5x_5+6x_6')

    :param variables: matriz variables de desicion
    :param utilidades: matriz con coeficientes de utilidad
    :param k: cantidad de parcelas
    :return: Tupla que representa funcion objetivo
    """
    resultado = []
    for i in range(k):
        var = variables[i]
        utl = utilidades[i]
        coeficientes = [union[0].replace('1x', '%ix' % union[1]) for union in zip(var, utl)]
        resultado += coeficientes
    return 'maximize', ' + '.join(resultado)


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
    Autor: Daniel Correa, Aurelio Vivas

    Permite obtener las restricciones en formato de solver para el primer conjunto de restricciones del modelo

    R2: Sum i=1 hasta k xi,1 <= 1 desde 1 hasta b

    Se inicializa el resultado con la primera fila.
    Para cada fila restante pega el valor de resultado y fila en la misma posicion con un + en el medio.
    Agrega el valor <= 1 para cada elemento de resultado
    Ej: Para dos filas [['1x_1', '1x_2'], ['1x_3', '1x_4']] genera las restricciones 1_x1 + 1x_3 <= 1 y 1x_2 + 1x_4 <= 1

    :param variables: matriz con variables de descion
    :return: Arreglo con restricciones en formato solver
    """
    # Naturalmente las funciones de python reciben los argumentos como una tupla,
    # * indica que la tupla que se esta pasando es una lista de argumentos a la
    # función zip
    resultado = [' + '.join(valores) for valores in zip(*tuple(variables))]
    resultado = ['%s <= 1' % valor for valor in resultado]
    return resultado

# Helper para R3


def sub_matriz(i, j, matriz, tis):
    """
    Autor: Daniel Correa, Aurelio Vivas, Kellys Santa, John Lourido

    Funcion auxiliar para calculo de submatriz de una variable de decision

    :param i: Posicion de la fila donde se encuentra la variable
    :param j: Posicion de la columna donde se encuentra la variable
    :param matriz: Matriz de variables de decision
    :param tis: Tiempos de cosechas de cada parcela
    :return: Sub matriz de una variable de decision
    """
    submatriz = matriz[:i] + matriz[i+1:]
    submatriz = [fila[j+1: j + tis[i]] for fila in submatriz]
    return submatriz


def pre_procesamiento_r3(variables, tis, m):
    """
    Autor: Daniel Correa, Aurelio Vivas, Kellys Santa, John Lourido

    Permite obtener las restricciones en formato de solver para el tercer conjunto de restricciones del modelo

    R3:
    Para cada Xij:

    Sum n=1 hasta K sum m = B hasta B + Ti -1 de Xnm - Sum m=1 hasta B de Xim <= (1-Xij)*M
    Explicacion:
    Para cada variable de decision se calcula su submatriz y se retorna la expresion para la suma de los valores de
    esta submatriz <= (1 - variable)*M

    :param variables: matriz con variables de descion
    :param tis: tiempos de cosecha de cada parcela
    :param m: valor cota superior para invalidar o validar restriccion
    :return: Arreglo con restricciones en formato solver
    """
    resultado = []
    for i, fila in enumerate(variables):
        for j, variable in enumerate(fila):
            submatriz = sub_matriz(i, j, variables, tis)
            # Construir restriccion para variable
            if [[]] != submatriz:
                expresion = [' + '.join(elemento) for elemento in submatriz]
                resultado.append(' + '.join(expresion) + ' + %i%s <= %i' % (m,variable[1:],m))
    return resultado

def planificacion_parcelas(solucion,variables,k,b):
    """
    Autor: Aurelio Vivas

    Permite obtener la planificación de cosecha de las parcelas en una matriz
    donde las filas reprsentan cada parcela desde i hasta la k esima, las 
    columnas los instantes desde i hasta b esimo.

    :param variables: matriz con variables de decision
    :param solución: diccionario de la forma {variable:valor} donde esta el valor de cada variable de decisión
    :param k: número de parcelas
    :param b: número de instantes de cosecha.
    :return: matriz de unos y ceros, uno si la parcela en la fila i va a ser cosechada en el instante j.
    """
    xs = []
    
    # Guardando solo aquellas variables cuyo valor es igual a 1 en xs
    for llave in solucion.keys():
        valor = solucion[llave]
        if int(valor) == 1:
            xs.append(llave)

    # Generando la matriz de planificación de cosechas
    posiciones = []
    for x_i in xs:
        i = int(x_i.replace('x_','')) - 1
        fila = int(i / b)
        columna = i % b
        posiciones.append((fila,columna))
    
    matriz = [[0 for i in range(b)] for j in range(k)]
    for i,j in posiciones:
        matriz[i][j] = 1

    return matriz
