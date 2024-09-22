from django import forms

class UploadVideosForm(forms.Form):
    def __init__(self, *args, **kwargs):
        num_cameras = kwargs.pop('num_cameras', 1)
        super(UploadVideosForm, self).__init__(*args, **kwargs)
        for i in range(num_cameras):
            self.fields[f'video_{i+1}'] = forms.FileField(label=f'Camera {i+1}')

class CheckerboardInfoForm(forms.Form):
    checkerboard_rows = forms.IntegerField(label='Checkerboard Rows', min_value=1, max_value=20)
    checkerboard_columns = forms.IntegerField(label='Checkerboard Columns', min_value=1, max_value=20)
    square_size = forms.FloatField(label='Square Size (meters)')
