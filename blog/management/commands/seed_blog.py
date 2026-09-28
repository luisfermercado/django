from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from blog.models import Category, Post, Tag

CATEGORIES = {
    "finanzas": ("Finanzas", "Modelos, proyecciones y valoración que resisten las preguntas del comité."),
    "financiacion": ("Financiación", "Crédito, inversión, fondos públicos y cooperación en Colombia."),
    "pitch": ("Pitch", "Cómo contar tu empresa para que el capital llegue."),
}

TAGS = ["Flujo de caja", "Valoración", "Crédito", "Inversión ángel", "Data room", "Convocatorias", "Oratoria", "Indicadores"]

POSTS = [
    {
        "title": "Las tres barras que revisa quien pone el dinero",
        "category": "financiacion", "pillar": Post.Pillar.CAPITAL, "featured": True,
        "tags": ["Inversión ángel", "Crédito"],
        "excerpt": "Números, datos y narrativa: por qué casi siempre falla una de las tres y cómo saber cuál es la tuya antes de sentarte con un inversionista o un banco.",
        "body": "Cuando una empresa con tracción no consigue capital, rara vez el problema es el negocio. Casi siempre falla una de tres cosas: los números no se sostienen, los datos no respaldan lo que dicen los números, o la historia no convence.\n\nLos números son la base. Un inversionista o un analista de crédito quiere ver estados financieros completos, proyecciones con supuestos explícitos y una valoración que puedas defender sin titubear.\n\nLos datos son la prueba. Si tus indicadores no se miden cada mes, nadie puede verificar que la tracción es real. Un tablero sencillo y un data room ordenado cambian la conversación.\n\nLa narrativa es el vehículo. Buenos números contados sin estructura se pierden en un comité. El pitch pesa tanto como la hoja de cálculo.\n\nEl primer paso es saber cuál de las tres barras es la más baja en tu caso. Para eso creamos el Capital Check AI.",
    },
    {
        "title": "Cómo proyectar tu flujo de caja a tres años sin inventar",
        "category": "finanzas", "pillar": Post.Pillar.NUMBERS,
        "tags": ["Flujo de caja", "Valoración"],
        "excerpt": "Una proyección creíble se construye desde los supuestos, no desde el resultado que quieres mostrar. Te mostramos el orden que usamos en Capital Sprint.",
        "body": "La mayoría de proyecciones que vemos empiezan por el final: el fundador sabe cuánto quiere vender en el año tres y reparte hacia atrás. El comité lo nota en la primera pregunta.\n\nEmpieza por los impulsores: cuántos clientes nuevos, a qué precio, con qué retención y con qué costo de adquisición. Cada número debe tener una fuente: tu histórico, un contrato firmado o un referente del sector.\n\nLuego traduce esos impulsores a ingresos, costos y capital de trabajo. En Colombia, los plazos de pago a proveedores y de cobro a clientes suelen explicar más problemas de caja que el margen.\n\nPor último, arma tres escenarios y escribe en una página qué tendría que pasar para que se cumpla cada uno. Esa página es la que defiende tu valoración.",
    },
    {
        "title": "Qué indicadores medir cada mes si vas a pedir crédito",
        "category": "finanzas", "pillar": Post.Pillar.DATA,
        "tags": ["Indicadores", "Crédito", "Data room"],
        "excerpt": "Los bancos y las líneas de fomento miran pocos indicadores, pero los quieren consistentes. Esta es la lista corta que recomendamos.",
        "body": "No necesitas cien métricas. Necesitas cinco o seis que midas igual todos los meses y que puedas explicar.\n\nPara crédito, las más revisadas son el margen bruto, el EBITDA, la rotación de cartera, la rotación de inventario, el nivel de endeudamiento y la cobertura del servicio de la deuda.\n\nLo importante es la serie: doce meses seguidos del mismo indicador, calculado de la misma forma, dicen más que un pico aislado.\n\nGuárdalos en un tablero y en una carpeta del data room con los soportes. Cuando el analista pregunte, la respuesta estará a un clic.",
    },
    {
        "title": "El pitch de dos minutos: estructura que funciona en comités",
        "category": "pitch", "pillar": Post.Pillar.NARRATIVE,
        "tags": ["Oratoria"],
        "excerpt": "Problema, solución, tracción, modelo, equipo y la cifra que pides. Cómo ordenarlos para que el comité recuerde lo importante.",
        "body": "Dos minutos alcanzan si sabes qué dejar por fuera. El error más común es explicar el producto en detalle y llegar sin tiempo a la tracción.\n\nAbre con el problema en una frase y con un dato. Sigue con la solución, pero cuéntala desde el cliente, no desde la tecnología.\n\nDedica la mitad del tiempo a la tracción y al modelo de negocio: cuánto vendes, cuánto te cuesta vender y por qué eso escala.\n\nCierra con el equipo y con una cifra concreta: cuánto capital buscas y en qué lo vas a usar. Practícalo en voz alta hasta que puedas decirlo sin mirar las diapositivas.",
    },
    {
        "title": "Convocatorias públicas: cómo leer los términos de referencia",
        "category": "financiacion", "pillar": Post.Pillar.CAPITAL,
        "tags": ["Convocatorias"],
        "excerpt": "Antes de escribir una sola línea de la propuesta, revisa estos cinco puntos de los términos de referencia.",
        "body": "Los recursos no reembolsables son una gran fuente para empresas en crecimiento, pero cada convocatoria tiene reglas propias.\n\nRevisa primero los requisitos habilitantes: tamaño de empresa, sector, antigüedad y ubicación. Si no cumples uno, no sigas.\n\nLuego mira la contrapartida exigida y si puede ser en especie. Muchas empresas se enteran tarde de que deben aportar un porcentaje en efectivo.\n\nFinalmente, lee la matriz de evaluación y escribe la propuesta en el mismo orden. Facilita el trabajo del evaluador y sube tu puntaje.",
    },
]


class Command(BaseCommand):
    help = "Carga categorías, etiquetas y artículos de ejemplo para el blog."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Borra los artículos existentes antes de cargar.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Post.objects.all().delete()

        categories = {
            slug: Category.objects.update_or_create(slug=slug, defaults={"name": name, "description": desc})[0]
            for slug, (name, desc) in CATEGORIES.items()
        }
        tags = {}
        for name in TAGS:
            tags[name], _ = Tag.objects.get_or_create(name=name, defaults={"slug": _slug(name)})

        now = timezone.now()
        created = 0
        for i, data in enumerate(POSTS):
            if Post.objects.filter(title=data["title"]).exists():
                continue
            post = Post.objects.create(
                title=data["title"],
                category=categories[data["category"]],
                pillar=data["pillar"],
                excerpt=data["excerpt"],
                body=data["body"],
                featured=data.get("featured", False),
                status=Post.Status.PUBLISHED,
                published_at=now - timedelta(days=i * 6),
            )
            post.tags.set(tags[t] for t in data["tags"])
            created += 1

        if options["verbosity"]:
            self.stdout.write(self.style.SUCCESS(f"{created} artículo(s) creados."))


def _slug(name):
    from django.utils.text import slugify

    return slugify(name)
