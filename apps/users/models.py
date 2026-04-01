from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = 'admin', 'Administrateur'
    MANAGER = 'manager', 'Manager'
    AGENT = 'agent', 'Agent'
    AUDITEUR = 'auditeur', 'Auditeur'


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.AGENT,
        verbose_name="Rôle"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    department = models.CharField(max_length=100, blank=True, verbose_name="Département")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    # ── Helpers de rôle ───────────────────────
    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_manager(self):
        return self.role in (Role.ADMIN, Role.MANAGER)

    @property
    def is_agent(self):
        return self.role == Role.AGENT

    @property
    def is_auditeur(self):
        return self.role == Role.AUDITEUR

    @property
    def role_badge_class(self):
        mapping = {
            Role.ADMIN: 'badge-danger',
            Role.MANAGER: 'badge-warning',
            Role.AGENT: 'badge-info',
            Role.AUDITEUR: 'badge-secondary',
        }
        return mapping.get(self.role, 'badge-secondary')
