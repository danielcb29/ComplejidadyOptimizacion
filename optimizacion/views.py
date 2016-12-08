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
        parcelas, tiempos, total_tiempo, matriz_utilidad = form.get_clean_archivo()
        #  Uso de funcionalidades tipo helper para pre proceso y calculo de resultado
        
        return super(ProcesamientoView, self).form_valid(form)

    def get_success_url(self):
        return reverse('optimizacion:inicio')


#  Toda funcionalidad helper para pre procesar y calcular el resultado

