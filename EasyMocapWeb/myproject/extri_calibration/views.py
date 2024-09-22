import os
import subprocess
from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import UploadVideosForm, CheckerboardInfoForm
from django.http import HttpResponse
from django.conf import settings

def get_extri_yml_view(request):
    num_cameras = request.session.get('num_cameras', 1)
    video_upload_form = UploadVideosForm(request.POST or None, request.FILES or None, num_cameras=num_cameras)
    checkerboard_info_form = CheckerboardInfoForm(request.POST or None)

    if request.method == 'POST':
        # Upload videos for extrinsic calibration
        if video_upload_form.is_valid():
            # Define the directory where files will be saved
            root_dir = os.path.join(settings.BASE_DIR, 'EasyMocap')
            upload_dir = os.path.join(root_dir, 'extri_data', 'videos')
            # Create the directory if it doesn't exist
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            for i in range(num_cameras):
                video = video_upload_form.cleaned_data[f'video_{i+1}']
                # Define the file name (01.mp4, 03.mp4, etc.)
                file_number = str((i + 1) * 2 - 1).zfill(2)
                save_path = os.path.join(upload_dir, f'{file_number}.mp4')
                with open(save_path, 'wb+') as destination:
                    for chunk in video.chunks():
                        destination.write(chunk)
        
        # Get checkerboard information
        if checkerboard_info_form.is_valid():
            request.session['checkerboard_rows'] = checkerboard_info_form.cleaned_data['checkerboard_rows']
            request.session['checkerboard_columns'] = checkerboard_info_form.cleaned_data['checkerboard_columns']
            request.session['square_size'] = checkerboard_info_form.cleaned_data['square_size']

        num_rows = request.session.get('checkerboard_rows') - 1
        num_columns = request.session.get('checkerboard_columns') - 1
        square_size = request.session.get('square_size')

        # Define the path to the script
        extract_script_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'scripts', 'preprocess', 'extract_video.py')
        detect_script_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'apps', 'calibration', 'detect_chessboard.py')
        calib_script_path = os.path.join(settings.BASE_DIR, 'EasyMocap', 'apps', 'calibration', 'calib_extri.py')

        # The required path argument in the expected format
        data_directory = 'EasyMocap/extri_data'
        intri_data_directory = 'EasyMocap/intri_data'
        extri_data_directory = 'EasyMocap/extri_data'

        # Check if the script extract file exists
        if not os.path.isfile(extract_script_path):
            return HttpResponse("Extract script file not found.", status=404)

        # Run the extract script using subprocess
        try:
            extract_command = f'python3 {extract_script_path} --no2d {data_directory}'
            extract_result = subprocess.run(extract_command, shell=True, cwd=settings.BASE_DIR, capture_output=True, text=True)
            if extract_result.returncode != 0:
                return HttpResponse(f"Extract script execution failed: {extract_result.stderr}", status=500)
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
        
        # Check if the detect script file exists
        if not os.path.isfile(detect_script_path):
            return HttpResponse("Detect script file not found.", status=404)
        
        # Run the detect script using subprocess
        try:
            detect_command = f'python3 {detect_script_path} {data_directory} --out {data_directory}/output/calibration --pattern {num_rows},{num_columns} --grid {square_size}'
            detect_result = subprocess.run(detect_command, shell=True, cwd=settings.BASE_DIR, capture_output=True, text=True)
            if detect_result.returncode != 0:
                return HttpResponse(f"Detect script execution failed: {detect_result.stderr}", status=500)
        except Exception as e:
            return HttpResponse(f"An error occurred during detect script execution: {str(e)}", status=500)

        # Check if the extri_calib script file exists
        if not os.path.isfile(calib_script_path):
            return HttpResponse("Calib script file not found.", status=404)
        
        # Run the extri_calib script using subprocess
        try:
            calib_command = f'python3 {calib_script_path} {extri_data_directory} --intri {intri_data_directory}/output/intri.yml'
            calib_result = subprocess.run(calib_command, shell=True, cwd=settings.BASE_DIR, capture_output=True, text=True)
            if calib_result.returncode != 0:
                return HttpResponse(f"Calib script execution failed: {calib_result.stderr}", status=500)
        except Exception as e:
            return HttpResponse(f"An error occurred during calib script execution: {str(e)}", status=500)

        else:
            form = UploadVideosForm(num_cameras=num_cameras)
        
        # All scripts ran successfully
        check_calibration_url = reverse('check_calibration')
        get_smpl_url = reverse('fit')
        success_html = f"""
        <html>
            <body>
                <h1>Success!</h1>
                <p>Your operation was successful.</p>
                <p>Click here to go to <a href="{check_calibration_url}">check calibration</a> or click here to go to <a href="{get_smpl_url}">fit SMPL</a>.</p>
            </body>
        </html>
        """
        return HttpResponse(success_html)
    
    return render(request, 'extri_calibration/get_extri_yml.html', {
        'video_upload_form': video_upload_form,
        'checkerboard_info_form': checkerboard_info_form
    })