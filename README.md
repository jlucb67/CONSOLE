# CONSOLE - la console d'administration du systeme d'agents specialises

## REGLE ABSOLUE
Ce depot est PUBLIC. Il ne porte QUE le code de la page.
Aucun document, aucun resume, aucune donnee d'agent, AUCUNE CLE n'y entre jamais.

## Ce que c'est
Une page unique (`index.html`), publiee par GitHub Pages : https://jlucb67.github.io/CONSOLE/
A l'ouverture, elle demande sa cle a JL (memorisee ensuite dans son navigateur), lit les depots
prives SOCLE, GENERAL et LFI par l'interface de GitHub, et construit l'affichage dans le navigateur.
Sans cle, l'adresse ne montre qu'une coquille sans donnees.

## Trois ecrans
1. Tunnel d'acquisition des connaissances - le tableau des documents (zones, tags, statuts, resumes,
   parcours Zone 1-2-3, decision en lot). Format canonique : P20 du manuel de l'Admin.
2. Gestion des agents - fraicheur de la memoire vive de chaque agent (savoir/VERSION.md).
3. Supervision de la veille - une ligne par veille active, age de sa derniere entree, ecarts.

## Regles de conception
- Le depot est la verite ; la console n'est qu'une vue. Elle lit l'etat REEL au moment de l'ouverture.
- Les decisions passent par une demande GitHub (P22) que le robot de promotion traite.
- Si l'envoi direct est impossible (affichage sans connexion sortante, cle absente), la page fabrique
  la commande a coller a l'Agent Admin, qui execute par le connecteur.
- Source versionnee du plan : SOCLE/ADMIN/instructions/CONSOLE_PLAN.md
