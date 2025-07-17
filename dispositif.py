# -*- coding: utf-8 -*-

"""Dispositif.

Contient la classe Dispositif.
"""
from entite_parcelle import EntiteParcelle

LISTE_PRODUITS = ["eau", "engrais", "insecticide"]


class Dispositif(EntiteParcelle):
    """Dispositif d'arrosage ou de dispersion d'intrants.

    Attributes
    ----------
        debut_programme : int > 0
            Pas où le programme  démarré (1 est le premier pas).
        duree_activation : int >= 0
            Durée en pas où le programme est actif à partir
            du début de chaque période d'activation.
            Si vaut 0 : Le programme ne fonctionne jamais.
        periode_activation : int > 0 et >= duree_activation
            Période en pas pour l'activation du système.
            Si vaut 1 : Le programme fonctionne en continu sauf si
            duree_activation vaut 0, alors le programme ne fonctionne pas.
        portee : int >= 0
            Rayon d'action en distance de Manhattan du dispositif.
        eau : bool = False
            Vrai si le dispositif diffuse de l'eau.
        engrais : bool = False
            Vrai si le dispositif diffuse de l'engrais.
        insecticide : bool = False
            Vrai si le dispositif diffuse de l'insecticide.

    Methods
    -------
    actif(self) -> bool:
        Renvoie un booléen indiquant si le dispositif est activé à ce pas.
    definir_programme(self, debut_programme: int, duree_activation: int,
                      periode_activation: int, eau: bool = False,
                      engrais: bool = False,
                      insecticide: bool = False) -> None:
        Redéfinit le programme du dispositif.
    """

    def __init__(self,
                 portee: int,
                 programmes: list = []) -> None:
        """Constructeur de la classe Dispositif.

        Parameters
        ----------
        portee : int >= 0
            Rayon d'action en distance de Manhattan du dispositif.
        eau : bool = False, optional
            Vrai si le dispositif diffuse de l'eau.
        engrais : bool = False, optional
            Vrai si le dispositif diffuse de l'engrais.
        insecticide : bool = False, optional
            Vrai si le dispositif diffuse de l'insecticide.

        Raises
        ------
        TypeError
            Les paramètres ne respectent pas les types demandés.
        ValueError
            Les paramètres ne respectent pas les conditions demandées.

        Returns
        -------
        None.

        """
        super().__init__()

        self._eau = False
        self._engrais = False
        self._insecticide = False

        self._programmes = []
        if not isinstance(programmes, list):
            raise TypeError("programmes doit être une liste.")
        for ele in programmes:
            try:
                self.ajouter_programme(ele)
            except TypeError:
                raise Exception("Un des programmes rentré est invalide.")

        # Définition de la portée (pas de setter)
        try:
            self._portee = int(portee)
        except ValueError as exc:
            raise TypeError("portee doit être un entier.") \
                from exc
        if self._portee <= 0:
            raise ValueError("portee doit être supérieur à 0")

    # Getter de portee (car non programmable)

    @property
    def portee(self):
        """Attribute portee getter."""
        return self._portee

    # Setters et getters des intrants.

    @property
    def eau(self):
        """Attribute eau getter."""
        return self._eau

    @property
    def engrais(self):
        """Attribute engrais getter."""
        return self._engrais

    @property
    def insecticide(self):
        """Attribute insecticide getter."""
        return self._insecticide

    def ajout_prog(self, prog) -> None:
        """Ajoute un programme à la liste de programmes du dispositif."""
        if isinstance(prog, Programme):
            self._programmes.append(prog)
            if prog.produit == "eau":
                self._eau = True
            if prog.produit == "engrais":
                self._engrais = True
            if prog.produit == "insecticide":
                self._insecticide = True
        else:
            raise TypeError("Le paramètre n'est pas un programme valide.")

    # Méthodes pour la simulation
    @property
    def actif(self) -> set:
        """Renvoie le set des produits dispersés à ce pas.

        La liste des produits dispersés à ce pas est établie pour tous les
        programmes du dispositif. Si un programme est actif, alors son produit
        est dispersé ce pas-ci.
        """
        return set([prog.produit
                    for prog in self._programmes
                    if prog.actif(self.age)])


class Programme():
    def __init__(self, produit: str, debut: int,
                 duree: int, periode: int) -> None:
        """Constructeur de la classe Programme.

        Parameters
        ----------
        produit: str in LISTE_PRODUITS
        debut: int >= 0
            Pas où le programme démarre (0 est le premier pas).
        duree: int >= 0
            Durée en pas où le programme est actif à partir
            du début de chaque période d'activation.
            Si vaut 0 : Le programme ne fonctionne jamais.
        periode: int > 0 et >= duree
            Période en pas pour l'activation du système.
            Si vaut 1 : Le programme fonctionne en continu sauf si
            duree vaut 0, alors le programme ne fonctionne pas.
        """
        if produit not in LISTE_PRODUITS:
            raise TypeError("""produit doit être un
                            élément de la liste :""", LISTE_PRODUITS)
        self._produit = produit
        try:
            self.debut = debut
            self.duree = duree
            self.periode = periode
        except (ValueError, TypeError) as exc:
            raise exc

    @property
    def debut(self):
        """Attribute debut getter."""
        return self._debut

    @debut.setter
    def debut(self, debut):
        """Attribute debut setter."""
        try:
            self._debut = int(debut)
        except ValueError as exc:
            raise TypeError("debut doit être un entier.") \
                from exc
        if self._debut < 0:
            raise ValueError("debut doit être supérieur"
                             + " ou égal à 0.")

    @property
    def duree(self):
        """Attribute duree getter."""
        return self._duree

    @duree.setter
    def duree(self, duree):
        """Attribute duree setter."""
        try:
            self._duree = int(duree)
        except ValueError as exc:
            raise TypeError("duree doit être un entier.") \
                from exc
        if self._duree < 0:
            raise ValueError("duree doit être supérieur"
                             + " ou égal à 0.")

    @property
    def periode(self):
        """Attribute periode getter."""
        return self._periode

    @periode.setter
    def periode(self, periode):
        """Attribute periode setter."""
        try:
            self._periode = int(periode)
        except ValueError as exc:
            raise TypeError("periode doit être un entier.") \
                from exc
        if self._periode <= 0 \
                or self._periode < self.duree:
            raise ValueError("periode doit être"
                             + " supérieur ou égal à 0 et au moins aussi"
                             + " grand que la durée d'activation.")

    @property
    def produit(self):
        """Attribute produit getter."""
        return self._produit

    def actif(self, age: int) -> bool:
        """Renvoie Vrai si le programme est actif au pas spécifié.

        L'activation du programme est établie en fonction de:
            -Le pas actuel et le pas debut
            -La période d'activation et la durée d'activation
        """
        return (age >= self.debut  # Programme démarré
                and ((age - self.debut) % self.periode) < (self.duree))


if __name__ == "__main__":
    from tests import tests_dispositif, tests_programme

    print("""=== Test de la classe Dispositif ===""")
    tests_dispositif("test").run()
    print("""=== Test de la classe Programme ===""")
    tests_programme("test").run()
