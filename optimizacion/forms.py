import os

from django import forms


class ProcesamientoForm(forms.Form):

    archivo = forms.FileField(label='Archivo de entrada')
    parcelas = None
    tiempos = None
    total_tiempo = None
    matriz_utilidad = []

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        name, extension = os.path.splitext(archivo.name)
        if extension not in ['.txt']:
            self.add_error('archivo', 'El formato de entrada debe ser txt')
            return archivo

        # Las lineas de archivo corresponden a lo que necesitamos
        lecutra = archivo.read().decode('utf-8').split('\n')
        self.parcelas = int(lecutra[0])
        self.tiempos = [int(valor) for valor in lecutra[1].split(' ')]
        self.total_tiempo = int(lecutra[2])
        for utilidades in lecutra[3:]:
            self.matriz_utilidad.append([int(valor) for valor in utilidades.split(' ')])
        return archivo

    def get_clean_archivo(self):
        return self.parcelas, self.tiempos, self.total_tiempo, self.matriz_utilidad