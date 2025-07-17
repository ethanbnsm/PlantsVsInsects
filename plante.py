    # -*- coding: utf-8 -*-

"""Plante.

Contient la classe Plante et sa classe héritée Drageon.
"""
from random import random, choice
import logging
from entite_parcelle import EntiteParcelle

class Plante(EntiteParcelle):
    """Plante d'une parcelle.

    Attributes
    ----------
        espece : str
            Espèce de la plante

        _tps_maturation : int >= 0
            Âge minimum de la plante pour donner des fruits.
        _nb_recoltes_potentielles : int >= 0
            Nombre maximum de récoltes données par la plante.
        _tps_entre_recoltes : int >= 0
            Nombre de pas entre deux récoltes pour une plante mature.

        _humidite : (0 <= int <= 1, 0 <= int <= 1)
            Humidités minimum et maximum pour le développement de la plante.
        surface_parcelle : 0.2 <= float <= 1
            Fraction de la parcelle que prend la plante.

        _tps_sous_insecticide : int = 0
            Durée en pas depuis sa création pour laquelle la plante a été
            en présence d'insecticide.
        _nb_recoltes_effectuees: int = 0
            Nombre de récoltes effectuées sur la plante. La plante ne
            produit plus si ce nombre atteint nb_recoltes_potentielles.
        _tps_croissance : int = 0
            Nombre de pas pendant lequel le fruit s'est développé. Le fruit
            est récolté lorsque ce développement atteint tps_entre_recoltes.


    Methods
    -------
        update_developpement(self) -> float
            Gère le développement de la plante.
        update_fruits(self) -> bool
            Récolte les fruits si il y en a et les ajoute à la récolte.
    """

    def __init__(self,
                 espece: str,
                 tps_maturation: int,
                 nb_recoltes_potentielles: int,
                 tps_entre_recoltes: int,
                 humidite: (int, int),
                 surface_parcelle: float):
        """Constructeur de la classe Plante.

        Parameters
        ----------
        espece : str
            Espèce de la plante
        tps_maturation : int >= 0
            Âge minimum de la plante pour donner des fruits.
        nb_recoltes_potentielles : int >= 0
            Nombre maximum de récoltes données par la plante.
        tps_entre_recoltes : int >= 0
            Nombre de pas entre deux récoltes pour une plante mature.
        humidite : (0 <= int <= 1, 0 <= int <= 1)
            Humidités minimum et maximum pour le développement de la plante.
        surface_parcelle : 0.2 <= float <= 1
            Fraction de la parcelle que prend la plante.

        Returns
        -------
        None.

        """

        super().__init__()

        # Définition de l'espèce
        try:
            self._espece = str(espece)
        except ValueError as exc:
            raise TypeError("espece doit être un str") from exc

        # Définition du temps de maturation
        try:
            self._tps_maturation = int(tps_maturation)
        except ValueError as exc:
            raise TypeError("tps_maturation doit être un entier.") \
                from exc
        if self._tps_maturation < 0:
            raise ValueError("tps_maturation doit être supérieur"
                             + " ou égal à 0.")

        # Définition du nombre de récoltes potentielles
        try:
            self._nb_recoltes_potentielles = int(nb_recoltes_potentielles)
        except ValueError as exc:
            raise TypeError("nb_recoltes_potentielles doit être un entier.") \
                from exc
        if self._nb_recoltes_potentielles < 0:
            raise ValueError("nb_recoltes_potentielles doit être supérieur"
                             + " ou égal à 0.")

        # Définition du temps entre 2 récoltes
        try:
            self._tps_entre_recoltes = int(tps_entre_recoltes)
        except ValueError as exc:
            raise TypeError("tps_entre_recoltes doit être un entier.") \
                from exc
        if self._tps_entre_recoltes < 0:
            raise ValueError("tps_entre_recoltes doit être supérieur"
                             + " ou égal à 0.")

        # Définition de l'humidité
        try:
            self._humidite = (float(humidite[0]), float(humidite[1]))
        except (ValueError, IndexError, TypeError) as exc:
            raise ValueError("humidite est un trouple de 2"
                             + " flottants entre 0 et 1.") from exc
        if self._humidite[0] > 1 or self._humidite[0] < 0:
            raise ValueError("humidite[0] doit être compris entre 0 et 1.")
        if self._humidite[1] > 1 or self._humidite[1] < 0:
            raise ValueError("humidite[1] doit être compris entre 0 et 1.")

        # Définition de la surface au sol
        try:
            self._surface_parcelle = float(surface_parcelle)
        except ValueError as exc:
            raise TypeError("surface_parcelle doit être un flottant"
                            + " entre 0.2 et 1.") from exc
        if self._surface_parcelle < 0.2 or self._surface_parcelle > 1:
            raise ValueError("surface_parcelle doit être"
                             + "compris entre 0.2 et 1.")

        self._tps_sous_insecticide = 0
        self._tps_croissance = 0
        self._nb_recoltes_effectuees = 0

    # Getters des attributs

    @property
    def espece(self) -> str:
        """Attribute espece getter."""
        return self._espece

    @property
    def surface_parcelle(self) -> str:
        """Attribute surface_parcelle getter."""
        return self._surface_parcelle
    def update_developpement(self) -> float:
        """Effectue un pas de développement de la plante.

        Calcule la valeur de développement à partir des attributs de la
        parcelle, et la renvoie. self._parcelle doit être une
        parcelle valide, sinon la fonction renvoie UnboundLocalError.
        """
        try:
            # Présence d'un insecte
            p_insecte = (len(self._parcelle.insectes) != 0)
            # Humidité correcte
            hum_ok = (self._parcelle.humidite >= self._humidite[0]
                      and self._parcelle.humidite <= self._humidite[1])
            # Présence d'engrais
            p_engrais = (self._parcelle.engrais > 0)
            dev = max(0, (1 + 1*p_engrais) * (1 + 1*hum_ok - 1*p_insecte))
            self._age += dev
            if self.mature:
                self._tps_croissance += dev
            if self.potager.loglevel >=3:
                print(f'{self.parcelle} {self.espece} : {dev}')
            return dev
        except AttributeError as exc:
            raise UnboundLocalError("La parcelle doit être définie pour"
                                    + " la plante.") from exc

    @property
    def mature(self) -> bool:
        """Renvoie Vrai si la plante est mature, Faux sinon.

        La plante est mature si son âge est supérieure ou égale à
        son temps de maturation.
        """
        return self.age >= self._tps_maturation

    @property
    def productive(self) -> bool:
        """Renvoie Vrai si la plante est productive, Faux sinon.

        La plante est productive SI elle est mature (self.mature) ET
        SI son nombre de récoltes faites n'a pas atteint le nombre de
        récoltes maximum de la plante.
        """
        return (self.mature
                and (self._nb_recoltes_effectuees
                     < self._nb_recoltes_potentielles))

    def update_fruits(self) -> bool:
        """Développe et récolte les fruits et les ajoute à la récolte.

        Executé à chaque pas de simulation. Augmente le développement des
        fruits si l'arbre est productif et les récolte si ils sont mûrs.
        Si un fruit est récolté, incrémente self._nb_recoltes_effectuees.
        Renvoie Vrai si un fruit a été récolté ce pas-ci.
        """
        # Condition de maturité, de productivité et de fruit mûr
        if ((self.mature and self.productive) and
                self._tps_croissance >= self._tps_entre_recoltes):
            # On récolte
            if self.potager.loglevel >= 2:
                print(f'{self.parcelle} {self.espece} ♣ {self._tps_sous_insecticide}')
            self._tps_croissance = 0  # On réinitialise la croissance du fruit
            self._nb_recoltes_effectuees += 1
            fruit = (self._espece, self._tps_sous_insecticide)
            self.parcelle.potager.ajouter_recolte(fruit)
            return True
        return False
    def pas(self) -> None:
        """Override la fonction de pas de la classe Entite_parcelle.

        Les plantes ne grandissent pas à la même vitesse
        que le temps qui passe.
        """
        if self.parcelle.insecticide:
            self._tps_sous_insecticide += 1


class Drageon(Plante):
    """Comme les plantes, mais en mieux.

    Attributes
    ----------
        proba_colonisation : 0 <= float <= 1
            Probabilité que la plante drageonnante tente de
            conquérir les parcelles voisines.


    Methods
    -------
        coloniser(self) -> bool
            Gère le développement de la plante.
    """

    def __init__(self,
                 espece: str,
                 tps_maturation: int,
                 nb_recoltes_potentielles: int,
                 tps_entre_recoltes: int,
                 humidite: (int, int),
                 surface_parcelle: float,
                 proba_colonisation: float):
        """Constructeur de la classe Drageon.

        Parameters
        ----------
        espece : str
            Espèce de la plante
        tps_maturation : int >= 0
            Âge minimum de la plante pour donner des fruits.
        nb_recoltes_potentielles : int >= 0
            Nombre maximum de récoltes données par la plante.
        tps_entre_recoltes : int >= 0
            Nombre de pas entre deux récoltes pour une plante mature.
        humidite : (0 <= int <= 1, 0 <= int <= 1)
            Humidités minimum et maximum pour le développement de la plante.
        surface_parcelle : 0.2 <= float <= 1
            Fraction de la parcelle que prend la plante.
        proba_colonisation : 0 <= float <= 1
            Probabilité que la plante drageonnante tente de
            conquérir les parcelles voisines.

        Returns
        -------
        None.

        """
        # Constructeur de la classe parente Plante
        super().__init__(espece, tps_maturation, nb_recoltes_potentielles,
                         tps_entre_recoltes, humidite, surface_parcelle)
        # Définition de la probabilité de colonisation du drageon
        try:
            self._proba_colonisation = float(proba_colonisation)
        except ValueError as exc:
            raise TypeError("proba_colonisation doit être un flottant"
                            + " entre 0 et 1.") from exc
        if self._proba_colonisation < 0 or self._proba_colonisation > 1:
            raise ValueError("proba_colonisation doit être"
                             + "compris entre 0 et 1.")

    def coloniser(self) -> bool:
        """Gère le développement de la plante par drageonnement.

        Renvoie Vrai si la plante a drageonné.
        """
        if not self.mature:  # La plante doit être adulte pour drageonner
            return False
        # La plante peut drageonner avec une certaine probabilité
        if random() > self._proba_colonisation:
            return False
        try:
            parcelles_voisines = self.parcelle.voisines()
        except AttributeError as exc:
            raise UnboundLocalError("La parcelle doit être définie pour"
                                    + " la plante.") from exc
        parcelles_colonisables = []
        # On cherche une parcelle colonisable
        for parcelle in parcelles_voisines:
            surface_occupee = 0
            for plante in parcelle._plantes:
                # On compte la surface totale prise par les plantes
                # de la parcelle
                surface_occupee += plante._surface_parcelle
            # Il faut assez d'espace sur la parcelle à coloniser pour
            # que le drageon s'y rajoute
            if 1 - surface_occupee > self._surface_parcelle:
                parcelles_colonisables.append(parcelle)
        if not parcelles_colonisables:
            return False
        # Toutes les conditions requises sont réunies : On choisit une parcelle
        colonie = choice(parcelles_colonisables)
        # On plante le drageon
        colonie.planter(Drageon(self._espece,
                                self._tps_maturation,
                                self._nb_recoltes_potentielles,
                                self._tps_entre_recoltes,
                                self._humidite,
                                self._surface_parcelle,
                                self._proba_colonisation))
        if self.potager.loglevel >=1:
            print(f"{self.parcelle} {self.espece} → {colonie}")
        return True
