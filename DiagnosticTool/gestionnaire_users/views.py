from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import AvatarUploadForm
from .models import Profile
from django.contrib import messages

def logout_user(request):
    """
    function that logout a user
    :param request:
    :return: login page
    """
    logout(request)
    return redirect('login_page')


def user_info(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AvatarUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Photo de profil bien ajouté :)")

            return redirect('infoUser')
    else:
        form = AvatarUploadForm(instance=profile)

    return render(request, 'gestionnaire_users/registration/userInfos.html', {
        'user': request.user,
        'profile': profile,
        'form': form
    })
