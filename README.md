# jourtempo

Couleur Tempo EDF d'aujourd'hui et de demain, jours EJP et jours de pointe PP, en Python, **sans clé ni compte**.
Les données viennent de l'API gratuite de [Jour Tempo](https://jourtempo.fr/api/) (couleurs RTE, calendrier EJP d'EDF,
signaux PP de RTE).

```bash
pip install jourtempo
```

```python
import jourtempo

jourtempo.couleur_aujourdhui()     # 'bleu', 'blanc' ou 'rouge'
jourtempo.couleur_demain()         # idem, ou 'inconnu' avant l'annonce de RTE (vers 10 h 30)
jourtempo.jours_restants("rouge")  # jours rouges restants dans la saison
jourtempo.ejp_demain()             # True, False, ou None si pas encore publié / hors saison
jourtempo.pp_demain()              # jour de pointe PP demain ?
jourtempo.tempo()                  # réponse complète (calendrier de la saison, compteurs…)
print(jourtempo.attribution())     # mention de source à afficher
```

- Aucune dépendance (bibliothèque standard seulement), Python 3.9 et plus.
- Les réponses restent en mémoire jusqu'à l'heure `perime_apres` donnée par l'API : la couleur ne change qu'une fois
  par jour, inutile d'interroger plus souvent.
- Le jour Tempo va de 6 h à 6 h : avant 6 h, « aujourd'hui » reste la couleur de la veille, comme sur la facture.

**Réutilisation des données** : gratuite, à condition de citer la source (champ `attribution` de chaque réponse).
Tous les champs sont décrits sur [jourtempo.fr/api](https://jourtempo.fr/api/).

## English

Python client for the free, keyless [Jour Tempo API](https://jourtempo.fr/api/#english): French EDF Tempo tariff colour
for today and tomorrow (RTE open data), EJP and PP peak days. `pip install jourtempo`, then
`jourtempo.couleur_demain()`. No dependencies. Credit the source when you reuse the data.

Licence du code : MIT.
