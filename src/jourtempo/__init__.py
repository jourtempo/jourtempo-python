"""Client Python de l'API gratuite de Jour Tempo (https://jourtempo.fr/api/).

Couleur Tempo d'aujourd'hui et de demain (données RTE), jours EJP (calendrier EDF) et jours de pointe PP (RTE),
sans clé ni compte. Les réponses sont gardées en mémoire jusqu'à l'heure ``perime_apres`` donnée par l'API :
inutile d'interroger plus souvent.

Exemple ::

    import jourtempo
    jourtempo.couleur_demain()        # 'bleu', 'blanc', 'rouge' ou 'inconnu' avant l'annonce de RTE
    jourtempo.jours_restants("rouge")  # jours rouges restants dans la saison
    jourtempo.ejp_demain()            # True, False ou None (pas encore publié)

Condition d'utilisation des données : citer la source (champ ``attribution`` de chaque réponse).
"""
from __future__ import annotations

import datetime as _dt
import json as _json
import threading as _threading
import urllib.request as _urlreq

__version__ = "0.1.0"
__all__ = ["tempo", "ejp", "pp", "couleur_aujourdhui", "couleur_demain", "jours_restants", "ejp_aujourdhui",
           "ejp_demain", "pp_demain", "attribution", "BASE_URL"]

BASE_URL = "https://jourtempo.fr/api/v1/"
_UA = f"jourtempo-python/{__version__} (+https://jourtempo.fr/api/)"
_cache: dict[str, tuple[dict, _dt.datetime | None]] = {}
_verrou = _threading.Lock()


def _maintenant() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _lire(fichier: str, rafraichir: bool = False, delai: float = 15.0) -> dict:
    """Lit ``fichier`` (tempo.json, ejp.json, pp.json), en mémoire jusqu'à ``perime_apres``."""
    with _verrou:
        if not rafraichir and fichier in _cache:
            donnees, perime = _cache[fichier]
            if perime is None or _maintenant() < perime:
                return donnees
    req = _urlreq.Request(BASE_URL + fichier, headers={"User-Agent": _UA, "Accept": "application/json"})
    with _urlreq.urlopen(req, timeout=delai) as reponse:
        donnees = _json.loads(reponse.read().decode("utf-8"))
    perime = None
    if donnees.get("perime_apres"):
        try:
            perime = _dt.datetime.fromisoformat(donnees["perime_apres"])
        except ValueError:
            perime = None
    with _verrou:
        _cache[fichier] = (donnees, perime)
    return donnees


def tempo(rafraichir: bool = False) -> dict:
    """Réponse complète de ``tempo.json`` (aujourd'hui, demain, saison, calendrier)."""
    return _lire("tempo.json", rafraichir)


def ejp(rafraichir: bool = False) -> dict:
    """Réponse complète de ``ejp.json`` (aujourd'hui, demain, saison, jours EJP)."""
    return _lire("ejp.json", rafraichir)


def pp(rafraichir: bool = False) -> dict:
    """Réponse complète de ``pp.json`` (jours de pointe PP du mécanisme de capacité, RTE)."""
    return _lire("pp.json", rafraichir)


def couleur_aujourdhui() -> str:
    """Couleur Tempo du jour : 'bleu', 'blanc' ou 'rouge'."""
    return tempo()["aujourdhui"]["code"]


def couleur_demain() -> str:
    """Couleur Tempo de demain : 'bleu', 'blanc', 'rouge', ou 'inconnu' avant l'annonce de RTE."""
    return tempo()["demain"]["code"]


def jours_restants(couleur: str = "rouge") -> int:
    """Jours restants de ``couleur`` ('bleu', 'blanc' ou 'rouge') dans la saison Tempo en cours."""
    return int(tempo()["saison"]["compteurs"][couleur]["restants"])


def _ejp_jour(jour: str) -> bool | None:
    code = ejp()[jour].get("code")
    return {"ejp": True, "normal": False}.get(code)


def ejp_aujourdhui() -> bool | None:
    """True si aujourd'hui est un jour EJP, False sinon, None hors saison ou si non publié."""
    return _ejp_jour("aujourdhui")


def ejp_demain() -> bool | None:
    """True si demain est un jour EJP, False sinon, None hors saison ou pas encore publié par EDF."""
    return _ejp_jour("demain")


def pp_demain() -> bool | None:
    """True si demain est un jour de pointe PP, False sinon, None si pas encore publié ou hors période."""
    code = pp()["demain"].get("code")
    return {"pp": True, "non-pp": False, "non-eligible": False}.get(code)


def attribution(fichier: str = "tempo.json") -> str:
    """Mention de source à afficher avec les données (condition de réutilisation)."""
    return _lire(fichier)["attribution"]
