# -*- coding: utf-8 -*-

"""Entite_parcelle.

Contient la classe Entite_parcelle.
"""


class EntiteParcelle():
    """Entité présente sur une parcelle.

    Attributes
    ----------
    parcelle : Parcelle
        Parcelle d'appartenance de l'entité. Doit être défini avant que la
        simulation ne commence réellement.
    potager : Potager
        Potager d'appartenance de l'entité. Est défini à partir de la parcelle
        d'appartenance de l'entité.
    age : int = 0
        Temps écoulé en pas depuis la création de l'entité.
        A pour valeur maximum le pas actuel du potager.

    Methods
    -------
        pas(self) -> None:
            Augmente le pas de l'entité.
    """

    def __init__(self) -> None:
        """Constructeur de l'entité de parcelle.

        Returns
        -------
        None.

        """
        self._parcelle = None
        self._age = 0

    @property
    def parcelle(self):
        """Attribute parcelle getter."""
        return self._parcelle

    @parcelle.setter
    def parcelle(self, parcelle) -> None:
        """Définit la parcelle d'appartenance de l'entité.

        parcelle doit être instance de Parcelle.
        """
        if True:
            self._parcelle = parcelle
        else:
            raise TypeError("parcelle doit être instance de Parcelle")

    @property
    def potager(self):
        """Attribute potager getter. Récupéré depuis la parcelle."""
        return self.parcelle.potager

    @property
    def age(self) -> int:
        """Attribute age getter."""
        return self._age

    def pas(self) -> None:
        """Augmente le pas de l'entité."""
        self._age += 1
