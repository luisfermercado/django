from diagnostico_financiero.forms import EvaluacionFinancieraForm

data = {
    'nombre_emprendimiento': 'Test',
    'etapa': 'Sesión 1: Diagnóstico Inicial',
    'nivel_flujo_caja': '1',
    'nivel_fuentes_financiacion': '1',
    'ventas_mensuales': '1,000',
    'costos_variables_totales': '100',
    'costos_fijos_mensuales': '100',
    'activo_corriente': '12',
    'pasivo_corriente': '4,345',
    'total_activo': '1,000',
    'total_pasivo': '800',
    'patrimonio_neto': '300,000'
}

form = EvaluacionFinancieraForm(data=data)
print("Is valid?", form.is_valid())
print("Errors:", form.errors)
