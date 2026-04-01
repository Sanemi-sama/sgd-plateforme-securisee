"""
Commande : python manage.py init_data
Crée le superuser admin + données de démonstration.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.dossiers.models import Client, Dossier
from apps.users.models import Role

User = get_user_model()


class Command(BaseCommand):
    help = "Initialise les données de démonstration (admin + clients + dossiers)"

    def handle(self, *args, **options):
        self.stdout.write("⚙️  Initialisation des données...")

        # ── Superuser admin ──────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@sgd.local',
                password='Admin1234!',
                first_name='Super',
                last_name='Admin',
                role=Role.ADMIN,
                department='Direction',
            )
            self.stdout.write(self.style.SUCCESS("✅ Superuser 'admin' créé (mot de passe: Admin1234!)"))
        else:
            self.stdout.write("ℹ️  Superuser 'admin' déjà existant.")

        # ── Utilisateurs de démonstration ────────────
        demo_users = [
            dict(username='manager1', email='manager@sgd.local', password='Manager1234!',
                 first_name='Marie', last_name='Dupont', role=Role.MANAGER, department='Sécurité'),
            dict(username='agent1', email='agent@sgd.local', password='Agent1234!',
                 first_name='Jean', last_name='Martin', role=Role.AGENT, department='Opérations'),
            dict(username='auditeur1', email='audit@sgd.local', password='Audit1234!',
                 first_name='Paul', last_name='Bernard', role=Role.AUDITEUR, department='Audit'),
        ]
        for u in demo_users:
            if not User.objects.filter(username=u['username']).exists():
                pwd = u.pop('password')
                user = User(**u)
                user.set_password(pwd)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Utilisateur '{user.username}' créé"))

        # ── Clients ───────────────────────────────────
        clients_data = [
            {'nom': 'Acme Corporation', 'email': 'contact@acme.bj', 'telephone': '+229 21 00 00 01'},
            {'nom': 'BenTech Solutions', 'email': 'info@bentech.bj', 'telephone': '+229 21 00 00 02'},
            {'nom': 'Ministère du Numérique', 'email': 'contact@min-num.gouv.bj', 'telephone': '+229 21 00 00 03'},
        ]
        clients = []
        for cd in clients_data:
            c, created = Client.objects.get_or_create(nom=cd['nom'], defaults=cd)
            clients.append(c)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Client '{c.nom}' créé"))

        # ── Dossiers de démonstration ─────────────────
        admin_user = User.objects.get(username='admin')
        manager = User.objects.filter(role=Role.MANAGER).first()

        dossiers_data = [
            {'titre': 'Audit sécurité infrastructure réseau', 'client': clients[2],
             'categorie': 'technique', 'statut': 'en_cours', 'priorite': 'haute',
             'description': "Audit complet de l'infrastructure réseau du ministère suite à une tentative d'intrusion détectée."},
            {'titre': 'Mise en conformité RGPD', 'client': clients[0],
             'categorie': 'juridique', 'statut': 'ouvert', 'priorite': 'normale',
             'description': "Accompagnement pour la mise en conformité avec le RGPD et les réglementations locales."},
            {'titre': 'Incident de sécurité — Phishing', 'client': clients[1],
             'categorie': 'incident', 'statut': 'ouvert', 'priorite': 'critique',
             'description': "Campagne de phishing ciblant les employés. Analyse forensique en cours."},
        ]
        for dd in dossiers_data:
            if not Dossier.objects.filter(titre=dd['titre']).exists():
                Dossier.objects.create(**dd, cree_par=admin_user, responsable=manager)
                self.stdout.write(self.style.SUCCESS(f"✅ Dossier '{dd['titre']}' créé"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Initialisation terminée !"))
        self.stdout.write("   → http://localhost:8000/")
        self.stdout.write("   → admin / Admin1234!")
        self.stdout.write("   → manager1 / Manager1234!")
        self.stdout.write("   → agent1 / Agent1234!")
