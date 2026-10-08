from django.db import models

class EvaluacionFinanciera(models.Model):
    ETAPAS_CHOICES = [
        ('Sesión 1: Diagnóstico Inicial', 'Sesión 1: Diagnóstico Inicial'),
        ('Sesión 4: Evaluación Final', 'Sesión 4: Evaluación Final'),
    ]

    nombre_emprendimiento = models.CharField(max_length=200, verbose_name="Nombre del emprendimiento")
    etapa = models.CharField(max_length=50, choices=ETAPAS_CHOICES, verbose_name="Etapa de evaluación")
    
    # Autoevaluación
    nivel_flujo_caja = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Nivel de conocimiento en flujo de caja (1-5)")
    nivel_fuentes_financiacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Nivel de conocimiento en fuentes de financiación (1-5)")
    
    # Datos Cuantitativos
    ventas_mensuales = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ventas mensuales")
    costos_variables_totales = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Costos variables totales")
    costos_fijos_mensuales = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Costos fijos mensuales")
    
    # Entregable
    plan_accion_file = models.FileField(upload_to='planes_accion/', blank=True, null=True, verbose_name="Plan de acción financiero a 12 meses")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_emprendimiento} - {self.etapa}"
