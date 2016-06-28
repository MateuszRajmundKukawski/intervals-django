from django import forms


class UploadFileForm(forms.Form):
    description = forms.CharField(max_length=50)
    file = forms.FileField()


class ParamForm(forms.Form):
    ccuracy_liczba_probek = forms.IntegerField(initial=8)
    accuracyPaceDiffForIntervalSearch = forms.IntegerField(initial=10)
    point_distance_minimal_between_interwalsS = forms.IntegerField(initial=1)
    filter_orderS = forms.IntegerField(initial=5)
    wiekS = forms.IntegerField(initial=3)
    zakresyTetnaProcentyS = forms.CharField(initial="54 63 73 81 91 100")

