#Importation des modules dont on a besoin
import random, curses, time


#On définit ces variables dès le début pour pouvoir les rendre globale au lieu qu'elle reste locale
entree_x, entree_y = None, None
sortie_x, sortie_y = None, None


#Fonction qui va créer le labyrinthe
def creer_labyrinthe(taille, proportion_chemins):
    #Initialisation d'une matrice avec que des 1
    labyrinthe = [[1 for i in range(taille)] for j in range(taille)]

    #Calcul du nb de cases qui vont être des chemins
    nb_cases_libres = int(taille * taille * proportion_chemins)
    
    #Liste de tts les positions possibles
    tts_positions = [(i, j) for i in range(taille) for j in range(taille)]
    #Tirage des cases qui vont être des chemins
    chemins_positions = random.sample(tts_positions, nb_cases_libres)

    for x, y in chemins_positions:
        #Attribution de la valeur 0 au cases tirées pour qu'elles soit considérées cm des chemins par la suite
        labyrinthe[x][y] = 0

    #On définit les coins de la matrice
    coins = [(0, 0), (0, taille - 1), (taille - 1, 0), (taille - 1, taille - 1)]
    #Rend les 4 variables globales
    global entree_x, entree_y, sortie_x, sortie_y
    #Choisit un coin pour l'entrée
    entree_x, entree_y = random.choice(coins)
    #Retire l'entrée des coins possibles pour la sortie
    coins.remove((entree_x, entree_y))
    sortie_x, sortie_y = random.choice(coins) 

    #Attribue une valeur à l'entrée et la sortie pour pouvoir les repérer plus tard
    labyrinthe[entree_x][entree_y] = 3
    labyrinthe[sortie_x][sortie_y] = 2

    #La fonction retourne le labyrinthe
    return labyrinthe


# def afficher_labyrinthe(labyrinthe, dico):
#     for ligne in labyrinthe:
#         ligne_affichee = ''.join(dico[valeur] for valeur in ligne)
#         print(ligne_affichee)


#Fonction qui va créer le joueur
def creer_joueur():
    #Le joueur est définit par un dictionnaire
    return {"symbole": "^", "x": entree_x, "y": entree_y}


# def afficher_labyrinthe_avec_joueur(labyrinthe, dico, joueur):
#     for i, ligne in enumerate(labyrinthe):
#         ligne_affichee = ""
#         for j, case in enumerate(ligne):
#             if i == joueur["x"] and j == joueur["y"]:
#                 ligne_affichee += joueur["symbole"]
#             else:
#                 ligne_affichee += dico[case]
#         print(ligne_affichee)


#Fonction qui va créer les objets
def cree_objets(labyrinthe, nb_objets):
    #Recuperation de la taille pour l'utiliser comme condition d'arrêt du in range
    taille = len(labyrinthe)
    #Création d'une liste qui va contenir tous les positions libres du labyrinthe 
    # c'est à dire les positions qui ne sont ni des murs, ni une entrée ou sortie
    cases_libres = [
        (i, j) for i in range(taille) for j in range(taille)
        if labyrinthe[i][j] == 0 and (i, j) != (entree_x, entree_y) and (i, j) != (sortie_x, sortie_y)
    ]
    
    #Retourne les positions aléatoires que vont prendre les objets en fonction des cases libres
    return random.sample(cases_libres, nb_objets)


#Fonction pour le ramassage des objets
def ramasser_objets(stdscr, joueur, objets):
    #Récupération de la position du joueur
    position_joueur = (joueur["x"], joueur["y"])
    #Condition que la position du joueur correspondent à la position d'un objet 
    if position_joueur in objets: 
        #Si c'est le cas on retire l'objet de la liste des objets à ramasser
        objets.remove(position_joueur) 
        stdscr.addstr(0, 0, "Objet collecté !")
        stdscr.refresh() 
        #Tps d'arrêt pour afficher le message à l'écran
        curses.napms(200) 
        return True
    return False


#Fonction qui affiche le labyrinthe à la fois avec le joueur et les différents objets
def afficher_labyrinthe_avec_joueur_et_objets(stdscr, labyrinthe, dico, joueur, objets):
    symbole_objets = '$'
    #On parcourt les lignes du labyrinthes, i étant l'index de la ligne, et ligne la liste 
    # avec les valeurs de celle ci
    for ligne_index, ligne in enumerate(labyrinthe):
        #Initialisation d'un string vide pour afficher la ligne
        ligne_affichee = ""
        #On parcourt les valeurs de la ligne, avec j étant l'index de la case ds la matrice, et 
        # case la valeur de la case (mur, chemin, entrée, sortie)
        for colonne_index, case in enumerate(ligne):
            #Condition que les coord soit celles liés à la position du joueur
            if ligne_index == joueur["x"] and colonne_index == joueur["y"]:
                #Si c'est le cas on affiche le symbole qu'on a donné au joueur dans le dictionnaire
                ligne_affichee += joueur["symbole"]
            #Si ce n'est pas les coord du joueur, on vérifie que ce ne sont pas les coord d'un objet
            elif (ligne_index, colonne_index) in objets:
                #Si c'est le cas on affiche le symbole des objets défini qql lignes plus haut
                ligne_affichee += symbole_objets
            #Si c'est ni les coord du joueur ou d'un objet on va afficher que c'est un chemin ou un 
            # mur en fonction de la valeur de la case
            else:
                ligne_affichee += dico[case]
        
        #Affiche la ligne à l'écran
        stdscr.addstr(ligne_index + 1, 0, ligne_affichee)


#Fonction pour mettre à jour la position du joueur
def update_p(stdscr, letter, joueur, labyrinthe):
    #Associe chaque direction à un mouvement sur la matrice
    directions = {'z': (-1, 0), 'q': (0, -1), 's': (1, 0), 'd': (0, 1)}

    #Condition que la touche pressée soit une direction acceptée
    if letter in directions:
        #On récupère à partir du dict direction le mouvement à réaliser x étant le dep vertical et y le dep horizontal
        deplacement_x, deplacement_y = directions[letter]
        #Stockage temporaire des nv valeurs le temps de vérifier qu'elles sont autorisés
        nv_x = joueur['x'] + deplacement_x
        nv_y = joueur['y'] + deplacement_y

        #Condition que la nv position ne soit pas en dehors de la matrice et n'est pas un mur
        if 0 <= nv_x < len(labyrinthe) and 0 <= nv_y < len(labyrinthe[0]) and labyrinthe[nv_x][nv_y] != 1:
            #Si c'est le cas on attribue les nv valeurs au joueur
            joueur['x'] = nv_x
            joueur['y'] = nv_y
        else:
            #Si c'est pas le cas on renvoie un message d'erreur
            stdscr.addstr(0, 0, "Mauvaise direction !")
            stdscr.refresh()
            #Tps d'arrêt pour afficher le message 
            curses.napms(500)
    else:
        #Si carrément la touche cliquée par l'utilisateur n'est pas une touche autorisée on renvoie 
        # un autre message d'erreur
        stdscr.addstr(0, 0, "Direction invalide !")
        stdscr.refresh()
        #Tjr un tps d'arrêt pour afficher le message
        curses.napms(500)


#Fonction qui permet de gérer le jeu à l'infini
def mode_infini(taille, proportion_chemins, niveau, nb_objet):
    #Augmente la taille de la matrice à chaque nv niveau
    taille += 1
    #Augmente le compteur du niveau affiché
    niveau += 1
    #Augmente le nb d'objet à collecter
    nb_objet +=1
    #Condition que la proportion soit pas inférieur à 0.7 histoire que le labyrinthe soit encore faisable quoi 
    if proportion_chemins>0.7:
        #On baisse de 0.05 la proportion à chaque nouveau niveau 
        proportion_chemins -= 0.05
        
    #Création du nv labyrinthe
    labyrinthe = creer_labyrinthe(taille, proportion_chemins)
    #On réintalise la position du joueur
    joueur = creer_joueur()
    #Création des nvx objets
    objets = cree_objets(labyrinthe, nb_objet)

    #On retourne toutes les valeurs dont on a besoin pour générer un nv niveau
    return labyrinthe, proportion_chemins, joueur, objets, taille, niveau, nb_objet


#Fonction qui va créer le chronomètre et agir en fct du temps
def chronometre(stdscr, temps_limite, debut, labyrinthe):
    #tps écoulé
    temps_ecoule = time.time() - debut
    #Tps restant et on met le max à 0 pr pas que ce soit négatif
    temps_restant = max(0, int(temps_limite - temps_ecoule))
    #Permet l'affichage du tps restant
    stdscr.addstr(len(labyrinthe) + 5, 0, f"Temps restant : {temps_restant}s")
    stdscr.refresh()

    #Si tps écoulé alors sa retourne True et du coup la condition dans la fct main s'active
    return temps_restant == 0


#Fonction principale
def main(stdscr):
    #Cache le curseur c'est plus beau cm ça
    curses.curs_set(0)
    #Réintalise l'affichage
    stdscr.clear()

    #Initialisation de toutes nos variables
    taille = 10
    niveau = 1
    nb_objet = 4
    proportion_chemins = 0.9
    labyrinthe = creer_labyrinthe(taille, proportion_chemins)
    joueur = creer_joueur()
    dico_affichage = {0: '_', 1: '■', 2: 'S', 3: 'E'}
    objets = cree_objets(labyrinthe, nb_objet)
    objets_collectes = 0
    debut = time.time()
    temps_limite = 60

    #Boucle principale
    while True:
        #Réintalise l'affichage à chaque nouvelle utilisation de la boucle
        stdscr.clear()
        #Affiche labyrinthe
        afficher_labyrinthe_avec_joueur_et_objets(stdscr, labyrinthe, dico_affichage, joueur, objets)

        #Affiche le niveau + utilisation du f-string pour l'afficher
        stdscr.addstr(len(labyrinthe) + 2, 0, f"Niveau : {niveau}")
        stdscr.addstr(len(labyrinthe) + 3, 0, f"Objets collectés : {objets_collectes}/{len(objets) + objets_collectes}")

        #Affiche le temps restant
        chronometre(stdscr, temps_limite, debut, labyrinthe)
        stdscr.addstr(len(labyrinthe) + 4, 0, \
                        "Si aucune solution possible, appuyez sur r pour régénérer un nouveau labyrinthe")
        #Méthode qui va afficher concretement les addstr qu'on utilise précédemment
        stdscr.refresh()
        
        #Récupération de la direction (touche que va appuyer l'utilisateur)
        letter = stdscr.getkey()

        if letter == 'r':
            labyrinthe = creer_labyrinthe(taille, proportion_chemins)  #Nv labyrinthe
            joueur = creer_joueur()  #Remet le joueur à l'entrée
            objets = cree_objets(labyrinthe, nb_objet)  #Nvx objets
            objets_collectes = 0  #Remet à 0 le nb d'obj collectés
            debut = time.time() #Remet à 0 le chrono
            continue  #Continue vers la suite de la boucle

        #Maj de la position du joueur
        update_p(stdscr, letter, joueur, labyrinthe)
        #Condition que le joueur ramasse un objet
        if ramasser_objets(stdscr, joueur, objets):
            #Augmente le nb d'objet collectés
            objets_collectes += 1

        #Condition que le joueur atteigne la sortie et qu'il est ramassé ts les objets
        if labyrinthe[joueur["x"]][joueur["y"]] == 2 and len(objets) == 0:
            #Affichage message de réussite et passage niveau suivant
            stdscr.addstr(len(labyrinthe) + 3, 0, "Niveau terminé ! Appuyez sur une touche.")
            stdscr.refresh()
            stdscr.getch()

            #Création du niveau suivant
            labyrinthe, proportion_chemins, joueur, objets, taille, niveau, nb_objet = \
                mode_infini(taille, proportion_chemins, niveau, nb_objet)
            #Remet le chrono à 0 pour pas continuer sur l'ancien
            debut = time.time()
            #Reinitisalise les obj collectés
            objets_collectes = 0
        #Sinon si le joueur atteint la sortie mais sans avoir ramasser ts les objets
        elif labyrinthe[joueur["x"]][joueur["y"]] == 2 and len(objets) != 0:
            stdscr.addstr(len(labyrinthe) + 3, 0, "Vous devez d'abord ramasser tous les objets.")
            stdscr.refresh()
            # Pause pour laisser le temps de lire le message
            curses.napms(500)

        #Condition que le chronomètre soit écoulé
        if chronometre(stdscr, temps_limite, debut, labyrinthe):
            stdscr.addstr(len(labyrinthe) + 6, 0, "Finito ! Reprend depuis l'entrée")
            stdscr.refresh()
            #Tps d'arrêt pour afficher le mess
            curses.napms(2000)
            #Remet le joueur à l'entrée
            joueur = creer_joueur()
            #Remet tous les objets 
            objets = cree_objets(labyrinthe, nb_objet)
            #Remet à 0 le compteur d'objet
            objets_collectes = 0
            #Recommence le chrono
            debut = time.time()


# Appel la fonction principale
curses.wrapper(main)