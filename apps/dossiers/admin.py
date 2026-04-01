from django.contrib import admin
from .models import Client, Dossier, Commentaire, PiecesJointes

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'telephone', 'created_at')
    search_fields = ('nom', 'email')

@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('reference', 'titre', 'client', 'statut', 'priorite', 'responsable', 'created_at')
    list_filter = ('statut', 'priorite', 'categorie')
    search_fields = ('reference', 'titre', 'client__nom')
    readonly_fields = ('reference', 'created_at', 'updated_at')

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('dossier', 'auteur', 'created_at')

@admin.register(PiecesJointes)
class PiecesJointesAdmin(admin.ModelAdmin):
    list_display = ('nom', 'dossier', 'uploade_par', 'created_at')
