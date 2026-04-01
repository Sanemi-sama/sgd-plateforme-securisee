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
            name='ActionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('action', models.CharField(
                    choices=[
                        ('LOGIN','Connexion'),('LOGOUT','Déconnexion'),
                        ('CREATE_USER','Création utilisateur'),('UPDATE_USER','Modification utilisateur'),
                        ('DELETE_USER','Suppression utilisateur'),('UPDATE_PROFILE','Mise à jour profil'),
                        ('CHANGE_PASSWORD','Changement mot de passe'),
                        ('CREATE_DOSSIER','Création dossier'),('VIEW_DOSSIER','Consultation dossier'),
                        ('UPDATE_DOSSIER','Modification dossier'),('DELETE_DOSSIER','Suppression dossier'),
                        ('CREATE_CLIENT','Création client'),('UPDATE_CLIENT','Modification client'),
                        ('ADD_COMMENT','Ajout commentaire'),('ADD_FILE','Ajout fichier'),
                        ('ACCESS_DENIED','Accès refusé'),('OTHER','Autre'),
                    ],
                    max_length=30,
                )),
                ('description', models.TextField(blank=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('path', models.CharField(blank=True, max_length=500)),
                ('method', models.CharField(blank=True, max_length=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='audit_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': "Journal d'action",
                'verbose_name_plural': "Journal des actions",
                'ordering': ['-timestamp'],
            },
        ),
    ]
