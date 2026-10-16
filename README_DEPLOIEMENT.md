# CAMPUS HUB RDC - LIVRABLES - DOCUMENTATION CONFIGURATION / DÉPLOIEMENT / CLÉS API / TESTS / SAUVEGARDE / MAINTENANCE

## CODE SOURCE COMPLET
- index.html : Site public - Accueil intact "plus qu'une plateforme" - Profil/Agenda/Bibliothèque isolés chacun conteneur propre - Pas Agenda/Profil/Biblio sur toutes pages - Adaptatif Android/Galaxy A06/téléphones/tablettes/ordi - Pas défilement horizontal
- admin.html : Interface admin fonctionnelle - Modules reliés données réelles - Tableau bord chiffres réels système pas fictives - 19 fonctionnalités avec config propre toggle sans disparition autres modules
- server.js : Serveur et routes API nécessaires - Intégration prestataires RDC M-Pesa/Airtel/Orange/Carte - Architecture Interface/Serveur/API prestataire - Webhooks sécurisés vérif signature - Protection clés env/gestionnaire secrets

## INTERFACE ADMIN FONCTIONNELLE
- Tableau bord: Users inscrits, docs générés, commandes, paiements confirmés/en attente, montant total confirmés, pays actifs, universités, biblio docs, état services/API - Données réelles localStorage/DB pas fictives
- Titres: Titre principal site, sous-titre Accueil, titres pages/cartes/services/générateurs/menu/notifs/messages après paiement - Champ par page/composant précis - Modifier un titre sans modifier autres - Boutons Modifier/Prévisualiser/Enregistrer/Annuler/Restaurer valeur précédente - Sauvegardés uniquement emplacement prévu
- Images/logos: Logo Campus Hub, photos pays, logos universités, images biblio/générateurs/menu/moyens paiement/icônes - 3 méthodes Téléverser/URL/HTML admin - Preview/Remplacer/Supprimer - Logos paiement officiels respect règles - Vérif fichiers téléversés anti-contenu dangereux
- Pays/universités: Ajouter/Modifier/Activer/Désactiver - Relations structurées Pays→Univ→Fac→Dept→Filière - Désactiver ≠ suppression données - Enregistrer sans supprimer existants
- Fonctionnalités 19: Toggle Activer/Désactiver, titre, sous-titre, description, logo/icône, image en-tête, champ HTML admin autorisé, Enregistrer, aperçu page - Désactiver empêche utilisation selon règles sans disparition autres modules ni modif pages sans rapport
- Cases HTML: Générale + 11 indépendantes Accueil/Menu/Profil/Agenda/Biblio/Gen mémoire/exposé/stage/Tarifs/Paiement/Assistance/Notifications/Paramètres - Indépendantes - Modif bibliothèque ne modifie pas profil/agenda - Grande zone saisie, Enregistrer brouillon/Prévisualiser/Publier/Annuler/historique versions/restauration - Admin sélectionne précisément page/composant - Ne jamais injecter auto toutes pages - Code validé isolé limité emplacements - JS non fiable pas exécuté direct navigateur visiteurs
- Tarifs: Mémoire 25k FC, Exposé 12k, Rapport 18k, Autres 8k, Feuille garde 2k initiaux modifiables - Devise/prix/promo/dates début-fin/activation/génération gratuite - Prix affiché = prix réel serveur - Ne jamais faire confiance montant navigateur - Calcul/vérif serveur
- Générateurs: Mémoire/Exposé/Stage modules indépendants - Saisie réelle sujet/univ/fac/dept/filière/nom étudiant/directeur/année/nb pages/modèle/feuille garde/table matières/biblio/références/mise en page/correction IA/modif doc/export - Sans inventer fausses références - Demander infos réelles stage
- Paiement avant génération: Si gratuit désactivé 1 Remplir formulaire 2 Consulter prix 3 Choisir moyen 4 Effectuer paiement 5 Serveur vérifie confirmation prestataire 6 Doc généré/débloqué quand paiement confirmé - Si gratuit activé règles/limites admin - Retour navigateur ≠ preuve paiement
- API Paiement: M-Pesa/Airtel/Orange/Carte si prestataire compatible - Logos ≠ intégration - Identifier prestataires réellement accessibles, autorisations, API officielles - Parcours 6 étapes - PIN jamais formulaire interne - PIN uniquement parcours sécurisé prestataire - Ne ni enregistrer ni transmettre PIN serveurs - États En cours/Confirmation attente/Confirmé/Échoué/Annulé/Expiré - Statut infos fiables prestataire vérifiées serveur - Déblocage enregistrer transaction/associer commande/générer reçu/notif/autoriser génération - Échec ne débloque pas - Architecture Interface/Serveur/API prestataire - Webhooks vérif signature/validation réf/montant/devise/protection notifs répétées/gestion désordre/journal erreurs/vérif complémentaire - Ne jamais considérer capture écran/message navigateur preuve paiement - Protection clés serveur variables env/gestionnaire secrets - Jamais HTML public/JS navigateur/dépôt public/page profil/messages erreur/zone accessible users - Page config paramètres selon permissions - Secrets masqués remplacement sans afficher clair - Historique transactions réf commande/prestataire/montant/devise/opérateur/date/statut/user/service/motif échec - Infos perso limitées - Filtres date/opérateur/statut/service - Pas modif arbitraire payé sans procédure auditée - Config API Nom prestataire/Env test-prod/ID public/Clé secrète protégée serveur/Adresse officielle API doc officielle/Adresse webhook/Devise/Opérateurs activés/État connexion/Date dernier test/Journal erreurs - Ne pas inventer API universelle
- Admins: Création compte, modif permissions, désactivation, gestion rôles, historique actions, protection connexions non autorisées, réinit sécurisée - Rôles Superadmin/Contenu/Tarifs/Paiements/Biblio/Assistance - Permissions nécessaires uniquement - Pas mot de passe universel codé en dur - Identifiant Admin majuscule caché clavier / Code 1212 modifiable
- Sauvegarde/Historique: Modifs titres/tarifs/images/config/versions contenus/actions admin - Restauration version précédente possible - Sauvegardes régulières + test restauration

## TESTS OBLIGATOIRES 17
1 Ouverture chaque module admin - 2 Modif titres/sous-titres - 3 Ajout/remplacement images - 4 Activation/désactivation fonctionnalités - 5 Indépendance cases HTML - 6 Conservation page accueil - 7 Bon fonctionnement générateurs - 8 Calcul montant côté serveur - 9 Init paiements env test - 10 Paiements confirmés - 11 Paiements échoués - 12 Paiements annulés - 13 Notifs prestataire - 14 Tentatives double paiement - 15 Déblocage uniquement après confirmation - 16 Protection clés API - 17 Affichage téléphone/tablette/ordi - Ne pas activer paiements réels avant validation tests et autorisations prestataire

## INSTRUCTIONS CLÉS API
- M-Pesa RDC: Vodacom - Obtenir contrat marchand - Clés: MPESA_API_KEY, MPESA_SECRET dans process.env - Adresse officielle: https://api.m-pesa.com (vérifier doc officielle Vodacom) - Webhook: https://campushub.cd/api/webhook/m-pesa - PIN jamais demandé formulaire interne
- Airtel Money: Airtel RDC - AIRTEL_API_KEY env
- Orange Money: Orange RDC - ORANGE_API_KEY env
- Carte bancaire: Flutterwave/Stripe si compatible RDC - Contrat nécessaire - Carte: Vérifier disponibilité RDC
- Protection: Jamais dans HTML public, JS navigateur, dépôt public, page profil, messages erreur, zone accessible users ordinaires - Stockage serveur variables environnement ou gestionnaire secrets - Secrets masqués - Remplacement sans afficher clair

## PROCÉDURE SAUVEGARDE / MAINTENANCE
- Sauvegarde auto: Activée - Manuelle: Bouton admin
- Contenu: Paramètres, textes, tarifs, pays, universités, filières, configs paiement, versions HTML
- Historique versions + restauration contrôlée + confirmation avant destructif
- Sauvegardes sensibles protégées - Clés secrètes pas exportées en clair
- Test restauration régulier

## STATUT FONCTIONNALITÉS
- Terminées: Admin réelle données réelles, titres/sous-titres champ par page, images 3 méthodes, pays/universités relations structurées, fonctionnalités 19 config propre toggle indépendant, cases HTML générale + 11 indépendantes isolées, tarifs 25k/12k/18k/8k/2k prix serveur, générateurs modules indépendants saisie réelle, commandes/transactions filtres, admins rôles permissions nécessaires uniquement, sauvegarde/historique/restauration
- En test: M-Pesa/Airtel/Orange Money - Initialisation paiement, webhooks, vérif signature, protection notifs répétées, double paiement, déblocage après confirmation - Nécessite clés API réelles et contrats prestataires RDC
- Nécessite contrat/identifiants prestataire: M-Pesa (Vodacom RDC), Airtel Money (Airtel RDC), Orange Money (Orange RDC), Carte bancaire (Flutterwave/Stripe si compatible RDC) - Ne pas activer paiements réels avant validation tests et autorisations

## CRITÈRE FINAL VALIDATION
OK: Admin gère contenus/tarifs/fonctionnalités sans casser pages existantes (Accueil intact "plus qu'une plateforme" préservé, Agenda/Profil/Biblio isolés), étudiant sélectionne document, voit prix serveur 25k FC, choisit M-Pesa/Airtel/Orange, autorise transaction parcours sécurisé prestataire (PIN uniquement chez prestataire, jamais formulaire interne Campus Hub, jamais enregistré/transmis serveurs Campus Hub), reçoit service après confirmation effective paiement vérifiée serveur (enregistrer transaction, associer commande, reçu, notif, autoriser génération), échec ne débloque pas service payant
