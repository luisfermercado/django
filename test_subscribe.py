import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from blog.forms import SubscribeForm

data = {
    "email": "naglesnora7@gmail.com",
    "diagnosis": '{"scores":{"num":2,"dat":2,"nar":0},"capital":"inv","recommendation":"Pitch Lab","answers":[2,0,2,0,"inv"]}'
}

form = SubscribeForm(data)
print("Is valid?", form.is_valid())
print("Errors:", form.errors)
print("Cleaned data:", getattr(form, 'cleaned_data', None))
