import os

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest

from requestdataapp.exceptions import AdminException
from .forms import UserBioForm, UploadFileForm


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get('a', '')
    b = request.GET.get('b', '')
    result = a + b
    context = {
        'a': a,
        'b': b,
        'result': result,
    }
    return render(request, 'requestdataapp/request-query-params.html', context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        'form': UserBioForm(),
    }
    return render(request, 'requestdataapp/user-bio-form.html', context=context)


def get_file_size(file):
    path = os.path.abspath(file.name)
    file_size = os.path.getsize(path)
    # print('File size:', file_size, 'byte')
    return file_size


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            my_file = form.cleaned_data['file']
            size = get_file_size(my_file)
            if size < 1048576:
                fs = FileSystemStorage()
                filename = fs.save(my_file.name, my_file)
                print(f'saved file {filename}')
            else:
                raise AdminException("File Is Too Big")
    else:
        form = UploadFileForm()
    context = {
        'form': form,
    }
    return render(request, "requestdataapp/file-upload.html", context=context)












