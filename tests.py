# -*- coding: utf-8 -*-

"""tests.

Contient le code permettant d'effectuer les tests unitaires du code
"""

from potager import Potager as pot
import unittest
import logging as log

log.basicConfig()
NOM_PLANTE_TEST = "géranium rose"
NOM_FICHIER_TEST = "tests/potager_test.xml"
NB_ITER = 5


class tests_parcelle(unittest.TestCase):

    def test(self):
        print("Test des fonctions de gestion des voisins des parcelles...")
        self.test_voisins()

    def test_voisins(self):
        pota = pot.Potager(None, NB_ITER, 5, 5)
        par = pota.parcelles[0][0]

        # self.assertEqual(self.plante.espece, NOM_PLANTE_TEST)
        self.assertTrue(par.voisinerandom() in par.voisines(),
                        """Un voisin aléatoire fait partie des voisins de la
                        parcelle dans un cas standard.""")
        for i in range(1, 4):
            self.assertEqual(len(par.voisines(i)),
                             len(list(set(par.voisines(i)))))

        pota = pot.Potager(None, NB_ITER, 1, 1)
        par = pota.parcelles[0][0]

        self.assertEqual(par.voisines(), [], """Une parcelle seule n'a pas de
                         parcelles voisines.""")
        self.assertIs(par.voisinerandom(), None, """Parcelle.voisinerandom()
                      renvoit None pour une parcelle sans voisines.""")

        pota = pot.Potager(None, NB_ITER, 14, 14)
        par = pota.parcelles[7][7]

        self.assertRaises(ValueError, par.voisines, 0)
        n_voisines = [0, 4, 4+8, 4+8+12, 4+8+12+16]
        for i in range(1, 5):
            voisines = par.voisines(i)
            print(["".join([("✅" if p in voisines else "❌") for p in r])
                   for r in pota.parcelles])
            print(f"portee = {i}   L = {len(voisines)}")
            self.assertEqual(len(voisines), n_voisines[i])
            input()


class tests_potager(unittest.TestCase):

    def test(self):
        print("Test des paramètres du constructeur de Potager...")
        self.tests_parametres()

    def tests_parametres(self):
        # Constantes d'initialisation
        NOM_FICHIER_TEST = "tests/potager_test.xml"
        LONGUEUR_TEST = 5
        LARGEUR_TEST = 5

        # Test de pas invalide
        N_INVALIDE = "carambar"
        self.assertRaises(TypeError,
                          pot.Potager, (NOM_FICHIER_TEST, N_INVALIDE,
                                            LONGUEUR_TEST, LARGEUR_TEST),
                          "Un pas invalide doit causer une TypeError.")

        # Test de fichier invalide
        NOM_FICHIER_INVALIDE = "SHOULD_NOT_EXIST.txt"
        self.assertRaises(TypeError,
                          pot.Potager, (NOM_FICHIER_INVALIDE, N_INVALIDE,
                                            LONGUEUR_TEST, LARGEUR_TEST),
                          "Un fichier invalide doit causer une OSError.")

        # Test de pas trop petit
        N_INVALIDE = -5
        self.assertRaises(TypeError,
                          pot.Potager, (NOM_FICHIER_TEST, N_INVALIDE,
                                            LONGUEUR_TEST, LARGEUR_TEST),
                          "Un pas trop faible doit causer une ValueError.")

        N = 5  # Test d'avance normal avec le fichier de test
        potager_test = pot.Potager(NOM_FICHIER_TEST, N,
                                       LONGUEUR_TEST, LARGEUR_TEST)

        for _ in range(N-1):
            self.assertTrue(potager_test.pas(),
                            "La simulation s'arrête trop tôt.")
        self.assertFalse(potager_test.pas(),
                         "La simulation s'arrête trop tard.")
        # Au pas final, potager.pas() renvoie False


class tests_plante(unittest.TestCase):

    @unittest.skip("Plante")
    def test(self):
        print("Test des paramètres du constructeur de Plante...")
        self.tests_parametres()
        self.test_maturation()

    def tests_parametres(self):
        pass

    def test_maturation(self):
        # Faire un test sur le fait de bien récupérer un fruit après un nombre suffisant de jours de maturation du fruit (bien faire attention au fait que la maturation du fruit dépend du bon développement de la plante)
        pota = pot.Potager(None, NB_ITER, 5, 5)
        par = pota.parcelles[2][2]
        par.planter(pot.Plante(self, "geranium", 3, 3, 4, (0.1, 0.9), 0.2))
        # Faire un test sur la prolifération d'un drageon dont les attribut ont été boostés au maximum (mettre un drageon solo au milieu du potager et vérifier qu'il colonise bien les parcelles voisines)
        # Faire un test pour vérifier que la plante n'est plus capable de produire de fruit après avoir son nombre maximal de récolte possible.
        # Faire un test pour vérifier que l'humidité diminue/augmente bien en cas d'usage ou non d'arrosage
        # Faire un test pour vérifier le bon développement de la plante en fonction des dispositifs et insectes présents sur la parcelle de la plante (vérifier le bon fonctionnement de la fonction dev)
        # TODO : Tester la classe Plante et Drageon
        pass


class tests_insecte(unittest.TestCase):

    @unittest.skip("Test Insecte")
    def test(self):
        print("Test des paramètres du constructeur de Insecte...")
        self.tests_parametres()

    def tests_parametres(self):
        # Faire un test pour vérifier l'évolution du niveau de vie de l'insecte en fonction de s'il s'est nourri ou pas et depuis cbm de temps
        # Faier un test pour vérifier qu'un insecte meurt bien si l'une des conditions est vérifiée
        # Faire un test pour vérifier le bon comportement d'un accouplement d'insectes et le bon comportement de la portée (vérifier que les mutation marchent bien également ?)
        # Vérifier qu'un insecte peut bien se déplacer d'une parcelle à une autre
        # Vérifier le respect du temps entre reproduction des insectes
        # Vérifier que le nombre de pv max est respecté et ne peut être dépassé

        # TODO : Tester la classe Insecte
        pass


class tests_dispositif(unittest.TestCase):

    @unittest.skip("Test Dispositif")
    def test(self):
        print("Test des paramètres du constructeur de Insecte...")
        # self.tests_parametres()
        self.tests_actif()

    def tests_parametres(self):
        # Vérifier qu'un dispositif s'efface bien une fois le nombre de pas effectifs dépassés
        # Vérifier qu'un dispositif est bien capable de se disperser sur les parcelles voisines de celle sur laquel il a été appliqué
        # TODO : Tester la classe Dispositif
        raise NotImplementedError("Y'a moy'sss de birser !")
    
    def tests_actif(self):
        d = pot.Dispositif(5,[pot.Programme("eau",5,3,5),pot.Programme("engrais",0,2,5)])
        for i in range(30):
            if "eau" in d.actif:
                if "engrais" in d.actif:
                    print("o",end="")
                else:
                    print("x",end="")
            else:
                if "engrais" in d.actif:
                    print("*",end="")
                else:
                    print("-",end="")
            d.pas()


dict_tests = {"parcelle": tests_parcelle, "potager": tests_potager,
              "plante": tests_plante, "insecte": tests_insecte,
              "dispositif": tests_dispositif}
dict_commandes = {"tout": unittest.main}
if __name__ == "__main__":
    user_input = ""
    while user_input != "quitter":
        user_input = input("Rentrez le nom de la classe à tester :")
        if user_input == "tout":
            unittest.main()
        elif user_input in dict_tests.keys():
            dict_tests[user_input]('test').run()
