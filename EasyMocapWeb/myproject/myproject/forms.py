from django import forms

class NumberOfCamerasForm(forms.Form):
    num_cameras = forms.IntegerField(label='Enter the number of cameras to get started', min_value=4, max_value=20)