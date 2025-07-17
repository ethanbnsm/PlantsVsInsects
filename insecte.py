# -*- coding: utf-8 -*-

"""Insecte.

Contient la classe Insecte.
"""
# Import from builtins
from math import inf
from random import random, randint, choice, normalvariate
# Import interne
from entite_parcelle import EntiteParcelle


GENES = ["_pv_max", "_esperance_vie", "_mobilite", "_resistance",
         "_tps_entre_repro", "_portee_max"]
NB_GENES = len(GENES)
PROBA_MUTATION = 0.05

POURCENTAGE_SANTE_FAIBLE = 0.2
POURCENTAGE_PV_ENFANT = 0.5
NB_REPAS_AFFAME = 3


class Insecte(EntiteParcelle):
    """Insecte vivant sur une parcelle."""

    def __init__(self, espece: str, sexe: bool,
                 pv_max: int, esperance_vie: int,
                 mobilite: float, resistance: float,
                 tps_entre_repro: int, portee_max: int,
                 enfant: bool = False) -> None:
        super().__init__()

        # Définition de l'espèce
        try:
            self._espece = str(espece)
        except ValueError as exc:
            raise TypeError("espece doit être un str") from exc

        # Définition du sexe
        try:
            self._sexe = bool(sexe)  # True = Homme , False = Femme
        except ValueError as exc:
            raise TypeError("sexe doit être un booléen.") from exc

        # Définition des points de vie maximum
        try:
            self._pv_max = int(pv_max)
        except ValueError as exc:
            raise TypeError("pv_max doit être un entier.") \
                from exc
        if self._pv_max <= 0:
            raise ValueError("pv_max doit être supérieur à 0.")

        # Définition de l'espérance de vie
        try:
            self._esperance_vie = int(esperance_vie)
        except ValueError as exc:
            raise TypeError("esperance_vie doit être un entier.") \
                from exc
        if self._esperance_vie <= 0:
            raise ValueError("esperance_vie doit être supérieur à 0.")

        # Définition de la mobilité
        try:
            self._mobilite = float(mobilite)
        except ValueError as exc:
            raise TypeError("mobilite doit être un flottant"
                            + " entre 0 et 1.") from exc
        if self._mobilite < 0 or self._mobilite > 1:
            raise ValueError("mobilite doit être"
                             + "compris entre 0 et 1.")

        # Définition de la résistance
        try:
            self._resistance = float(resistance)
        except ValueError as exc:
            raise TypeError("resistance doit être un flottant"
                            + " entre 0 et 1.") from exc
        if self._resistance < 0 or self._resistance > 1:
            raise ValueError("resistance doit être"
                             + "compris entre 0 et 1.")

        # Définition du temps entre 2 reproductions
        try:
            self._tps_entre_repro = int(tps_entre_repro)
        except ValueError as exc:
            raise TypeError("tps_entre_repro doit être un entier.") \
                from exc
        if self._tps_entre_repro < 0:
            raise ValueError("tps_entre_repro doit être supérieur"
                             + " ou égal à 0.")

        # Définition de la taille de portée maximum
        try:
            self._portee_max = int(portee_max)
        except ValueError as exc:
            raise TypeError("portee_max doit être un entier.") \
                from exc
        if self._portee_max < 0:
            raise ValueError("portee_max doit être supérieur"
                             + " ou égal à 0.")

        # Définition des valeurs d'historique
        self._derniere_repro = inf
        self._dernier_repas = inf
        self._repas_consecutifs = 0

        if enfant:  # Cas où l'insecte est généré par reproduction
            self._maturite = self._tps_entre_repro * 2
            self._pv = max(1, int(self._pv_max * POURCENTAGE_PV_ENFANT))
        else:  # Cas d'un insecté créé adulte (ou présent au premier pas)
            self._maturite = 0
            self._pv = self._pv_max

    # Getters des attributs

    @property
    def espece(self):
        """Attribute espece getter."""
        return self._espece

    @property
    def portee_max(self):
        """Attribute portee_max getter."""
        return self._portee_max

    @property
    def sexe(self):
        """Attribute sexe getter."""
        return self._sexe

    def survivre(self) -> bool:
        """Détermine si l'insecte meurt à ce tour. SI oui, le tue.

        L'insecte meurt SI:
            Il n'a plus de points de vie;
            OU Il n'arrive pas à résister (défini par sa résistance)
               à l'insecticide sur la parcelle si il y en a;
            OU Son espérance de vie est écoulée;
        """
        mort = False
        if self._pv <= 0:
            if self.potager.loglevel >= 2:
                print(f"{self} ✝ faim")
            mort = True
        try:
            if self._parcelle.insecticide > 0:  # Insecticide présent
                if random() > self._resistance:
                    if self.potager.loglevel >= 2:
                        print(f"{self} ✝ insecticide")
                    mort = True
        except AttributeError as exc:
            raise UnboundLocalError("La parcelle doit être définie pour"
                                    + " l'insecte.") from exc
        if self.age > self._esperance_vie:
            if self.potager.loglevel >= 2:
                print(f"{self} ✝ age")
            mort = True
        if mort:
            self.parcelle._insectes.remove(self)

    def se_nourrir(self) -> bool:
        """Gestion du nourrisage de l'insecte.

        SI il y a une plante sur la parcelle, l'insecte se nourrit.
            Il gagne un PV SI l'insecte se nourrit
            pour au moins la 3ème fois consécutive.
        SINON (l'insecte n'a pas pu se nourrir), il perd un point de vie.

        Renvoie Vrai si l'insecte a pu se nourrir. Faux sinon.
        """
        try:
            if len(self._parcelle.plantes) > 0:  # Au moins une plante
                # L'insecte se nourrit
                self._dernier_repas = 0
                self._repas_consecutifs += 1
                if self._repas_consecutifs >= 3:
                    # L'insecte gagne un PV (jusqu'à ses PV max)
                    self._pv = min(self._pv + 1, self._pv_max)
                return True
            # Sinon, l'insecte mange son seum
            self._dernier_repas += 1
            self._repas_consecutifs = 0
            self._pv = max(self._pv - 1, 0)
            return False
        except AttributeError as exc:
            raise UnboundLocalError("La parcelle doit être définie pour"
                                    + " l'insecte.") from exc

    @property
    def disponible(self) -> bool:
        """Renvoie Vrai si l'insecte est disponible, Faux sinon.

        L'insecte est disponible SI il ne s'est pas reproduit trop
        récemment ET SI il est adulte.
        """
        return (self._derniere_repro > self._tps_entre_repro
                and self.age >= self._maturite and self._dernier_repas < 3)

    def partenaires(self) -> list:
        """Renvoie la liste des partenaires valides pour l'insecte."""
        # Vérification qu'il y a d'autres insectes sur la parcelle
        try:
            return [i for i
                    in self._parcelle.insectes
                    if (i.disponible and i.sexe != self.sexe
                        and i.espece == self.espece)]
        except AttributeError:
            return []

    @staticmethod
    def mutation(gene) -> (float, int):
        """Renvoie le gène mutée par la loi de probabilité."""
        return normalvariate(gene, 0.05)

    def reproduire(self):
        """Reproduction de l'insecte.

        Un insecte peut se reproduire SI il est lui-même disponible
        sexuellement, mature, ET SI un autre insecte sur la parcelle est
        dans le même cas ET compatible (espèce identique ET sexe différent)
        SINON, renvoie None.
        """
        self._derniere_repro += 1
        if not self.disponible:  # L'insecte n'est pas disponible
            if self.potager.loglevel >= 2:
                print(f"{self} 🟥")
            return []
        partenaires = self.partenaires()
        if partenaires == []:  # Pas de partenaire trouvé
            if self.potager.loglevel >= 2:
                print(f"{self} 💦")
            return []
        # On en choisit un au hasard
        partenaire = choice(partenaires)
        # Génération aléatoire de la taille de la portée
        t_portee = randint(1, partenaire.portee_max)
        parents_dict = (self.__dict__, partenaire.__dict__)

        self._derniere_repro, partenaire._derniere_repro = 0, 0
        portee = []
        for _ in range(t_portee):
            # Choix des gènes de chaque enfant de la portée
            ind = [0]*NB_GENES  # Liste des choix d'héritage des gènes
            while ind in ([0]*NB_GENES, [1]*NB_GENES):
                ind = [randint(0, 1) for i in range(NB_GENES)]
            # Dictionnaire contenant les caractéristiques
            # de l'enfant qui va naître
            enf = {}
            for i, gene in enumerate(GENES):
                enf[gene] = parents_dict[ind[i]][gene]
            # Mutation
            if random() < PROBA_MUTATION:
                # On choisit un des gènes à muter
                gene_mute = choice(GENES)
                # On mute le gène selon la loi de probabilité de mutation()
                enf[gene_mute] = self.mutation(enf[gene_mute])
            enf["sexe"] = bool(randint(0, 1))
            # Normalisation des valeurs
            enf["_pv_max"] = int(max(1, enf["_pv_max"]))
            enf["_esperance_vie"] = int(max(1, enf["_esperance_vie"]))
            enf["_mobilite"] = float(min(1, max(0, enf["_mobilite"])))
            enf["_resistance"] = float(min(1, max(0, enf["_resistance"])))
            enf["_tps_entre_repro"] = int(max(0, enf["_tps_entre_repro"]))
            enf["_portee_max"] = int(max(0, enf["_portee_max"]))
            # Création de l'insecte
            portee.append(Insecte(self.espece, enf["sexe"], enf["_pv_max"],
                          enf["_esperance_vie"], enf["_mobilite"],
                          enf["_resistance"], enf["_tps_entre_repro"],
                          enf["_portee_max"], True))
        if self.potager.loglevel >= 1:
            print(f"{self} ♥ {t_portee}")
        return portee

    def bouger(self) -> bool:
        """Mouvement de l'insecte.

        L'insecte bouge selon une probabilité dépendant de:
            *sa mobilité;
            *sa faim;
            *sa santé.
        Renvoie Vrai si l'insecte bouge.
        """
        proba_mobilite = self._mobilite
        if self._dernier_repas >= NB_REPAS_AFFAME:  # L'insecte est affamé
            proba_mobilite *= 2
        if self._pv < (self._pv_max * POURCENTAGE_SANTE_FAIBLE):
            # L'insecte a une santé faible
            proba_mobilite /= 2
        if random() < proba_mobilite:  # L'insecte essaie de bouger
            try:
                voisin = self.parcelle.voisinerandom()
                if voisin is None:  # Pas de parcelle voisine
                    return False
                if self.potager.loglevel >= 3:
                    print(f"{self} → {voisin}")
                voisin.accueillir(self)
            except AttributeError as exc:
                raise UnboundLocalError("La parcelle doit être définie"
                                        + "pour l'insecte.") from exc
            return True
        return False

    def __repr__(self) -> str:
        return f"{self.parcelle} {self.espece} {self.age}{'♂' if self.sexe else '♀'}"