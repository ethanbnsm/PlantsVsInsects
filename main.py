# -*- coding: utf-8 -*-

"""MINI_POO – 2023_S1 : Mini POOtager.

Ce programme permet de lancer une simulation de
potager simulant pas-à-pas la vie de plantes et d'insectes
sur un quadrillage de parcelles, ainsi que le fonctionnement de
dispositifs d'arrosage et de diffusion automatiques.

Ce fichier contient le code de l'interface.
"""
# Import des builtins
import tkinter as tk
from tkinter import Menu, ttk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import math
import xml.etree.ElementTree as ET
# Import des modules internes
from potager import Potager

VERSION = "0.0.6"
TITLE_STR = f"Plantes contre Insectes v{VERSION}"
DELAI_STD = 10  # millisecondes
LARGEUR_TUILE = 32
LONGUEUR_TUILE = 32
LARGEUR_WIN_MIN = 315
LONGUEUR_WIN_MIN = 80
SEUIL_AFF_BAR = 0.01
FREQ_ACTU_MAINFRAME = 1
AUTO_INFO = False


class Interface(tk.Tk):
    """Interface de l'application.

    Attributes
    ----------
    mainframe : tk.Frame
        La Frame contenant l'ensemble de l'interface, excepté la barre de
        statut et la barre de menu.
    maincanvas : tk.Canvas
        Le Canvas contenant l'ensemble des représentations des parcelles.
    menu_... : tk.menu
        Les menus permettent le fonctionnement de la barre de menu.
    texte_etat : tk.StringVar
        Contient le texte de la barre d'état.
    potager = None : Potager
        Le potager actuellement géré par l'interface.
    lecture = False : bool
        Vrai en lecture (avance des pas automatique).
    termine = False : bool
        Vrai si la lecture vient de se terminer.
    n_pas = 0 : int
        Pas actuel de la simulation.
    delai = DELAI_STD : int
        Délai minimum entre deux pas (en avance automatique).
    par_cur = None : Parcelle
        Parcelle actuellement sélectionnée par l'utilisateur.
    fichier_cur = None : str
        Chemin du fichier actuellement ouvert.

    _aff_dispos = tk.NORMAL : str
        Les dispositifs sont visibles lorsque tk.NORMAL.
    _aff_humid = tk.NORMAL : str
        Les barres d'humidité relative sont visibles lorsque tk.NORMAL.
    _aff_b_plantes = tk.NORMAL :str
        Les barres de surface totale prise sont visibles lorsque tk.NORMAL.
    _aff_b_insectes = tk.NORMAL : str
        Les barres de quantités d'insectes sont visibles lorsque tk.NORMAL.
    _actu_compteur = 0 : int
        Compteur pour la mise à jour de l'interface en avance automatique.
    _T_nb_insectes = [] : list[Counter(str, int)]
        Liste de Counter contenant la population d'insectes par espèce à
        chaque pas.
"""

    def __init__(self):
        """Constructeur de la classe Interface."""
        super().__init__()  # Constructeur de tk.Tk()
        self.minsize(LARGEUR_WIN_MIN, LONGUEUR_WIN_MIN)
        # = Définition du thème =
        style = ttk.Style(self)
        self.tk.call("source", "assets/forest_ttk/forest-light.tcl")
        style.theme_use("forest-light")
        self.title(TITLE_STR)

        # = Barre de progression =
        self.load_frame_assets()
        barre_pas = tk.Frame(self, bd=1, height=2,
                             relief=tk.RAISED)
        barre_pas.pack(side="top", fill="none", anchor=tk.CENTER)
        tk.Button(barre_pas, state=tk.DISABLED,
                  image=self._img_bp_debut).grid(row=0, column=0,
                                                 sticky='w e n s',
                                                 padx=5, pady=5)
        tk.Button(barre_pas, state=tk.DISABLED,
                  image=self._img_bp_precedent).grid(row=0, column=1,
                                                     sticky='w e n s',
                                                     padx=5, pady=5)
        self.bt_play = tk.Button(barre_pas, command=self.toggleLecture,
                                 image=self._img_bp_play)
        self.bt_play.grid(row=0, column=2, sticky='w e n s', padx=5, pady=5)
        tk.Button(barre_pas, command=lambda: self.pas(True),
                  image=self._img_bp_suivant).grid(row=0, column=3,
                                                   sticky='w e n s',
                                                   padx=5, pady=5)
        tk.Button(barre_pas, command=self.dernier_pas,
                  image=self._img_bp_fin).grid(row=0, column=4,
                                               sticky='w e n s',
                                               padx=5, pady=5)
        # == Cadre principal ==
        self.mainframe = tk.Frame(self, bg="blue")
        self.mainframe.pack(side="top")

        # == Définition du canvas de potager ==
        self.maincanvas = tk.Canvas(self.mainframe,
                                    height=0, width=0, bg="black", bd=0)
        self.maincanvas.pack(fill="both")
        self.maincanvas.bind("<Motion>", self.update_canvas_move)
        # Gestion de l'actualisation du curseur interne

        #  == Barre de menu ==
        menu = Menu(self)
        self.config(menu=menu)

        # = Sous-menu Fichier =
        self.menu_fichier = Menu(self)
        menu_fichier = self.menu_fichier
        menu.add_cascade(label="Fichier", menu=menu_fichier)

        menu_fichier.add_command(
            label='Ouvrir',
            command=self.charger,
        )
        menu_fichier.add_command(
            label='Recharger',
            command=self.recharger,
        )
        menu_fichier.add_command(
            label='Enregistrer',
            command=self.sauvegarder,
        )
        menu_fichier.add_command(
            label='Quitter',
            command=self.destroy,
        )

        # = Sous-menu Simulation =
        self.menu_sim = Menu(self)
        menu_sim = self.menu_sim
        menu.add_cascade(label="Simulation", menu=menu_sim)

        menu_sim.add_command(
            label='Lecture',
            command=self.toggleLecture,
        )
        menu_sim.add_command(
            label='Premier pas',
            command=None,
            state=tk.DISABLED
        )
        menu_sim.add_command(
            label='Pas précédent',
            command=None,
            state=tk.DISABLED
        )
        menu_sim.add_command(
            label='Pas suivant',
            command=lambda: self.pas(True),
        )
        menu_sim.add_command(
            label='Dernier pas',
            command=self.dernier_pas,
        )
        menu_sim.add_command(
            label='Délai...',
            command=self.changer_delai,
        )

        # = Sous-menu Affichage =
        self.menu_affichage = Menu(self)
        menu_affichage = self.menu_affichage
        menu.add_cascade(label="Affichage", menu=menu_affichage)

        menu_affichage.add_command(
            label='Dispositifs',
            command=self.toggleAffDispos,
        )

        self.menu_resultats = Menu(self)
        menu_resultats = self.menu_resultats
        menu.add_cascade(label="Résultats", menu=menu_resultats)

        menu_resultats.add_command(
            label='Récolte',
            command=self.montrer_recolte
        )

        menu.add_command(
            label='À propos',
            command=self.apropos,
        )

        # Raccourcis clavier
        self.bind('<Control-s>', lambda e: self.sauvegarder())
        self.bind('<Control-o>', lambda e: self.charger())
        self.bind('<Control-q>', lambda e: self.destroy())
        self.bind('<Control-r>', lambda e: self.recharger())
        self.bind('<Control-S>', lambda e: self.sauvegarder())
        self.bind('<Control-O>', lambda e: self.charger())
        self.bind('<Control-Q>', lambda e: self.destroy())
        self.bind('<Control-R>', lambda e: self.recharger())

        self.bind('<F1>', lambda e: self.toggleLecture())
        self.bind('<space>', lambda e: self.pas(True))
        self.bind('<Control-F1>', lambda e: self.dernier_pas())

        self.bind('<F5>', lambda e: self.set_canvas())

        self.bind('<F6>', lambda e: self.changer_delai())
        self.bind('R', lambda e: self.montrer_recolte())
        self.bind('D', lambda e: self.toggleAffDispos())
        self.bind('r', lambda e: self.montrer_recolte())
        self.bind('d', lambda e: self.toggleAffDispos())

        self.bind('<F11>', lambda e: self.apropos())

        self.maincanvas.bind('<Button-1>', lambda e: self.info_parcelle())

        self.potager = None
        self.lecture = False
        self.termine = False
        self.n_pas = 0
        self.delai = DELAI_STD
        self.par_cur = None
        self.fichier_cur = None

        self._aff_dispos = tk.NORMAL
        self._aff_humid = tk.NORMAL
        self._aff_b_plantes = tk.NORMAL
        self._aff_b_insectes = tk.NORMAL
        self._actu_compteur = 0
        self._T_nb_insectes = []

    def charger(self) -> bool:
        """Charge un potager."""
        if self.potager:  # Demande de confirmation si un potager est en cours
            sauv = messagebox.askyesno(parent=self,
                                       title="Confirmation d'ouverture",
                                       message="""Un fichier a déjà été chargé.
                                       \nVoulez-vous exporter les résultats ?""")
            if sauv:
                self.sauvegarder()
        fichier_cur = filedialog.askopenfilename(filetypes=(("Fichier *","Fichier_XML {.xml}")))
        self.fichier_cur = fichier_cur
        if not fichier_cur:  # Si aucun fichier n'a été choisi
            return False
        try:
            self.potager = Potager(fichier_cur)
        except (ValueError, OSError):
            print(f"{fichier_cur} n'a pas pu être ouvert.")
            return False
        else:
            print(f"Fichier {fichier_cur} chargé.")
            self.set_canvas()
            self._T_nb_insectes = [self.potager.nb_insectes]
            self.lecture = False
            self.termine = False
            self.n_pas = 0
            return True

    def recharger(self) -> bool:
        """Recharge le potager associé au fichier censé être ouvert."""
        fichier_cur = self.fichier_cur
        if fichier_cur:
            try:
                self.potager = Potager(fichier_cur)
            except (ValueError, OSError):
                print(f"{fichier_cur} n'a pas pu être ouvert.")
                return False
            else:
                print(f"Fichier {fichier_cur} rechargé.")
                self.set_canvas()
                self._T_nb_insectes = [self.potager.nb_insectes]
                self.lecture = False
                self.termine = False
                self.n_pas = 0
                return True
        else:
            print("Aucun fichier chargé !")

    def sauvegarder(self) -> bool:
        """Exporte les résultats à un emplacement à déterminer."""
        fichier_cur = filedialog.asksaveasfilename(filetypes=(("Fichier_XML {.xml}", "Fichier {*}")))
        self.fichier_cur = fichier_cur
        tronc = ET.Element('Resultats')
        arbreXML = ET.ElementTree(tronc)
        format_recoltes = dict([(i[0], str(i[1])) for i in self.potager.recolte_par_especes().items()])
        tronc.append(ET.Element("Recolte",format_recoltes))
        T_format_nb_insectes = [dict([(i[0], str(i[1])) for i in j.items()]) for j in self._T_nb_insectes]
        for i in range(self.n_pas):
            pasXML = ET.Element("pas",{"n":str(i)})

            pasXML.append(ET.Element("Population", T_format_nb_insectes[i]))
            tronc.append(pasXML)
        ET.indent(tronc)
        arbreXML.write(fichier_cur)

    def apropos(self) -> None:
        """Affiche les informations du programme dans une Infobox."""
        messagebox.showinfo(parent=self, title="A propos",
                            message=f"""Plantes contre Insectes\n
                            Version {VERSION}
                            Réalisation :
                            Mathis Cosson, Côme Sixdenier
                            pour le projet MINI-POO\n
                            Les textures des tuiles ©Mojang
                            Les textures des dispositifs ©Chucklefish
                            Utilise le thème Forest-light sous license MIT""")

    def changer_delai(self) -> None:
        """Ouvre une fenêtre pour spécifier le délai réel entre les pas."""
        self.erreur_entree_delai = False
        fen = tk.Toplevel(self)
        fen.title("Délai")
        fen.config(width=350, height=250)
        formulaire = tk.Entry(fen, text=self.delai)
        formulaire.bind("<Return>",
                        lambda e: self.get_entree_delai(fen, formulaire))
        label_requete = tk.Label(fen, text="Délai (en ms) :")
        label_requete.pack(pady=5, padx=5)
        formulaire.pack(pady=10, padx=20)
        fen.focus()

    def get_entree_delai(self, fenetre: tk.Tk, formulaire: tk.Entry) -> None:
        """Récupère dans delai l'entrée de changer_delai."""
        try:
            self.delai = int(formulaire.get())
        except ValueError:
            if not self.erreur_entree_delai:
                self.erreur_entree_delai = True
                label_erreur = tk.Label(fenetre, text="Entree invalide",
                                        foreground="red")
                label_erreur.pack(pady=10, padx=20)
        else:
            fenetre.destroy()
            print(f"Délai changé à {self.delai} ms")

    def toggleLecture(self) -> None:
        """Démarre ou arrête l'avance automatique de la simulation."""
        self.lecture = not self.lecture
        if not self.lecture:
            self.menu_sim.entryconfig(1, label="Lecture")
            self.bt_play.config(image=self._img_bp_play)
            print("Pause...")
        else:
            self.menu_sim.entryconfig(1, label="Pause")
            self.bt_play.config(image=self._img_bp_pause)
            print("Lecture...")
            self.actu_compteur = 0
        self.pas()

    def toggleAffDispos(self) -> None:
        """Inverse l'état d'affichage des dispositifs (NORMAL ou HIDDEN)."""
        if self._aff_dispos == tk.NORMAL:
            self._aff_dispos = tk.HIDDEN
            print("Dispositifs cachés")
        else:
            self._aff_dispos = tk.NORMAL
            print("Dispositifs montrés")
        self.update_dispos()

    def montrer_recolte(self) -> None:
        """Montre dans un graphique la récolte."""
        print(self.potager.recolte)
        recolte_especes = self.potager.recolte_par_especes()
        if not recolte_especes:
            print("Aucun fruit récolté")
            return
        plt.bar(recolte_especes.keys(),recolte_especes.values())

    def update_mainframe(self) -> None:
        """Met à jour le cadre principal du programme."""
        self.update_barres()
        self.update_dispos()

    def update_barres(self) -> None:
        """Met à jour les barres d'information de chaque parcelle."""
        for i in range(self.potager.longueur):
            for j in range(self.potager.largeur):
                if self.potager.parcelles[i][j]:
                    # Pour chaque parcelle du potager :
                    par = self.potager.parcelles[i][j]

                    # Affichage des barres de surface
                    self.maincanvas.coords(self.entites_id["lignes_surf"][i][j],
                        (i * LONGUEUR_TUILE + 2, j * LARGEUR_TUILE + 2,
                         i * LONGUEUR_TUILE + 2 + int(par.surface_totale
                                                       * LONGUEUR_TUILE),
                         j * LARGEUR_TUILE + 5))
                    etat = tk.NORMAL if par.surface_totale >= SEUIL_AFF_BAR else tk.HIDDEN
                    self.maincanvas.itemconfig(self.entites_id["lignes_surf"][i][j],
                                               state=etat and self._aff_b_plantes)

                    # Affichage des barres d'humidité
                    self.maincanvas.coords(self.entites_id["lignes_humid"][i][j],
                        (i * LONGUEUR_TUILE + 2, j * LARGEUR_TUILE + 5,
                         i * LONGUEUR_TUILE + 2 + par.humidite
                         * LONGUEUR_TUILE, j * LARGEUR_TUILE + 8))
                    etat = tk.NORMAL if par.humidite >= SEUIL_AFF_BAR else tk.HIDDEN
                    self.maincanvas.itemconfig(self.entites_id["lignes_humid"][i][j],
                                               state=etat and self._aff_humid)

                    # TODO : Indicateur de status des dispositifs

                    # Affichage des barres d'insecte
                    self.maincanvas.coords(self.entites_id["barres_insecte"][i][j],
                        (i * LONGUEUR_TUILE + 2,
                         j * LARGEUR_TUILE + 8,
                         i * LONGUEUR_TUILE + 2
                         + int(math.log(1+sum(list(par.nb_insectes.values())))
                               / 4 * LONGUEUR_TUILE),
                         j * LARGEUR_TUILE + 10))
                    self.maincanvas.itemconfig(self.entites_id["barres_insecte"][i][j],
                                               state=self._aff_b_insectes)

    def update_dispos(self):
        """Met à jour l'état de l'affichage des dispositifs."""
        for i in range(self.potager.longueur):
            for j in range(self.potager.largeur):
                if not self.potager.parcelles[i][j]:
                    continue
                par = self.potager.parcelles[i][j]
                if par.dispositif is None:
                    continue
                self.maincanvas.itemconfig(self.entites_id["dispositifs"][i][j],
                                           state=self._aff_dispos)

    def set_canvas(self):
        """Charge le canvas montrant le potager."""
        # Chargement des sprites
        self.load_assets()
        self.title(f"{self.potager.nom_potager} - {TITLE_STR}")
        # Liste des clés des entités pour chaque parcelle sur le canvas
        self.el_canvas = ["parcelles", "lignes_surf", "lignes_humid",
                          "dispositifs", "barres_insecte"]
        # Liste des éléments de canvas actualisés et correspondant au dict
        # self.entites_id
        self.entites_id = dict([(i, ([[None
                               for j in range(self.potager.largeur)]
                               for i in range(self.potager.longueur)]))
                               for i in self.el_canvas])
        c = self.maincanvas  # Raccourci
# =============================================================================
#       On définit les dimensions de la fenêtre et du cadre pour que la
#       barre d'état et le canvas ne soient pas rognés.
# =============================================================================
        self.minsize(max(LARGEUR_WIN_MIN,
                         self.potager.longueur * LONGUEUR_TUILE + 10),
                     LONGUEUR_WIN_MIN + self.potager.largeur * LARGEUR_TUILE)
        c.config(height=self.potager.largeur * LARGEUR_TUILE,
                 width=self.potager.longueur * LONGUEUR_TUILE)
        # On initialise chaque case du canvas grâce au potager
        for i in range(self.potager.longueur):
            for j in range(self.potager.largeur):
                if self.potager.parcelles[i][j]:
                    par = self.potager.parcelles[i][j]
                    # Il y a une parcelle à cet endroit du potager
                    self.entites_id["parcelles"][i][j] = c.create_image(
                        (i * LONGUEUR_TUILE + 2,
                         j * LARGEUR_TUILE + 2),
                        image=self._img_parcelle_s, anchor="nw")
                    # Affichage des dispositifs
                    if par.dispositif is not None:
                        portee = par.dispositif.portee
                        portee_aff = min(portee - 1, 2)
                        self.entites_id["dispositifs"][i][j] = c.create_image(
                            (i * LONGUEUR_TUILE + 2,
                             j * LARGEUR_TUILE + 2),
                            image=self._imgs_sprk[portee_aff], anchor="nw",
                            state=self._aff_dispos)
                    # Affichage des barres de surface
                    self.entites_id["lignes_surf"][i][j] = c.create_rectangle(
                         (i * LONGUEUR_TUILE + 2,
                          j * LARGEUR_TUILE + 2,
                          i * LONGUEUR_TUILE + 2 + int(par.surface_totale
                                                       * LONGUEUR_TUILE),
                          j * LARGEUR_TUILE + 4),
                         fill="green", state=self._aff_b_plantes)
                    # Affichage des barres d'humidité
                    self.entites_id["lignes_humid"][i][j] = c.create_rectangle(
                        (i * LONGUEUR_TUILE + 2,
                         j * LARGEUR_TUILE + 6,
                         i * LONGUEUR_TUILE + 2 + par.humidite * LONGUEUR_TUILE,
                         j * LARGEUR_TUILE + 8),
                        fill="blue", state=self._aff_humid)
                    # Affichage des insectes
                    self.entites_id["barres_insecte"][i][j] = c.create_rectangle(
                        (i * LONGUEUR_TUILE + 2,
                         j * LARGEUR_TUILE + 8,
                         i * LONGUEUR_TUILE + 2
                         + int(math.log(1+sum(list(par.nb_insectes.values())))
                               / 3 * LONGUEUR_TUILE),
                         j * LARGEUR_TUILE + 10),
                        fill="red", state=self._aff_b_insectes)
                else:
                    # Affichage des tuiles vides
                    self.entites_id["parcelles"][i][j] = c.create_image(
                        (i * LONGUEUR_TUILE + 2,
                         j * LARGEUR_TUILE + 2),
                        image=self._img_defaut, anchor="nw")
        # Affichage du curseur
        self.tile_cursor = c.create_image((0, 0),
                                          image=self._img_cursor, anchor="nw")
        self.update_mainframe()

    def update_canvas_move(self, event):
        """Event lorsque l'on déplace le curseur dans le canvas.

        La parcelle sélectionnée est récupérée à partir de la position
        du curseur dans le canvas. Si AUTO_INFO, on en affiche les
        caractéristiques.
        """
        if not self.potager:
            return  # Pas de potager chargé
        # On récupère les coordonnées de la parcelle dans le potager
        self.par_x = min(event.x//LONGUEUR_TUILE, self.potager.longueur-1)
        self.par_y = min(event.y//LARGEUR_TUILE, self.potager.largeur-1)
        # Si on a mis le curseur sur une autre parcelle
        if self.par_cur != self.potager.parcelles[self.par_x][self.par_y]:
            self.par_cur = self.potager.parcelles[self.par_x][self.par_y]
            if AUTO_INFO:
                self.info_parcelle()
        if self.tile_cursor:
            # Déplacer le curseur sur la parcelle sélectionnée
            self.maincanvas.moveto(self.tile_cursor,
                                   self.par_x * LONGUEUR_TUILE + 2,
                                   self.par_y * LARGEUR_TUILE + 2)

    def info_parcelle(self) -> None:
        """Affiche les informations de la parcelle."""
        if self.par_cur:
            # Il y a une parcelle à cet endroit
            print(f"""Parcelle X{self.par_x} Y{self.par_y}\t
                  {self.par_cur.humidite}\t
                  {len(self.par_cur.insectes)}""", end="")
            if self.par_cur.dispositif is not None:
                # Il y a un dispositif sur la parcelle
                print(f"""\t\t D{self.par_cur.dispositif.portee}""")
            else:
                print("")
            aff_plantes = [
                print(f"""{p.espece}\t{p.surface_parcelle}\t{p.age}""")
                for p in self.par_cur.plantes
                          ]
        else:
            print("Pas de parcelle")

    def pas(self, une_fois=False) -> None:
        """Gère l'avancement de la simulation pas-à-pas ou automatique.

        Si un potager est chargé, on avance au choix selon deux modes:
            En mode pas-à-pas (une_fois=True):
                on avance de seulement un pas.
            En mode automatique (une_fois=False):
                on avance d'un pas, puis on crée un timer pour qu'un autre
                pas soit exécuté jusqu'à ce que le potager se termine.
        """
        if self.potager and (self.lecture or une_fois):
            self.n_pas += 1
            termine = not self.potager.pas() # Voir Potager
            print(f"pas n°{self.n_pas} : {self.potager.nb_insectes}")
# =============================================================================
#           Ces conditions permettent que la première fois qu'on utilise
#           l'avance automatique, la simulation s'arrête au pas indiqué dans
#           le fichier. Par contre, une fois que la simulation a été terminée
#           au moins une fois, la simulation ne pourra être arrêtée que
#           manuellement.
# =============================================================================
            if not self.termine and termine:
                self.termine = True
                if self.lecture:
                    self.toggleLecture()
                print("terminé")
            self._T_nb_insectes.append(self.potager.nb_insectes)
        if une_fois or self._actu_compteur % FREQ_ACTU_MAINFRAME == 0:
            # On ne met à jour l'affichage que tout les FREQ_ACTU_MAINFRAME pas
            self.update_mainframe()
        if self.lecture:
            self._actu_compteur += 1
            self.after(self.delai, self.pas)  # On planifie le pas suivant

    def dernier_pas(self) -> None:
        """Avance la simulation jusqu'au pas maximum sans actualiser."""
        if self.potager:
            n_pas_debut = self.n_pas
            while not self.termine:
                # La simulation ne s'effectue pas si le potager a déjà été fini
                self._T_nb_insectes.append(self.potager.nb_insectes)
                self.termine = not self.potager.pas()
                self.n_pas += 1
            print(f"Terminé : {self.n_pas-n_pas_debut} pas effectués")
            self.update_mainframe()

    def chargement_manuel(self, potager):
        """Charge un potager depuis une instance de Potager."""
        if isinstance(potager, Potager):
            # On définit le potager associé à l'interface
            self.potager = potager
            self.set_canvas()
            self.fichier_cur = self.potager._nom_fichier
            print("Potager chargé.")

    def load_frame_assets(self):
        """Charge les fichiers de l'interface."""
        self._img_bp_debut = tk.PhotoImage(file="assets/debut.png")
        self._img_bp_fin = tk.PhotoImage(file="assets/fin.png")
        self._img_bp_pause = tk.PhotoImage(file="assets/pause.png")
        self._img_bp_play = tk.PhotoImage(file="assets/play.png")
        self._img_bp_precedent = tk.PhotoImage(file="assets/precedent.png")
        self._img_bp_stop = tk.PhotoImage(file="assets/stop.png")
        self._img_bp_suivant = tk.PhotoImage(file="assets/suivant.png")

    def load_assets(self):
        """Charge les sprites pour le canvas principal."""
        self._img_parcelle_h = tk.PhotoImage(file="assets/parcelle_humide.png")
        self._img_parcelle_s = tk.PhotoImage(file="assets/parcelle_seche.png")
        self._img_defaut = tk.PhotoImage(file="assets/defaut.png")
        self._img_cursor = tk.PhotoImage(file="assets/cursor.png")
        self._img_sprk_1 = tk.PhotoImage(file="assets/sprinkler_1.png")
        self._img_sprk_2 = tk.PhotoImage(file="assets/sprinkler_2.png")
        self._img_sprk_3 = tk.PhotoImage(file="assets/sprinkler_3.png")
        self._imgs_sprk = [self._img_sprk_1, self._img_sprk_2, self._img_sprk_3]


if __name__ == "__main__":
    app = Interface()
    pota = Potager("levels/Pootager_Cas_4_modifie.xml")
    # Cas préprogrammé dès le lancement
    app.chargement_manuel(pota)
    app.mainloop()
