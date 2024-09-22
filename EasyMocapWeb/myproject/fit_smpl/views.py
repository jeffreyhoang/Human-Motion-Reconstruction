import os
import shutil
import subprocess
from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from .forms import UploadVideosForm

def fit_view(request):

    num_cameras = request.session.get('num_cameras', 1)

    if request.method == 'POST':
        # Define path to script files.
        mvimage_yml = os.path.join(settings.BASE_DIR, 'EasyMocap', 'config', 'datasets', 'mvimage.yml')
        fitSMPL_yml = os.path.join(settings.BASE_DIR, 'EasyMocap', 'config', 'mv1p', 'detect_triangulate_fitSMPL.yml')

        # Define path to dataset directory
        final_data_directory = os.path.join(settings.BASE_DIR, 'EasyMocap', 'data', 'examples', 'my_dataset')

        # Define path to yml files
        extri_yml = os.path.join(settings.BASE_DIR, 'EasyMocap', 'extri_data', 'extri.yml')
        intri_yml = os.path.join(settings.BASE_DIR, 'EasyMocap', 'extri_data', 'intri.yml')

        # Ensure yml files exist
        if not os.path.isfile(extri_yml) or not os.path.isfile(intri_yml):
            return HttpResponse("One or both YML files not found.", status=404)
        
        # Move the YML files to the dataset directory
        shutil.copy(extri_yml, os.path.join(settings.BASE_DIR, 'EasyMocap', final_data_directory, 'extri.yml'))
        shutil.copy(intri_yml, os.path.join(settings.BASE_DIR, 'EasyMocap', final_data_directory, 'intri.yml'))

        # Upload unsynced videos
        form = UploadVideosForm(request.POST, request.FILES, num_cameras=num_cameras)
        if form.is_valid():
            upload_dir = os.path.join(settings.BASE_DIR, 'sync', 'videos')

            for i in range(num_cameras):
                video = form.cleaned_data[f'video_{i+1}']
                # Define the file name (01.mp4, 03.mp4, etc.)
                file_number = str((i + 1) * 2 - 1).zfill(2)
                save_path = os.path.join(upload_dir, f'{file_number}.mp4')
                with open(save_path, 'wb+') as destination:
                    for chunk in video.chunks():
                        destination.write(chunk)
                                
        # Run script to syncrhonize videos
        sync_videos_dir = os.path.join(settings.BASE_DIR, 'sync', 'output')

        if not os.path.exists(sync_videos_dir):
            try:
                syn_video_script = f'python sync.py'
                syn_video_result = subprocess.run(syn_video_script, shell=True, cwd=os.path.join(settings.BASE_DIR, 'sync'), capture_output=True, text=True)
                if syn_video_result.returncode != 0:
                    return HttpResponse(f"Syn video script execution failed: {syn_video_result.stderr}", status=500)
            except Exception as e:
                return HttpResponse(f"An error occurred: {str(e)}", status=500)

        
        # Move synced videos into final dataset directory
        try:
            sync_videos_dir = os.path.join(settings.BASE_DIR, 'sync', 'output')
            final_videos_dir = os.path.join(final_data_directory, 'videos')

            # Ensure the final destination directory exists
            if not os.path.exists(final_videos_dir):
                os.makedirs(final_videos_dir)

            # Copy each synchronized video
            for filename in os.listdir(sync_videos_dir):
                if filename.endswith(".mp4"):  # Only copy .mp4 files
                    shutil.copy2(os.path.join(sync_videos_dir, filename), os.path.join(final_videos_dir, filename))
        except Exception as e:
            return HttpResponse(f"Error copying synchronized videos: {str(e)}", status=500)
        


        # Run fit_smpl script
        try:
            fit_smpl_script = f'emc --data {mvimage_yml} --exp {fitSMPL_yml} --root {final_data_directory} --subs_vis 07 01 03 05'
            fit_smpl_result = subprocess.run(fit_smpl_script, shell=True, cwd=os.path.join(settings.BASE_DIR, 'EasyMocap'), capture_output=True, text=True)
            if fit_smpl_result.returncode != 0:
                return HttpResponse(f"Fit SMPL script execution failed: {fit_smpl_result.stderr}", status=500)
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
        
        # All scripts ran successfully
        url = reverse('homepage')
        success_html = f"""
        <html>
            <body>
                <h1>Success!</h1>
                <p>Your operation was successful.</p>
                <p>Click here to go to return to <a href="{url}">homepage</a>.</p>
            </body>
        </html>
        """
        return HttpResponse(success_html)

    else:
        form = UploadVideosForm(num_cameras=num_cameras)

    return render(request, 'fit_smpl/fit_smpl.html', {'form': form})
