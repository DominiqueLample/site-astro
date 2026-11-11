# ✦ SHO·astro — ciel profond en palette SHO

Site statique en français : galerie d'astrophotos avec commentaires astrophysiques,
et explications sur la palette SHO, la naissance des photons, le filtrage en bande
étroite et le voyage des photons dans l'espace.

## Lancer le site

Ouvrez simplement `index.html` dans un navigateur, ou servez le dossier :

```
python3 -m http.server 8000
# puis http://localhost:8000
```

Aucune dépendance externe : HTML + CSS + JS purs.

## Structure

- `index.html` — page unique (galerie, SHO, photons, filtrage, voyage)
- `css/style.css` — thème sombre spatial
- `js/main.js` — galerie rendue depuis le tableau `PHOTOS`, lightbox, champ d'étoiles, spectre interactif
- `assets/` — images (démo : générées procéduralement en SHO)
- `tools/generate_images.py` — régénère les images de démo (`python3 tools/generate_images.py`)

## Utiliser vos propres photos

1. Déposez vos fichiers (JPG) dans `assets/`.
2. Dans `js/main.js`, modifiez le tableau `PHOTOS` : `src`, `alt`, `title`, `meta`, `comment`.
