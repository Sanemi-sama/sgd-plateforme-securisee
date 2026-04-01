from django.db import models
from django.conf import settings


class StatutDossier(models.TextChoices):
    OUVERT = 'ouvert', 'Ouvert'
    EN_COURS = 'en_cours', 'En cours'
    SUSPENDU = 'suspendu', 'Suspendu'
    CLOS = 'clos', 'Clôturé'
    ARCHIVE = 'archive', 'Archivé'


class PrioriteDossier(models.TextChoices):
    BASSE = 'basse', 'Basse'
    NORMALE = 'normale', 'Normale'
    HAUTE = 'haute', 'Haute'
    CRITIQUE = 'critique', 'Critique'


class CategorieDossier(models.TextChoices):
    COMMERCIAL = 'commercial', 'Commercial'
    JURIDIQUE = 'juridique', 'Juridique'
    TECHNIQUE = 'technique', 'Technique'
    INCIDENT = 'incident', 'Incident de sécurité'
    AUTRE = 'autre', 'Autre'


class Client(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom / Raison sociale")
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Dossier(models.Model):
    reference = models.CharField(max_length=30, unique=True, verbose_name="Référence")
    titre = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(blank=True)
    client = models.ForeignKey(
        Client, on_delete=models.PROTECT,
        related_name='dossiers', verbose_name="Client"
    )
    categorie = models.CharField(
        max_length=20, choices=CategorieDossier.choices,
        default=CategorieDossier.AUTRE
    )
    statut = models.CharField(
        max_length=20, choices=StatutDossier.choices,
        default=StatutDossier.OUVERT
    )
    priorite = models.CharField(
        max_length=10, choices=PrioriteDossier.choices,
        default=PrioriteDossier.NORMALE
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='dossiers_responsable',
        verbose_name="Responsable"
    )
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='dossiers_crees',
        verbose_name="Créé par"
    )
    date_echeance = models.DateField(null=True, blank=True, verbose_name="Échéance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dossier"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.reference}] {self.titre}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self._generate_reference()
        super().save(*args, **kwargs)

    def _generate_reference(self):
        from django.utils import timezone
        year = timezone.now().year
        last = Dossier.objects.filter(reference__startswith=f'DOS-{year}-').count()
        return f'DOS-{year}-{last + 1:04d}'

    @property
    def statut_badge_class(self):
        mapping = {
            'ouvert': 'badge-success',
            'en_cours': 'badge-info',
            'suspendu': 'badge-warning',
            'clos': 'badge-secondary',
            'archive': 'badge-dark',
        }
        return mapping.get(self.statut, 'badge-secondary')

    @property
    def priorite_badge_class(self):
        mapping = {
            'basse': 'badge-secondary',
            'normale': 'badge-info',
            'haute': 'badge-warning',
            'critique': 'badge-danger',
        }
        return mapping.get(self.priorite, 'badge-secondary')


class PiecesJointes(models.Model):
    dossier = models.ForeignKey(
        Dossier, on_delete=models.CASCADE, related_name='pieces_jointes'
    )
    fichier = models.FileField(upload_to='dossiers/pieces_jointes/')
    nom = models.CharField(max_length=255)
    uploade_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


class Commentaire(models.Model):
    dossier = models.ForeignKey(
        Dossier, on_delete=models.CASCADE, related_name='commentaires'
    )
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    contenu = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Commentaire de {self.auteur} sur {self.dossier}"
