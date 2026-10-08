from django.shortcuts import render, redirect, get_object_or_404
from .models import EvaluacionFinanciera
from .forms import EvaluacionFinancieraForm
from decimal import Decimal

def ingreso_datos(request):
    if request.method == 'POST':
        form = EvaluacionFinancieraForm(request.POST, request.FILES)
        if form.is_valid():
            evaluacion = form.save()
            return redirect('diagnostico_financiero:dashboard', evaluacion_id=evaluacion.id)
    else:
        form = EvaluacionFinancieraForm()
    
    return render(request, 'diagnostico_financiero/ingreso_datos.html', {'form': form})

def dashboard(request, evaluacion_id):
    evaluacion = get_object_or_404(EvaluacionFinanciera, id=evaluacion_id)
    
    # Cálculos Financieros
    # Utilidad Neta
    utilidad_neta = evaluacion.ventas_mensuales - evaluacion.costos_variables_totales - evaluacion.costos_fijos_mensuales
    
    # Margen de Contribución
    margen_contribucion = evaluacion.ventas_mensuales - evaluacion.costos_variables_totales
    
    # Margen Neto
    if evaluacion.ventas_mensuales > 0:
        margen_neto_porcentaje = (utilidad_neta / evaluacion.ventas_mensuales) * 100
    else:
        margen_neto_porcentaje = Decimal(0)
        
    # Punto de Equilibrio
    if evaluacion.ventas_mensuales > 0 and margen_contribucion > 0:
        margen_contribucion_porcentaje = margen_contribucion / evaluacion.ventas_mensuales
        punto_equilibrio = evaluacion.costos_fijos_mensuales / margen_contribucion_porcentaje
    else:
        punto_equilibrio = Decimal(0)
    
    context = {
        'evaluacion': evaluacion,
        'utilidad_neta': utilidad_neta,
        'margen_contribucion': margen_contribucion,
        'margen_neto_porcentaje': margen_neto_porcentaje,
        'punto_equilibrio': punto_equilibrio,
    }
    return render(request, 'diagnostico_financiero/dashboard.html', context)
