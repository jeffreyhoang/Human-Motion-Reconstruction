import os
import shutil
import subprocess
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings


def check_calibration(request):
    if request.method == 'POST':
        try:
            # Define the source and destination paths
            base_dir = settings.BASE_DIR
            source_path = os.path.join(base_dir, 'EasyMocap', 'extri_data', 'extri.yml')
            destination_dir = os.path.join(base_dir, 'EasyMocap', 'intri_data', 'output')
            destination_path = os.path.join(destination_dir, 'extri.yml')

            # Check if the source file exists
            if not os.path.isfile(source_path):
                return HttpResponse("Source file not found.", status=404)

            # Ensure the destination directory exists
            if not os.path.isdir(destination_dir):
                return HttpResponse("Destination directory not found.", status=404)

            # Move the file
            shutil.copy(source_path, destination_path)

            # Define path to the script
            check_calibration_script = os.path.join(settings.BASE_DIR, 'EasyMocap', 'apps', 'calibration', 'check_calib.py')

            intri = 'EasyMocap/intri_data'
            extri = 'EasyMocap/extri_data'

            # Check if the check calibration script file exists
            if not os.path.isfile(check_calibration_script):
                return HttpResponse("Check calibration script file not found.", status=404)
            
            # Run the check calibration script using subprocess
            try:
                check_calibration_command = f'python3 {check_calibration_script} {extri} --out {intri}/output --show'
                check_calibration_result = subprocess.run(check_calibration_command, shell=True, cwd=settings.BASE_DIR, capture_output=True, text=True)
                if check_calibration_result.returncode != 0:
                    return HttpResponse(f"Check calibration script execution failed: {check_calibration_result.stderr}", status=500)
            except Exception as e:
                        return HttpResponse(f"An error occurred: {str(e)}", status=500)
                    
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
        
        # All scripts ran successfully
        url = reverse('fit')
        success_html = f"""
        <html>
            <body>
                <h1>Success!</h1>
                <p>Your operation was successful.</p>
                <p>Click here to go to <a href="{url}">fit SMPL</a>.</p>
            </body>
        </html>
        """
        return HttpResponse(success_html)


    return render(request, 'check_calibration/check_calibration.html')