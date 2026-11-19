"""Tests hors ligne : on remplace l'appel réseau par des réponses d'exemple."""
import datetime as dt
import json
import unittest
from unittest import mock

import jourtempo

DEMAIN = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=1)).isoformat()
TEMPO = {"attribution": "Source : RTE ; via Jour Tempo", "perime_apres": DEMAIN,
         "aujourdhui": {"code": "bleu"}, "demain": {"code": "rouge"},
         "saison": {"compteurs": {"rouge": {"quota": 22, "tombes": 1, "restants": 21},
                                  "blanc": {"quota": 43, "tombes": 1, "restants": 42},
                                  "bleu": {"quota": 300, "tombes": 79, "restants": 221}}}}
EJP = {"attribution": "Source : EDF ; via Jour Tempo", "perime_apres": DEMAIN,
       "aujourdhui": {"code": "normal"}, "demain": {"code": "ejp"}}
PP = {"attribution": "Source : RTE ; via Jour Tempo", "perime_apres": DEMAIN,
      "aujourdhui": {"code": "non-pp"}, "demain": {"code": "attente"}}


class FausseReponse:
    def __init__(self, donnees):
        self._d = json.dumps(donnees).encode()

    def read(self):
        return self._d

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def faux_urlopen(req, timeout=0):
    url = req.full_url
    return FausseReponse(TEMPO if url.endswith("tempo.json") else EJP if url.endswith("ejp.json") else PP)


class Tests(unittest.TestCase):
    def setUp(self):
        jourtempo._cache.clear()

    @mock.patch("urllib.request.urlopen", side_effect=faux_urlopen)
    def test_couleurs_et_compteurs(self, appel):
        self.assertEqual(jourtempo.couleur_aujourdhui(), "bleu")
        self.assertEqual(jourtempo.couleur_demain(), "rouge")
        self.assertEqual(jourtempo.jours_restants("rouge"), 21)
        self.assertEqual(appel.call_count, 1)  # mis en mémoire jusqu'à perime_apres

    @mock.patch("urllib.request.urlopen", side_effect=faux_urlopen)
    def test_ejp_pp(self, appel):
        self.assertIs(jourtempo.ejp_aujourdhui(), False)
        self.assertIs(jourtempo.ejp_demain(), True)
        self.assertIs(jourtempo.pp_demain(), None)
        self.assertIn("Jour Tempo", jourtempo.attribution("pp.json"))

    @mock.patch("urllib.request.urlopen", side_effect=faux_urlopen)
    def test_perime_relit(self, appel):
        jourtempo.tempo()
        jourtempo._cache["tempo.json"] = (TEMPO, dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=1))
        jourtempo.tempo()
        self.assertEqual(appel.call_count, 2)


if __name__ == "__main__":
    unittest.main()
