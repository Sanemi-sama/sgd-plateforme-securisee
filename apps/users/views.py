from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from .models import User
from .forms import LoginForm, UserCreateForm, UserUpdateForm, ProfileForm
from apps.audit.utils import log_action


def require_admin(view_func):
    """Décorateur : admin seulement."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Accès refusé.")
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_manager(view_func):
    """Décorateur : manager ou admin."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_manager:
            messages.error(request, "Accès refusé.")
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Authentification ──────────────────────────────────────────
class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return render(request, 'users/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Enregistre l'IP
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
            user.last_login_ip = ip.split(',')[0].strip() if ip else None
            user.save(update_fields=['last_login_ip'])
            login(request, user)
            log_action(user, 'LOGIN', f"Connexion depuis {user.last_login_ip}")
            return redirect('dashboard:home')
        return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    log_action(request.user, 'LOGOUT', "Déconnexion")
    logout(request)
    return redirect('users:login')


# ── Liste des utilisateurs ────────────────────────────────────
@login_required
@require_manager
def user_list(request):
    users = User.objects.all().order_by('-created_at')
    return render(request, 'users/user_list.html', {'users': users})


# ── Créer un utilisateur ──────────────────────────────────────
@login_required
@require_admin
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_action(request.user, 'CREATE_USER', f"Création de l'utilisateur {user.username}")
            messages.success(request, f"Utilisateur {user.username} créé avec succès.")
            return redirect('users:list')
    else:
        form = UserCreateForm()
    return render(request, 'users/user_form.html', {'form': form, 'action': 'Créer'})


# ── Modifier un utilisateur ───────────────────────────────────
@login_required
@require_admin
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            log_action(request.user, 'UPDATE_USER', f"Modification de {user.username}")
            messages.success(request, "Utilisateur mis à jour.")
            return redirect('users:list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form, 'action': 'Modifier', 'target': user})


# ── Supprimer un utilisateur ──────────────────────────────────
@login_required
@require_admin
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.user == user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('users:list')
    if request.method == 'POST':
        username = user.username
        user.delete()
        log_action(request.user, 'DELETE_USER', f"Suppression de {username}")
        messages.success(request, f"Utilisateur {username} supprimé.")
        return redirect('users:list')
    return render(request, 'users/user_confirm_delete.html', {'target': user})


# ── Profil personnel ──────────────────────────────────────────
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            log_action(request.user, 'UPDATE_PROFILE', "Mise à jour du profil")
            messages.success(request, "Profil mis à jour.")
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/profile.html', {'form': form})


# ── Changement de mot de passe ────────────────────────────────
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_action(request.user, 'CHANGE_PASSWORD', "Changement de mot de passe")
            messages.success(request, "Mot de passe modifié avec succès.")
            return redirect('users:profile')
    else:
        form = PasswordChangeForm(request.user)
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'
    return render(request, 'users/change_password.html', {'form': form})
