# -*- coding: utf-8 -*-

"""Potager.

Permet de simuler le potager et contient la classe Potager et Parcelle.
"""

from plante import Plante, Drageon
from insecte import Insecte
from dispositif import Dispositif,Programme

from random import choice
from collections import Counter
import os
import xml.etree.ElementTree as ET
import logging as log

HUMIDITE_INIT = 0.5  # Humidité par défaut d'une parcelle
LOG_LEVEL = 1

class Potager():
    """Contient une liste de parcelles et en avance le pas de simulation.

    Attributes
    ----------
    _pas : int >= 0
        Pas en cours de la simulation du potager.

    _nom_fichier : str = None
        Chemin vers le fichier XML contenant la configuration du potager.
        Si défini à None, un potager vide est créé par le constructeur.
    _nom_potager : str = None
        Nom du potager pour l'affichage.
    longueur : int > 0
        Longueur du potager.
    largeur : int > 0
        Largeur du potager.
    nb_iterations : int > 0
        Nombre de pas simulés maximum du potager
    _parcelles : list[[Parcelle]]
        Matrice de taille _longueur*_largeur contenant les parcelles ou None et
        de facto leur emplacement dans le potager.
    _parcelles_1d : list[Parcelle]
        Liste de toutes les parcelles : Version aplatie de _parcelles.

    recolte : list(tuple)
        Liste des fruits récoltés, avec les tuples contenant les informations
        des fruits

    Methods
    -------
    pas(self) -> Bool
        Avance la simulation du potager d'un pas.
    snapshot(self) -> SnapshotPotager
        Renvoie un instantané de l'état du potager pour l'utilisation
        par une interface et le stockage.
    affecter(self, x: int > 0, y: int > 0, portee: int > 0,
             eau = False, engrais = False, insecticide = False)
             -> list[Parcelle]
        Cherche la liste des parcelles affectées par un dispositif situé à
        des coordonnées (x,y) à une certaine portée et y simule la dispersion
        d'engrais, insecticide ou eau.
    ajouter_recolte(self, entree) -> None
        Ajoute un fruit à la récolte.
    _creer_parcelles_vides(self, x: int, y: int, humidite: float)
        Crée une matrice de taille (x,y) de parcelles vides.
    """

    def __init__(self,
                 nom_fichier: str = None,
                 nb_iter: int = 0,
                 longueur: int = 0,
                 largeur: int = 0) -> None:
        """Constructeur de la classe Potager.

        Ce constructeur charge le fichier XML indiqué par nom_fichier. Si
        Parameters
        ----------
        nom_fichier : str
            Chemin vers le fichier XML contenant la configuration du potager.
            Si défini à None (par défaut), un potager vide est créé.
        nb_iter : int >= 0
            Nombre de pas maximum de la simulation, et correspond aussi
            au nombre de pas. Si défini à 0 (par défaut),
            le potager a le nombre d'itérations indiqué par le fichier.
            Cependant, si fichier est None, le constructeur renvoie ValueError.
        longueur : int >= 0
            Longueur du potager en parcelles. Si défini à 0 (par défaut),
            le potager a la longueur indiquée par le fichier
            Cependant, si fichier est None, le constructeur renvoie ValueError.
        largeur : int >= 0
            Largeur du potager en parcelles. Si défini à 0 (par défaut),
            le potager a la largeur indiquée par le fichier.
            Cependant, si fichier est None, le constructeur renvoie ValueError.

        Raises
        ------
        TypeError
            Les paramètres ne respectent pas les types demandés.
        ValueError
            Le pas n'est pas supérieur ou égal à 1.
        OSError
            Le fichier est inaccessible ou introuvable.

        Returns
        -------
        None.

        """
        self._nom_fichier = None
        self._nom_potager = None
        troncXML = None
        if nom_fichier is not None:
            # Si on charge un fichier
            try:
                self._nom_fichier = nom_fichier
                with open(nom_fichier) as fichier:
                    # Chargement du contenu du fichier
                    arbre = ET.parse(nom_fichier)
                troncXML = arbre.getroot()
                # Récupération des principaux paramètres du potager
                self._nom_potager = troncXML.attrib["Nom"]
                if nb_iter == 0:
                    nb_iter = int(troncXML.attrib["Nb_iterations"])
                if longueur == 0:
                    longueur = int(troncXML.attrib["Size_x"])
                if largeur == 0:
                    largeur = int(troncXML.attrib["Size_y"])
            except (ValueError, OSError, ET.ParseError,KeyError) as exc:
                if isinstance(exc, ValueError):
                    raise TypeError from exc
                raise

        try:
            self._nb_iter = int(nb_iter)
        except ValueError as exc:
            raise TypeError(
                """Le nombre d'itérations doit être un
                nombre entier.""") from exc
        else:
            if self._nb_iter < 1:
                raise ValueError(
                    """Le nombre d'itérations doit être un
                    entier positif non nul.""")
            self._pas = 0

        # Définition de la largeur même si nulle
        try:
            self._largeur = int(largeur)
        except ValueError as exc:
            raise TypeError(
                """La longueur doit être un nombre entier.""") from exc
        if self._largeur < 0:
            raise ValueError(
                """La largeur doit être un entier positif non nul.""")

        # Définition de la longueur même si nulle
        try:
            self._longueur = int(longueur)
        except ValueError as exc:
            raise TypeError(
                """La longueur doit être un nombre entier.""") from exc
        if self._longueur <= 0:
            raise ValueError(
                """La longueur doit être un entier positif non nul.""")

        # Création de la matrice de parcelles
        if troncXML is None:
            self._parcelles = self._creer_parcelles_vides(self._longueur,
                                                          self._largeur)
        else:
            self._parcelles = [[None
                                for j in range(self._largeur)]
                               for i in range(self._longueur)]

        # Si fichier chargé
        try:
            if troncXML is not None:
                # Ajout des parcelles et de leurs entités
                for parcelleXML in troncXML.findall("Parcelle"):
                    p_x = int(parcelleXML.attrib['Pos_x'])
                    p_y = int(parcelleXML.attrib['Pos_y'])
                    if p_x >= self._longueur and p_y >= self._largeur:
                        continue  # Hors limites
                    parcelle = Parcelle(self, p_x, p_y)
                    self._parcelles[p_x][p_y] = parcelle
                    # Ajout des dispositifs
                    for d in parcelleXML.findall("Dispositif")[:1]:
                        dispo = Dispositif(d.attrib["Rayon"])
                        parcelle.dispositif = dispo
                        print(f"Dispositif - {parcelle}")
                        # Ajout des programmes
                        for prog in d.findall("Programme"):
                            dispo.ajout_prog(Programme(prog.attrib["Produit"]
                                                       .lower(),
                                                       prog.attrib["Debut"],
                                                       prog.attrib["Duree"],
                                                       prog.attrib["Periode"]))
                            print(f"Programme - {parcelle}")
                    # Ajout des plantes non-drageonnantes
                    for p in parcelleXML.findall("Plante"):
                        parcelle.planter(Plante(p.attrib["Espece"],
                                                p.attrib["Maturite_pied"],
                                     p.attrib["Nb_recolte"],
                                     p.attrib["Maturite_fruit"],
                                     (p.attrib["Humidite_min"],
                                      p.attrib["Humidite_max"]),
                                     p.attrib["Surface"]))
                        print(f"Plante - {parcelle}")
                    # Ajout des plantes drageonnantes
                    for p in parcelleXML.findall("Plante_Drageonnante"):
                        try:
                            parcelle.planter(Drageon(p.attrib["Espece"],
                                             p.attrib["Maturite_pied"],
                                     p.attrib["Nb_recolte"],
                                     p.attrib["Maturite_fruit"],
                                     (p.attrib["Humidite_min"],
                                      p.attrib["Humidite_max"]),
                                     p.attrib["Surface"],
                                     p.attrib["Proba_Colonisation"]))
                            print(f"Drageon - {parcelle}")
                        except:
                            raise ValueError
                    # Ajout des insectes
                    for i in parcelleXML.findall("Insecte"):
                        parcelle.accueillir(Insecte(i.attrib["Espece"],
                                                    True if i.attrib["Sexe"]=="M" else False,
                                                    i.attrib["Vie_max"],
                                                    i.attrib["Duree_vie_max"],
                                                    i.attrib["Proba_mobilite"],
                                                    i.attrib["Resistance_insecticide"],
                                                    i.attrib["Temps_entre_repro"],
                                                    i.attrib["Max_portee"]))
                        print(f"Insecte - {parcelle}")

        except (ValueError, AttributeError, KeyError) as exc:
            raise exc

        # version 1D pour la mise à jour séquentielle
        self._parcelles_1d = [i for j in self._parcelles for i in j if
                              i is not None]
        self.loglevel = LOG_LEVEL
        self._recolte = []

    @property
    def parcelles(self) -> list:
        """Attribute parcelles getter."""
        return self._parcelles

    @parcelles.setter
    def parcelles(self, parcelles) -> None:
        """Attribute parcelles setter."""
        if not isinstance(parcelles, list):
            if parcelles is not None:
                raise TypeError(
                    "parcelles doit être une matrice d'instances de Parcelle.")
        self._longueur = len(parcelles)
        if self._longueur <= 0:
            raise TypeError(
                "parcelles doit être une matrice de dimensions non-nulles.")
        if not isinstance(parcelles[0], list):
            raise TypeError(
                "parcelles doit être une matrice d'instances de Parcelle.")
        self._largeur = len(parcelles[0])
        if self._largeur <= 0:
            raise TypeError(
                "parcelles doit être une matrice de dimensions non-nulles.")
        for rangee in parcelles:
            if not isinstance(rangee, list):
                raise TypeError(
                    "parcelles doit être une matrice d'instances de Parcelle.")
            if len(rangee) != self._largeur:
                raise TypeError(
                    "parcelles doit être une matrice (une liste contenant"
                    "n listes de même taille m).")
            for entree in rangee:  # Pour chaque parcelle du potager
                if entree is not None and not isinstance(entree, Parcelle):
                    raise TypeError(
                        "Chaque élément de parcelles doit être "
                        + "instance de Parcelle ou hérité.")
        self._parcelles = parcelles

    def _creer_parcelles_vides(self, l_x: int, l_y: int,
                               humidite: float = HUMIDITE_INIT) -> list: 
        """Crée une matrice de taille (l_x, l_y) de parcelles vides."""
        return [[Parcelle(self, i, j, humidite)
                for j in range(max(1, l_y))]
                for i in range(max(1, l_x))]

    @property
    def longueur(self) -> int:
        return self._longueur

    @property
    def largeur(self) -> int:
        return self._largeur
    @property
    def recolte(self) -> list:
        """Attribute recolte getter."""
        return self._recolte

    def ajouter_recolte(self, entree) -> None:
        """Ajoute un fruit à la récolte.

        entree doit être un tuple contenant:
            *une chaine de caractères pour l'espèce du fruit;
            *un entier pour le temps sous insecticide.
        """
        try:
            self._recolte.append((str(entree[0]), int(entree[1])))
        except (ValueError, TypeError, IndexError) as exc:
            raise TypeError("Les informations du fruit récolté n'ont pas le"
                            + "format demandé.") from exc

    def recolte_par_especes(self) -> dict:
        recolte_especes = dict()
        for i in self.recolte:
            if i[0] not in recolte_especes.keys():
                recolte_especes[i[0]] = 0
            recolte_especes[i[0]] += 1
        return recolte_especes

    @property
    def nb_insectes(self) -> dict:
        """Obtenir le nombre d'insectes sur le potager de chaque espèce."""
        l_insectes = Counter()
        for i in self._parcelles_1d:
            l_insectes += i.nb_insectes
        return l_insectes

    @property
    def nom_potager(self) -> str:
        """Attribute nom_potager getter."""
        return self._nom_potager

    def pas(self) -> bool:
        """Avance la simulation du potager d'un pas.

        Le pas initial est de 0. Renvoie False si la simulation est terminée,
         donc si le pas maximum est atteint, et True sinon.
        """
        # log.info(f"Pas n°{self._pas}")
        # On exécute pour chaque parcelle dans les fonctions dans l'ordre
        for fonc in (Parcelle.update_plantes, Parcelle.update_insectes,
                         Parcelle.update_dispositif, Parcelle.update_parcelle):
            for i in self._parcelles_1d:
                fonc(i)
        self._pas += 1
        return self._pas < self._nb_iter
        for i in self._parcelles_1d:
            i.update_plantes()
        for i in self._parcelles_1d:
            i.update_insectes()
        for i in self._parcelles_1d:
            i.update_dispositif()
        for i in self._parcelles_1d:
            i.update_parcelle()
        self._pas += 1
        return self._pas < self._nb_iter
        # False si la simulation doit continuer

    def affecter(self, portee: int, parcelle = None,
                 eau=False, engrais=False, insecticide=False,
                 pos_x: int = -1, pos_y: int = -1) -> list:
        """Affecte les parcelles à portée d'une position par les intrants.

        Cherche la liste des parcelles affectées par un dispositif situé sur la
        parcelle spécifiée ou si non indiquée, à la parcelle située
        aux coordonnées (pos_x, pos_ y) à une certaine portée et y simule
        la dispersion d'engrais, insecticide et/ou eau.
        """
        if parcelle is None:
            try:
                parcelle = self.parcelles[pos_x][pos_y]
            except IndexError as exc:
                raise(ValueError, "La position spécifiée est invalide.")
                voisines = []
            else:
                voisines = parcelle.voisines(portee)
        else:
            voisines = parcelle.voisines(portee)
        if voisines:
            #print(voisines)
            pass
        for voisine in voisines:
            # On modifie chaque parcelle en fonction des produits diffusés
            if eau: voisine.arroser()
            if engrais: voisine.mettre_engrais()
            if insecticide: voisine.mettre_insecticide()

    def voisines(self, parcelle, portee: int = 1) -> list:
        """Renvoie la liste des parcelles voisine de la parcelle.

        portee est un entier positif non nul. Il indique la distance de
        Manhattan à parcourir au plus pour chercher les voisins.
        Renvoie [] si la parcelle n'a pas de voisines.
        """
        if portee <= 0:
            raise ValueError("La portée doit être un entier positif non nul.")
        lvoisines = self._voisines(parcelle, portee)
        log.debug(f"Portee = {portee}   L = {len(lvoisines)}")
        if portee > 1:
            # Pour une portée > 1, l'algorithme considère la parcelle comme
            # l'une de ses voisines, on la supprime donc de la liste
            try:
                lvoisines.remove(parcelle)
            except ValueError:
                # Cas qui peut arriver lorsque la parcelle n'a pas de voisines
                pass
        log.debug(f"{parcelle} {lvoisines}")
        return lvoisines

    def _voisines(self, parcelle, portee) -> list :
        voisines = []
        if not portee:
            return parcelle
        x, y = parcelle.pos_x, parcelle.pos_y
        # On ne rajoute la parcelle (vide ou non) que si l'on n'est pas au bord
        if x+1 < self._longueur:
            par = self.parcelles[x+1][y]
            if par is not None:
                voisines.append(par)
        if x != 0:
            par = self.parcelles[x-1][y]
            if par is not None:
                voisines.append(par)
        if y+1 < self._largeur:
            par = self.parcelles[x][y+1]
            if par is not None:
                voisines.append(par)
        if y != 0:
            par = self.parcelles[x][y-1]
            if par is not None:
                voisines.append(par)
        if portee == 1:
            return voisines
        else:
            return list(set(voisines+[i for j in voisines
                                      for i in self._voisines(j,
                                                              portee - 1)]))

    def voisinerandom(self, parcelle, portee: int = 1):
        """Renvoie une parcelle voisine aléatoire de la parcelle.

        Renvoie None si la parcelle n'a pas de parcelle voisine.
        """
        voisines = self.voisines(parcelle, portee)
        if voisines == [None] or not voisines:
            return None
        else:
            return choice(voisines)


DUREE_EFFET_INSECTICIDE = 5  # en pas
DUREE_EFFET_ENGRAIS = 5  # en pas
HUMIDITE_ARROSAGE = 0.5  # humidité ajoutée si arrosage entre 0 et 1
HUMIDITE_DESSECHEMENT = 0.2  # humidité retirée si pas d'arrosage entre 0 et 1


class Parcelle():
    """Parcelle d'un potager.

    Attributes
    ----------
    _potager : Potager
        Potager d'appartenance de la parcelle.
    x: int
        Abscisse de la parcelle dans la matrice du potager.
    y: int
        Ordonnée de la parcelle dans la matrice du potager.
    plantes : list[Plante]
        Liste des plantes présentes sur la parcelle.
    insectes : list[Insecte]
        Liste des insectes présents sur la parcelle.
    dispositif : Dispositif
        Dispositif de diffusion de la parcelle, si présent.
    engrais : int
        Nombre de ticks avant expiration de
        l'engrais : 0 si aucun engrais.
    insecticide : int
        Nombre de ticks avant expiration de
        l'insecticide : 0 si aucun insecticide.
    humidite : float
        Humidité de la parcelle, comprise entre 0 et 1 (0 et 100%).
    _arrose : bool
        True si la parcelle a été arrosée durant ce pas. Se reset à chaque
        fois que la parcelle met à jour son état.

    Methods
    -------
    update_plantes(self) -> None:
        Met à jour toutes les plantes de la parcelle.
    update_insectes(self) -> None:
        Met à jour tous les insectes de la parcelle.
    update_dispositif(self) -> None:
        Vérifie si le dispositif devrait être actif ce pas-ci et simule son
        activation si c'est le cas
    update_parcelle(self) -> None:
        Met à jour l'état du sol de la parcelle.
    arroser(self) -> float:
        Change l'humidité de la parcelle pour simuler un arrosage.
        Renvoie l'humidité après arrosage.
    accueillir(self,list[Insecte]) -> None
        Déplace l'insecte de sa parcelle d'origine à celle-ci.

    mettre_engrais(self) -> None:
        Change la quantité d'engrais de la parcelle pour
        simuler la dispersion d'engrais par un dispositif.

    mettre_insecticide(self) -> None:
        Change la quantité d'insecticide de la parcelle pour
        simuler la dispersion d'insecticide par un dispositif.
    """

    def __init__(self,
                 potager: Potager,
                 pos_x: int,
                 pos_y: int,
                 humidite: float = HUMIDITE_INIT,
                 plantes: list = None,
                 insectes: list = None,
                 dispositif: Dispositif = None) -> None:
        """Constructeur de la classe Parcelle.

        Parameters.
        ----------
        pos_x : int
            Coordonnée x (sens de la longueur) de la parcelle par rapport
            au potager.
        pos_y : int
            Coordonnée y (sens de la largeur) de la parcelle par rapport
            au potager.
        potager : Potager
            Potager d'appartenance de la parcelle.
        plantes : list[Plante]
            Liste des plantes présentes sur la parcelle.
        insectes : list[Insecte]
            Liste des insectes présents sur la parcelle.
        dispositif : Dispositif|None
            Dispositif de la parcelle, si présent.
        humidite : float
            Humidité de la parcelle entre 0 et 1.

        Raises
        ------
        TypeError
            Les paramètres ne respectent pas les types demandés.

        Returns
        -------
        None.

        """
        # Définition du potager
        if isinstance(potager, Potager):
            self._potager = potager
            # Définition des coordonnées de la parcelle
            try:
                self._pos_x = int(pos_x)
                self._pos_y = int(pos_y)
            except ValueError as exc:
                raise TypeError("pos_x et pos_y ne sont pas valides.") from exc
        else:
            raise TypeError("potager doit être une instance de Potager.")

        # Définition des plantes
        self._plantes = []
        if isinstance(plantes, list):
            for entree in plantes:  # Pour chaque plante de la parcelle
                self.planter(entree)
            if self._plantes:  # Si il y a des plantes
                if self.surface_totale > 1:
                    raise ValueError("La surface au sol prise par les plantes"
                                     + "dépasse celle de la parcelle.")
        elif plantes is not None:
            raise TypeError(
                "plantes doit être une liste d'instances de Plante ou hérité.")

        # Définition des insectes
        self._insectes = []
        if isinstance(insectes, list):
            for entree in insectes:  # Pour chaque insecte de la parcelle
                self.accueillir(entree)
        elif insectes is not None:
            raise TypeError(
                "insectes doit être une liste d'instances de Insecte.")

        # Définition de l'humidité
        try:
            self._humidite = float(humidite)
        except ValueError as exc:
            raise TypeError("humidite doit être un flottant entre 0 et 1.") \
                from exc
        if self._humidite < 0 or self._humidite > 1:
            raise ValueError("humidite doit être compris entre 0 et 1.")

        # Définition du dispositif
        self._dispositif = None
        self.dispositif = dispositif
        # Définition des intrants
        self._engrais = 0
        self._insecticide = 0
        self._arrose = 0

    @property
    def pos_x(self) -> int:
        """Attribute x getter."""
        return self._pos_x

    @property
    def pos_y(self) -> int:
        """Attribute y getter."""
        return self._pos_y

    @property
    def potager(self) -> Potager:
        """Attribute potager getter."""
        return self._potager

    @property
    def plantes(self) -> list:
        """Attribute plantes getter."""
        return self._plantes

    @property
    def surface_totale(self) -> float:
        """Renvoie la surface totale occupée par les plantes de la parcelle."""
        return sum([plante._surface_parcelle for plante in self.plantes])

    @property
    def insectes(self) -> list:
        """Attribute insectes getter."""
        return self._insectes

    @property
    def nb_insectes(self) -> dict:
        """Obtenir le nombre d'insectes sur la parcelle de chaque espèce."""
        l_insectes = dict()
        for i in self.insectes:
            if i.espece not in l_insectes.keys():
                l_insectes[i.espece] = 0
            l_insectes[i.espece] += 1
        return l_insectes
    @property
    def dispositif(self) -> (Dispositif, None):
        """Attribute dispositif getter."""
        return self._dispositif

    @dispositif.setter
    def dispositif(self, dispositif) -> None:
        """Attribute dispositif setter."""
        if dispositif is None:
            self._dispositif = None
        else:
            if isinstance(dispositif, Dispositif):
                self._dispositif = dispositif
                # On définit la parcelle
                self._dispositif.parcelle = self
            else:
                raise TypeError("dispositif doit être instance de Dispositif.")

    @property
    def humidite(self):
        """Attribute humidite getter."""
        return self._humidite

    @property
    def engrais(self):
        """Attribute engrais getter."""
        return self._engrais

    @property
    def insecticide(self):
        """Attribute insecticide getter."""
        return self._insecticide

    def update_plantes(self) -> None:
        """Met à jour toutes les plantes de la parcelle."""
        for plante in self._plantes:
            plante.update_developpement()
        for plante in self._plantes:
            plante.update_fruits()
        for plante in self._plantes:
            if isinstance(plante, Drageon):
                plante.coloniser()

    def update_insectes(self) -> None:
        """Met à jour tous les insectes de la parcelle."""
        for insecte in self._insectes:
            insecte.survivre()
        for insecte in self._insectes:
            insecte.se_nourrir()
        for insecte in self._insectes:
            for i in insecte.reproduire():
                self.accueillir(i)
        for insecte in self._insectes:
            insecte.bouger()

    def update_dispositif(self) -> None:
        """Vérifie si l'activation du dispositif et simule son activation."""
        if self._dispositif is None:
            return  # Pas de dispositif sur la parcelle
        produits = self._dispositif.actif
        eau = "eau" in produits
        engrais = "engrais" in produits
        insecticide = "insecticide" in produits
        try:
            self._potager.affecter(self._dispositif.portee, self,
                                   eau, engrais, insecticide)
        except AttributeError as exc:
            raise UnboundLocalError("Le potager doit être définie pour"
                                    + " la parcelle.") from exc
        except ValueError as exc:
            raise ValueError("erreur") from exc

    def update_parcelle(self) -> None:
        """Met à jour l'état du sol de la parcelle.

        -La plante se déssèche si elle n'a pas été arrosé ce tour.
        -L'engrais et l'insecticide se dissipent partiellement.
        """
        if self._arrose:
            self._arrose = False
        else:
            self._humidite -= HUMIDITE_DESSECHEMENT
            if self._humidite < 0:
                self._humidite = 0  # L'humidité ne peut pas être négative

        self._insecticide = max(self._insecticide - 1, 0)
        self._engrais = max(self._engrais - 1, 0)
        for plante in self._plantes:
            plante.pas()
        for insecte in self._insectes:
            insecte.pas()
        if self._dispositif:
            self._dispositif.pas()

    def arroser(self) -> float:
        """Change l'humidité de la parcelle pour simuler un arrosage.

        Renvoie l'humidité après arrosage.
        """
        self._humidite = min(self._humidite + HUMIDITE_ARROSAGE, 1)
        self._arrose = True
        return self._humidite

    def mettre_engrais(self) -> None:
        """La fonction simule la dispersion d'engrais.

        Change la quantité d'engrais de la parcelle pour
        simuler la dispersion d'engrais par un dispositif.
        """
        self._engrais = DUREE_EFFET_ENGRAIS

    def mettre_insecticide(self) -> None:
        """La fonction simule la dispersion d'insecticide.

        Change la quantité d'insecticide de la parcelle pour
        simuler la dispersion d'insecticide par un dispositif.
        """
        self._insecticide = DUREE_EFFET_INSECTICIDE

    def voisinerandom(self):
        """Renvoie une parcelle voisine aléatoire de la parcelle.

        Renvoie None si la parcelle n'a pas de parcelle voisine.
        """
        return self.potager.voisinerandom(self)

    def voisines(self, portee: int = 1) -> list:
        """Renvoie la liste des parcelles voisine de la parcelle.

        Renvoie [] si la parcelle n'a pas de voisines.
        """
        return self.potager.voisines(self, portee)

    def accueillir(self, insecte) -> None:
        """Déplace l'insecte de sa parcelle d'origine à celle-ci."""
        if isinstance(insecte, Insecte):
            if insecte.parcelle is not None:
                insecte.parcelle._insectes.remove(insecte)
            # On définit sa parcelle
            insecte.parcelle = self
            self._insectes.append(insecte)
            log.info(f"{insecte.espece} accueilli sur la parcelle {self}")
        else:
            raise TypeError(
                "Chaque élément doit être "
                + "instance de Insecte ou hérité.")

    def planter(self, plante) -> None:
        """Ajoute la plante aux plantes de la parcelle."""
        if isinstance(plante, Plante):
            # On définit sa parcelle
            plante.parcelle = self
            self._plantes.append(plante)
            log.info(f"{plante.espece} plantée sur la parcelle {self}")
        else:
            raise TypeError(
                "Chaque élément doit être "
                + "instance de Plante ou hérité.")

    def __repr__(self):
        """__repr__ of Parcelle class."""
        return str((self.pos_x, self.pos_y))


if __name__ == "__main__":

    from tests import tests_potager, tests_parcelle

    print("""=== Test de la classe Potager ===""")
    tests_potager("test").run()
    print("""=== Test de la classe Parcelle ===""")
    tests_parcelle("test").run()
