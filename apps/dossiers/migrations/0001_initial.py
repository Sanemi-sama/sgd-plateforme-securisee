from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=200, verbose_name='Nom / Raison sociale')),
                ('email', models.EmailField(blank=True)),
                ('telephone', models.CharField(blank=True, max_length=20)),
                ('adresse', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Client', 'ordering': ['nom']},
        ),
        migrations.CreateModel(
            name='Dossier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('reference', models.CharField(max_length=30, unique=True, verbose_name='Référence')),
                ('titre', models.CharField(max_length=255, verbose_name='Titre')),
                ('description', models.TextField(blank=True)),
                ('categorie', models.CharField(
                    choices=[('commercial','Commercial'),('juridique','Juridique'),('technique','Technique'),('incident','Incident de sécurité'),('autre','Autre')],
                    default='autre', max_length=20,
                )),
                ('statut', models.CharField(
                    choices=[('ouvert','Ouvert'),('en_cours','En cours'),('suspendu','Suspendu'),('clos','Clôturé'),('archive','Archivé')],
                    default='ouvert', max_length=20,
                )),
                ('priorite', models.CharField(
                    choices=[('basse','Basse'),('normale','Normale'),('haute','Haute'),('critique','Critique')],
                    default='normale', max_length=10,
                )),
                ('date_echeance', models.DateField(blank=True, null=True, verbose_name='Échéance')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dossiers', to='dossiers.client', verbose_name='Client')),
                ('cree_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dossiers_crees', to=settings.AUTH_USER_MODEL, verbose_name='Créé par')),
                ('responsable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dossiers_responsable', to=settings.AUTH_USER_MODEL, verbose_name='Responsable')),
            ],
            options={'verbose_name': 'Dossier', 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Commentaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('contenu', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('dossier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commentaires', to='dossiers.dossier')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='PiecesJointes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('fichier', models.FileField(upload_to='dossiers/pieces_jointes/')),
                ('nom', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('dossier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pieces_jointes', to='dossiers.dossier')),
                ('uploade_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
