from django.shortcuts import render
from san_site.models import Section


def index(request):
    sections = Section.objects.filter(parent_guid="---")
    return render(request, 'index.html', {'sections': sections})



