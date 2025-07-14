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
        avatar = request.FILES.get('avatar')

        if avatar:
            if avatar.content_type not in ['image/jpeg', 'image/png', 'image/gif']:
                messages.error(request, "Ce format d'image n'est pas supporté. Veuillez utiliser JPG, PNG ou GIF.")
            elif form.is_valid():
                form.save()
                messages.success(request, "Photo de profil a bien été ajouté :)")
                return redirect('infoUser')
        else:
            messages.error(request, "Aucun fichier sélectionné.")
    else:
        form = AvatarUploadForm(instance=profile)

    return render(request, 'gestionnaire_users/registration/userInfos.html', {
        'user': request.user,
        'profile': profile,
        'form': form
    })
