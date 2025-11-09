# BF6 Stats Bot 🎮

Un **bot Discord** qui génère des **bannières personnalisées** avec les statistiques des joueurs de **Battlefield 6**.  
Il récupère les stats via l’API [GameTools](https://api.gametools.network/) et crée une image esthétique avec les informations clés.

---

## Fonctionnalités

- Génération de **bannière avec fond, logo et frosted glass** derrière les stats.  
- Affichage des statistiques principales :
  - K/D, Kills, Deaths, Wins, Loses  
  - Accuracy, Classe préférée, Revives, Kill Assists  
  - Time Played  
- Support pour **plusieurs plateformes** :
  - `pc`, `xboxone`, `ps4`, `xboxseries`, `ps5`, `xbox`, `psn`  
- Commande simple sur Discord :  
`!bf6stats <pseudo> [plateforme]`
- Génération d’image directement en mémoire (**BytesIO**) sans créer de fichier temporaire.

---

## Prérequis

- Python 3.10+  
- Bibliothèques Python :
```bash
pip install discord.py pillow requests
```

- Images nécessaires dans le dossier du bot :
  - bannerBackgroundImage.webp → fond de la bannière
  - logo_bf6.webp → logo du jeu (optionnel) 
- Polices TrueType (optionnel, Windows par défaut utilisées si non présentes) :
  - segoeui.ttf, arial.ttf, Tahoma.ttf

3. Le bot répond avec la **bannière générée** directement dans le chat.

---

## Personnalisation

- Modifier le fond : remplace `bannerBackgroundImage.webp`.  
- Modifier le logo : remplace `logo_bf6.webp`.  
- Changer les polices : dans `bot.py`, modifier la fonction `load_font` pour utiliser vos `.ttf`.  
- Ajuster les couleurs ou la taille des textes directement dans le script.

---

## Contributions

Les contributions sont les bienvenues !  
- Fork le dépôt  
- Crée une branche pour tes modifications  
- Ouvre une Pull Request  

---

## Licence

Ce projet est sous licence MIT.  
Vous êtes libre de l’utiliser et de le modifier, mais n’oubliez pas de créditer l’auteur original.

---

**Made with ❤️ for Battlefield 6**
"""



