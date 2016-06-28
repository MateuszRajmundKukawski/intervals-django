import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.generic.edit import FormView

from .forms import UploadFileForm, ParamForm
from .models import GpxData
from .utils import parse_training, datetime_js_to_date


def index(request):
    template = loader.get_template('inter_plot/index.html')
    return HttpResponse(template.render(request))


def save_file_to_db(gpx_file, description, training_date_str):
    gpx_data = json.dumps(parse_training(gpx_file, dt=False))
    training_date = datetime_js_to_date(training_date_str)
    g = GpxData(
        gpx=gpx_data,
        description=description,
        training_date=training_date)
    g.save()


def testing_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            print request.POST
            save_file_to_db(
                request.FILES['file'],
                request.POST['description'],
                request.POST['training_date']
            )
            trainings = GpxData.objects.all().order_by('-training_date').order_by('-pub_date')
            return render(
                request,
                'inter_plot/trainings_list.html',
                {'test_text': 'test_text', 'trainings': trainings},
            )

    return render(
        request,
        'inter_plot/test_site.html',
        {'test_text': 'test_text_fail'})


class UploadView(FormView):
    template_name = 'inter_plot/upload_file.html'
    form_class = UploadFileForm

    def form_valid(self, form):
        return super(UploadView, self).form_valid(form)

class ParamView(FormView):
    template_name = 'inter_plot/param_form.html'
    form_class = ParamForm

    def form_valid(self, form):
        return super(ParamView, self).form_valid(form)


