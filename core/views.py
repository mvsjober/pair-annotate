from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings

#------------------------------------------------------------------------------

def register(request):
    error = None
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if request.POST['secret'] != settings.REGISTER_SECRET:
            error = 'Wrong secret!'
            
        if form.is_valid() and error == None:
            new_user = form.save()
            return HttpResponseRedirect("/")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {
        'form': form,
        'error': error,
    })
