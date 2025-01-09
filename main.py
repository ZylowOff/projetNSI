import pygame
import random
import sys

# Initialisation de Pygame
pygame.init()


# Dimensions de la fenêtre
LARGEUR = 800
HAUTEUR = 600
TAILLE_CASE = 50

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
GRIS = (200, 200, 200)
JOUEUR = (41, 27, 14)
SORTIE = (255, 255, 255)
MUR = (26, 0, 8)
SOL = (115, 109, 115)

# Création de la fenêtre
fenetre = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Hôpital Abandonné")

# Horloge pour contrôler le FPS
horloge = pygame.time.Clock()


# Génération d'un labyrinthe aléatoire
# Génération d'un labyrinthe avec des couloirs larges
def generer_hopital(nb_lignes, nb_colonnes):
    # Ajuster les dimensions pour correspondre à des blocs de 3x3
    nb_lignes = (nb_lignes // 3) * 3 + 1
    nb_colonnes = (nb_colonnes // 3) * 3 + 1
    hopital = [["#" for _ in range(nb_colonnes)] for _ in range(nb_lignes)]

    def voisins(x, y):
        directions = [(6, 0), (-6, 0), (0, 6), (0, -6)]
        random.shuffle(directions)
        return [
            (x + dx, y + dy)
            for dx, dy in directions
            if 0 <= x + dx < nb_colonnes and 0 <= y + dy < nb_lignes]


    def creuser(x, y):
        # Creuser un bloc 3x3
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= y + i < nb_lignes and 0 <= x + j < nb_colonnes:
                    hopital[y + i][x + j] = " "


        # Parcourir les voisins
        for nx, ny in voisins(x, y):
            if hopital[ny][nx] == "#":
                # Creuser le couloir de 3x3 vers le voisin
                for i in range(-1, 2):
                    for j in range(-3, 4):
                        if 0 <= (y + ny) // 2 + i < nb_lignes and 0 <= (x + nx) // 2 + j < nb_colonnes:
                            hopital[(y + ny) // 2 + i][(x + nx) // 2 + j] = " "


                # Creuser le voisin
                creuser(nx, ny)


    # Point de départ (centre)
    creuser(nb_colonnes // 2, nb_lignes // 2)


    # Ajouter des culs-de-sac pour tromper l'utilisateur
    for _ in range(nb_lignes * nb_colonnes // 10):
        x, y = random.randint(1, nb_colonnes - 2), random.randint(1, nb_lignes - 2)
        if hopital[y][x] == " ":
            nx, ny = random.choice(voisins(x, y))
            if 0 <= nx < nb_colonnes and 0 <= ny < nb_lignes and hopital[ny][nx] == "#":
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= ny + i < nb_lignes and 0 <= nx + j < nb_colonnes:
                            hopital[ny + i][nx + j] = " "


    # Positionner la sortie aléatoirement dans un des coins atteignables
    coins = [(0, 0), (0, nb_colonnes - 1), (nb_lignes - 1, 0), (nb_lignes - 1, nb_colonnes - 1)]
    random.shuffle(coins)


    for sortie_y, sortie_x in coins:
        if hopital[sortie_y][sortie_x] == " ":
            hopital[sortie_y][sortie_x] = "S"
            break


    return hopital




# Dessin de l'hôpital
def dessiner_hopital(hopital, joueur_pos, camera_offset):
    fenetre.fill(NOIR)
    joueur_x, joueur_y = joueur_pos
    for i, ligne in enumerate(hopital):
        for j, case in enumerate(ligne):
            distance_x = abs(j - joueur_x)
            distance_y = abs(i - joueur_y)

            # Limiter la visibilité avec une zone élargie
            if distance_x <= 4 and distance_y <= 4:
                x = j * TAILLE_CASE - camera_offset[0]
                y = i * TAILLE_CASE - camera_offset[1]
                if 0 <= x < LARGEUR and 0 <= y < HAUTEUR:
                    if case == "#":
                        pygame.draw.rect(fenetre, MUR, (x, y, TAILLE_CASE, TAILLE_CASE))
                    elif case == "S":
                        pygame.draw.rect(fenetre, SORTIE, (x, y, TAILLE_CASE, TAILLE_CASE))
                    elif case == " ":
                        pygame.draw.rect(fenetre, SOL, (x, y, TAILLE_CASE, TAILLE_CASE))

    # Dessiner le joueur
    joueur_ecran_x = joueur_x * TAILLE_CASE - camera_offset[0]
    joueur_ecran_y = joueur_y * TAILLE_CASE - camera_offset[1]
    pygame.draw.rect(fenetre, JOUEUR, (joueur_ecran_x, joueur_ecran_y, TAILLE_CASE, TAILLE_CASE))

# Vérification si le joueur clique sur un bouton
def bouton_clique(rect, pos):
    return rect.collidepoint(pos)



# Vérification de la validité du déplacement
def deplacement_valide(hopital, pos):
    x, y = pos
    if 0 <= x < len(hopital[0]) and 0 <= y < len(hopital):
        return hopital[y][x] != "#"
    return False



# Fonction d'affichage de victoire
def afficher_victoire():
    fenetre.fill(NOIR)
    texte = pygame.font.Font(None, 60).render("Victoire !", True, BLANC)
    texte_rect = texte.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    pygame.time.delay(3000)  # Attendre 3 secondes



# Menu principal
def menu_principal():
    bouton_jouer = pygame.Rect((LARGEUR // 2 - 100, HAUTEUR // 2 - 50), (200, 100))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_clique(bouton_jouer, event.pos):
                    return  # Commence le jeu

        # Dessiner le menu
        fenetre.fill(NOIR)
        pygame.draw.rect(fenetre, GRIS, bouton_jouer)
        texte = pygame.font.Font(None, 50).render("Jouer", True, BLANC)
        texte_rect = texte.get_rect(center=bouton_jouer.center)
        fenetre.blit(texte, texte_rect)


        pygame.display.flip()
        horloge.tick(60)


# Menu pause
def menu_pause():
    bouton_continuer = pygame.Rect((LARGEUR // 2 - 100, HAUTEUR // 2 - 150), (200, 75))
    bouton_recommencer = pygame.Rect((LARGEUR // 2 - 100, HAUTEUR // 2 - 50), (200, 75))
    bouton_quitter = pygame.Rect((LARGEUR // 2 - 100, HAUTEUR // 2 + 50), (200, 75))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_clique(bouton_continuer, event.pos):
                    return "CONTINUER"
                elif bouton_clique(bouton_recommencer, event.pos):

                    return "RECOMMENCER"

                elif bouton_clique(bouton_quitter, event.pos):

                    pygame.quit()

                    sys.exit()



        # Dessiner le menu pause

        fenetre.fill(NOIR)



        # Dessiner les boutons

        pygame.draw.rect(fenetre, GRIS, bouton_continuer)

        pygame.draw.rect(fenetre, GRIS, bouton_recommencer)

        pygame.draw.rect(fenetre, GRIS, bouton_quitter)



        # Ajouter les textes

        texte_continuer = pygame.font.Font(None, 40).render("Continuer", True, BLANC)

        texte_recommencer = pygame.font.Font(None, 35).render("Recommencer", True, BLANC)  # Taille réduite

        texte_quitter = pygame.font.Font(None, 40).render("Quitter", True, BLANC)



        fenetre.blit(texte_continuer, texte_continuer.get_rect(center=bouton_continuer.center))

        fenetre.blit(texte_recommencer, texte_recommencer.get_rect(center=bouton_recommencer.center))

        fenetre.blit(texte_quitter, texte_quitter.get_rect(center=bouton_quitter.center))



        pygame.display.flip()

        horloge.tick(60)





# Dimensions de l'hôpital

NB_LIGNES = (HAUTEUR // TAILLE_CASE) * 4

NB_COLONNES = (LARGEUR // TAILLE_CASE) * 4



# Génération initiale de l'hôpital

hopital = generer_hopital(NB_LIGNES, NB_COLONNES)



# Position initiale du joueur (au centre)

joueur_pos = [NB_COLONNES // 2, NB_LIGNES // 2]



# Offset de la caméra

camera_offset = [0, 0]



# Vitesse de déplacement

vitesse_deplacement = 10

compteur_deplacement = 10



# Afficher le menu principal avant de commencer le jeu

menu_principal()



# Boucle principale

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:

            action = menu_pause()

            if action == "RECOMMENCER":

                joueur_pos = [NB_COLONNES // 2, NB_LIGNES // 2]

                hopital = generer_hopital(NB_LIGNES, NB_COLONNES)



    # Gestion des touches

    touches = pygame.key.get_pressed()

    nouvelle_pos = joueur_pos[:]

    if compteur_deplacement == 0:

        if touches[pygame.K_UP] or touches[pygame.K_z]:

            nouvelle_pos[1] -= 1

        elif touches[pygame.K_DOWN] or touches[pygame.K_s]:

            nouvelle_pos[1] += 1

        elif touches[pygame.K_LEFT] or touches[pygame.K_q]:

            nouvelle_pos[0] -= 1

        elif touches[pygame.K_RIGHT] or touches[pygame.K_d]:

            nouvelle_pos[0] += 1



        if deplacement_valide(hopital, nouvelle_pos):

            joueur_pos = nouvelle_pos



        compteur_deplacement = vitesse_deplacement



    if compteur_deplacement > 0:

        compteur_deplacement -= 1



    # Vérifier si le joueur a atteint la sortie

    if hopital[joueur_pos[1]][joueur_pos[0]] == "S":

        afficher_victoire()

        running = False  # Terminer le jeu



    # Mise à jour de la caméra

    camera_offset[0] = joueur_pos[0] * TAILLE_CASE - LARGEUR // 2

    camera_offset[1] = joueur_pos[1] * TAILLE_CASE - HAUTEUR // 2



    # Dessiner le jeu

    dessiner_hopital(hopital, joueur_pos, camera_offset)



    pygame.display.flip()

    horloge.tick(120)



pygame.quit()
