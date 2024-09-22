import os
import shutil
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import NumberOfCamerasForm

def homepage(request):
    if request.method == 'POST':
        form = NumberOfCamerasForm(request.POST)
        if form.is_valid():
            num_cameras = form.cleaned_data['num_cameras']
            request.session['num_cameras'] = num_cameras
            return redirect('get_intri_yml')
    else:
        form = NumberOfCamerasForm()
    return render(request, 'homepage.html', {'form': form})

def documentation(request):
    return render(request, 'documentation.html')

def reset(request):
    if request.method == 'POST':
        try:
            extri_data_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'extri_data')
            intri_data_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'intri_data')
            extri_yml_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'data', 'examples', 'my_dataset', 'extri.yml')
            intri_yml_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'data', 'examples', 'my_dataset', 'intri.yml')
            videos_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'data', 'examples', 'my_dataset', 'videos')
            images_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'data', 'examples', 'my_dataset', 'images')
            audio_videos_path = os.path.join(settings.BASE_DIR, 'sync', 'videos')
            audio_audio_path = os.path.join(settings.BASE_DIR, 'sync', 'audio')
            audio_output_path = os.path.join(settings.BASE_DIR, 'sync', 'output')
            final_output_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'output')
            yolov5m_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'yolov5m.pt')
            models_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'data', 'models')


            # Remove the directories if they exist
            if os.path.exists(extri_data_path):
                shutil.rmtree(extri_data_path)
            if os.path.exists(intri_data_path):
                shutil.rmtree(intri_data_path)
            if os.path.exists(extri_yml_path):
                os.remove(extri_yml_path)
            if os.path.exists(intri_yml_path):
                os.remove(intri_yml_path)
            if os.path.exists(videos_path):
                shutil.rmtree(videos_path)
                os.makedirs(videos_path)
            if os.path.exists(images_path):
                shutil.rmtree(images_path)
            if os.path.exists(audio_videos_path):
                shutil.rmtree(audio_videos_path)
                os.makedirs(audio_videos_path)
            if os.path.exists(audio_audio_path):
                shutil.rmtree(audio_audio_path)
            if os.path.exists(audio_output_path):
                shutil.rmtree(audio_output_path)
            if os.path.exists(final_output_path):
                shutil.rmtree(final_output_path)
            if os.path.exists(yolov5m_path):
                os.remove(yolov5m_path)
            if os.path.exists(models_path):
                shutil.rmtree(models_path)

            # Redirect to the homepage after reset
            return redirect('homepage')
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)

    return render(request, 'homepage.html')