from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.generic.edit import FormView

from .forms import UploadFileForm
from .models import GpxData


def index(request):
    template = loader.get_template('inter_plot/index.html')
    return HttpResponse(template.render(request))

def handle_uploaded_file(f):
    print(type(f))
    gpx_data = f.read()
    g = GpxData(gpx=gpx_data, description='jajaja')
    g.save()
    print('*'*100)

def testing_view(request):
    if request.method == 'POST':

        form = UploadFileForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return render(request, 'inter_plot/test_site.html', {'test_text': 'POST'})
    return render(request, 'inter_plot/test_site.html', {'test_text': 'DUPA'})

class UploadView(FormView):
    template_name = 'inter_plot/upload_file.html'
    form_class = UploadFileForm
    success_url = 'inter_plot/test_site.html'

    def form_valid(self, form):
        return super(UploadView, self).form_valid(form)


