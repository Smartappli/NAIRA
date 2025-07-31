"""
Commande Django pour migrer les mots de passe existants vers Argon2
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from auth.backends import Argon2Backend
from django.contrib.auth.hashers import check_password
import getpass

class Command(BaseCommand):
    help = 'Migre les mots de passe existants vers Argon2'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nom d\'utilisateur spécifique à migrer',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Migrer tous les utilisateurs',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simuler la migration sans faire de changements',
        )

    def handle(self, *args, **options):
        if options['username']:
            # Migrer un utilisateur spécifique
            try:
                user = User.objects.get(username=options['username'])
                self.migrate_user(user, options['dry_run'])
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Utilisateur "{options["username"]}" non trouvé')
                )
        elif options['all']:
            # Migrer tous les utilisateurs
            users = User.objects.all()
            self.stdout.write(f'Migration de {users.count()} utilisateurs...')
            
            for user in users:
                self.migrate_user(user, options['dry_run'])
                
            self.stdout.write(
                self.style.SUCCESS('Migration terminée !')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    'Veuillez spécifier --username <nom> ou --all pour migrer les utilisateurs'
                )
            )

    def migrate_user(self, user, dry_run=False):
        """Migre un utilisateur spécifique"""
        self.stdout.write(f'Migration de l\'utilisateur: {user.username}')
        
        # Vérifier si le mot de passe est déjà en Argon2
        if user.password.startswith('$argon2'):
            self.stdout.write(
                self.style.WARNING(f'  - {user.username}: Mot de passe déjà en Argon2')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'  - {user.username}: Sera migré (simulation)')
            )
            return
        
        # Demander le mot de passe actuel
        password = getpass.getpass(f'Mot de passe pour {user.username}: ')
        
        # Vérifier le mot de passe actuel
        if not check_password(password, user.password):
            self.stdout.write(
                self.style.ERROR(f'  - {user.username}: Mot de passe incorrect')
            )
            return
        
        # Hasher avec Argon2
        new_hash = Argon2Backend.hash_password(password)
        user.password = new_hash
        user.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'  - {user.username}: Migré avec succès')
        ) 