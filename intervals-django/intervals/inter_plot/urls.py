from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload_file/$', views.UploadView.as_view(), name='upload_file'),
    url(r'^testing_view/$', views.testing_view, name='testing_view'),
]