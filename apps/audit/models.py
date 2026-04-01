from django.db import models
from django.conf import settings


class ActionLog(models.Model):
    ACTIONS = [
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('CREATE_USER', 'Création utilisateur'),
        ('UPDATE_USER', 'Modification utilisateur'),
        ('DELETE_USER', 'Suppression utilisateur'),
        ('UPDATE_PROFILE', 'Mise à jour profil'),
        ('CHANGE_PASSWORD', 'Changement mot de passe'),
        ('CREATE_DOSSIER', 'Création dossier'),
        ('VIEW_DOSSIER', 'Consultation dossier'),
        ('UPDATE_DOSSIER', 'Modification dossier'),
        ('DELETE_DOSSIER', 'Suppression dossier'),
        ('CREATE_CLIENT', 'Création client'),
        ('UPDATE_CLIENT', 'Modification client'),
        ('ADD_COMMENT', 'Ajout commentaire'),
        ('ADD_FILE', 'Ajout fichier'),
        ('ACCESS_DENIED', 'Accès refusé'),
        ('OTHER', 'Autre'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_logs'
    )
    action = models.CharField(max_length=30, choices=ACTIONS)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    path = models.CharField(max_length=500, blank=True)
    method = models.CharField(max_length=10, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Journal d'action"
        verbose_name_plural = "Journal des actions"
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user} — {self.get_action_display()}"
