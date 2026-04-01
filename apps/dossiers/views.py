from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Dossier, Client, Commentaire, PiecesJointes
from .forms import DossierForm, ClientForm, CommentaireForm, PieceJointeForm
from apps.audit.utils import log_action
from apps.users.views import require_manager


# ── Dossiers ──────────────────────────────────────────────────

@login_required
def dossier_list(request):
    qs = Dossier.objects.select_related('client', 'responsable', 'cree_par')

    # Filtres
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    priorite = request.GET.get('priorite', '')
    categorie = request.GET.get('categorie', '')

    if q:
        qs = qs.filter(
            Q(titre__icontains=q) |
            Q(reference__icontains=q) |
            Q(client__nom__icontains=q)
        )
    if statut:
        qs = qs.filter(statut=statut)
    if priorite:
        qs = qs.filter(priorite=priorite)
    if categorie:
        qs = qs.filter(categorie=categorie)

    # Agents ne voient que leurs dossiers
    if request.user.is_agent:
        qs = qs.filter(Q(responsable=request.user) | Q(cree_par=request.user))

    paginator = Paginator(qs, 15)
    page = paginator.get_page(request.GET.get('page'))

    from .models import StatutDossier, PrioriteDossier, CategorieDossier
    context = {
        'page_obj': page,
        'q': q, 'statut': statut, 'priorite': priorite, 'categorie': categorie,
        'statuts': StatutDossier.choices,
        'priorites': PrioriteDossier.choices,
        'categories': CategorieDossier.choices,
    }
    return render(request, 'dossiers/dossier_list.html', context)


@login_required
def dossier_detail(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk)

    # Vérif accès agent
    if request.user.is_agent and dossier.responsable != request.user and dossier.cree_par != request.user:
        messages.error(request, "Accès refusé.")
        return redirect('dossiers:list')

    comment_form = CommentaireForm()
    pj_form = PieceJointeForm()

    if request.method == 'POST':
        if 'commentaire' in request.POST:
            comment_form = CommentaireForm(request.POST)
            if comment_form.is_valid():
                c = comment_form.save(commit=False)
                c.dossier = dossier
                c.auteur = request.user
                c.save()
                log_action(request.user, 'ADD_COMMENT', f"Commentaire sur {dossier.reference}")
                messages.success(request, "Commentaire ajouté.")
                return redirect('dossiers:detail', pk=pk)
        elif 'piece_jointe' in request.POST:
            pj_form = PieceJointeForm(request.POST, request.FILES)
            if pj_form.is_valid():
                pj = pj_form.save(commit=False)
                pj.dossier = dossier
                pj.uploade_par = request.user
                pj.save()
                log_action(request.user, 'ADD_FILE', f"Fichier ajouté à {dossier.reference}")
                messages.success(request, "Fichier ajouté.")
                return redirect('dossiers:detail', pk=pk)

    log_action(request.user, 'VIEW_DOSSIER', f"Consultation de {dossier.reference}")
    return render(request, 'dossiers/dossier_detail.html', {
        'dossier': dossier,
        'comment_form': comment_form,
        'pj_form': pj_form,
    })


@login_required
def dossier_create(request):
    if request.method == 'POST':
        form = DossierForm(request.POST, user=request.user)
        if form.is_valid():
            dossier = form.save(commit=False)
            dossier.cree_par = request.user
            dossier.save()
            log_action(request.user, 'CREATE_DOSSIER', f"Création de {dossier.reference}")
            messages.success(request, f"Dossier {dossier.reference} créé.")
            return redirect('dossiers:detail', pk=dossier.pk)
    else:
        form = DossierForm(user=request.user)
    return render(request, 'dossiers/dossier_form.html', {'form': form, 'action': 'Créer'})


@login_required
def dossier_update(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk)
    if request.user.is_agent and dossier.cree_par != request.user:
        messages.error(request, "Accès refusé.")
        return redirect('dossiers:list')
    if request.method == 'POST':
        form = DossierForm(request.POST, instance=dossier, user=request.user)
        if form.is_valid():
            form.save()
            log_action(request.user, 'UPDATE_DOSSIER', f"Modification de {dossier.reference}")
            messages.success(request, "Dossier mis à jour.")
            return redirect('dossiers:detail', pk=pk)
    else:
        form = DossierForm(instance=dossier, user=request.user)
    return render(request, 'dossiers/dossier_form.html', {'form': form, 'action': 'Modifier', 'dossier': dossier})


@login_required
@require_manager
def dossier_delete(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk)
    if request.method == 'POST':
        ref = dossier.reference
        dossier.delete()
        log_action(request.user, 'DELETE_DOSSIER', f"Suppression de {ref}")
        messages.success(request, f"Dossier {ref} supprimé.")
        return redirect('dossiers:list')
    return render(request, 'dossiers/dossier_confirm_delete.html', {'dossier': dossier})


# ── Clients ───────────────────────────────────────────────────

@login_required
def client_list(request):
    q = request.GET.get('q', '')
    clients = Client.objects.all()
    if q:
        clients = clients.filter(nom__icontains=q)
    paginator = Paginator(clients, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dossiers/client_list.html', {'page_obj': page, 'q': q})


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            log_action(request.user, 'CREATE_CLIENT', f"Création client {client.nom}")
            messages.success(request, "Client créé.")
            return redirect('dossiers:client_list')
    else:
        form = ClientForm()
    return render(request, 'dossiers/client_form.html', {'form': form, 'action': 'Créer'})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            log_action(request.user, 'UPDATE_CLIENT', f"Modification client {client.nom}")
            messages.success(request, "Client mis à jour.")
            return redirect('dossiers:client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'dossiers/client_form.html', {'form': form, 'action': 'Modifier'})
