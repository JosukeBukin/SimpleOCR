from django.http import HttpResponse
from django.shortcuts import redirect, render
from docsreader.settings import BASE_DIR
from .models import UploadedFiles
import os, time
from Include import reader

# чистит директории с файлами
def cleaner_decorator(func):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        finally:
            time.sleep(5)
            reader.cleaner()
    return wrapper

# responds to post and serves result back
@cleaner_decorator
def page(request):
    absolute_path = str(BASE_DIR) + os.path.sep + 'downloader' + os.path.sep + 'media' + os.path.sep + 'saved_files'
    context = reader.file_discoverer(absolute_path)
    if request.method == 'POST':
        try:
            index = reader.find_index(str(UploadedFiles.objects.create(file=request.FILES.get('file'))))
            file_name = reader.get_file_name(index)
            if file_name is not None:
                file_path = os.path.join(absolute_path, file_name)
                reader.ocr_resolver(file_path)
                res_path = reader.res_finder(file_name)
                serve_file(res_path, file_name)
        except Exception as e:
            print(f'Error: {e}')
            pass
    return render(request, 'hello.html', context) 

# file service
def serve_file(res_path, file_name):
    try:
        with open(res_path, 'rb') as f:
            contents = f.read()
            print(contents)
            response = HttpResponse(contents,'application/downloader; charset=utf-8') 
            response['Content-Disposition'] = f'attachment; filename="{file_name}_result.txt"'
            print(str(response))
            return response 
    except Exception as e:
        print(f'Error: {e}')
        pass