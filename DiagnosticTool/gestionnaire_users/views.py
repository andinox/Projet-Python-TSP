from django.shortcuts import render, redirect
from django.contrib.auth import logout

def logout_user(request):
    """
    function that logout a user
    :param request:
    :return: login page
    """
    logout(request)
    return redirect('login_page')

