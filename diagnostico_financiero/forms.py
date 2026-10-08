from django import forms
from .models import EvaluacionFinanciera

class EvaluacionFinancieraForm(forms.ModelForm):
    class Meta:
        model = EvaluacionFinanciera
        fields = [
            'nombre_emprendimiento',
            'etapa',
            'nivel_flujo_caja',
            'nivel_fuentes_financiacion',
            'ventas_mensuales',
            'costos_variables_totales',
            'costos_fijos_mensuales',
            'plan_accion_file'
        ]
        widgets = {
            'nombre_emprendimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'etapa': forms.Select(attrs={'class': 'form-control'}),
            'nivel_flujo_caja': forms.Select(attrs={'class': 'form-control'}),
            'nivel_fuentes_financiacion': forms.Select(attrs={'class': 'form-control'}),
            'ventas_mensuales': forms.NumberInput(attrs={'class': 'form-control'}),
            'costos_variables_totales': forms.NumberInput(attrs={'class': 'form-control'}),
            'costos_fijos_mensuales': forms.NumberInput(attrs={'class': 'form-control'}),
            'plan_accion_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
