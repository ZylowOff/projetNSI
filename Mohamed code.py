import pygame
import random
import sys
import math
import os

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()  # Initialiser le module de mixage

# Dimensions de la fenêtre
largeur = 1920  # Largeur de la fenêtre
hauteur = 1080  # Hauteur de la fenêtre
taille_case = 50  # Taille d'une case dans le labyrinthe

# Couleurs utilisées dans le jeu
noir = (0, 0, 0)
blanc = (255, 255, 255)
gris = (200, 200, 200)
gris_fonce = (50, 50, 50)
sortie = (0, 255, 0)
mur = (100, 40, 30)
sol = (115, 109, 115)
cle = (255, 223, 0)
ennemis = (255, 0, 0)
bordeaux = (40, 0, 0)

# Fichiers utilisés dans le jeu
joueur_img = pygame.image.load("./assets/characters/personnage.png")
joueur = pygame.transform.scale(joueur_img, (taille_case * 1.25, taille_case * 1.25))
son_menu = "./assets/music/S.T.A.L.K.E.R..mp3"
son_fond = "./assets/music/Amnesia-02.mp3"
font_helpme = "./assets/font/HelpMe.ttf"
font_november = "./assets/font/November.ttf"
font_arrows = "./assets/font/Arrows.ttf"
fond_1 = "./assets/background/background_1.png"
fond_2 = "./assets/background/background_2.png"
fond_3 = "./assets/background/background_3.png"
fond_4 = "./assets/background/background_4.png"
fond_5 = "./assets/background/background_5.png"
# icone = pygame.image.load('icon.png')
nom = "Echoes of the Hollow"

plein_ecran = True

# Création de la fenêtre
fenetre = pygame.display.set_mode(
    (largeur, hauteur), pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE
)
pygame.display.set_caption(nom)
# pygame.display.set_icon(icone)

# Horloge pour contrôler les FPS
horloge = pygame.time.Clock()

# Paramètres de jeu
nombre_cles = 3
cles_collectees = 0
nombre_ennemis = 3
vitesse_ennemis = 0.4
delai_mouvement = 35
dernier_mouvement = 0

# Paramètres de la vision
cone_angle = 60
cone_longueur = 600
rayon_vision_proche = 100

# Paramètres du réticule
tailles_reticule = [3, 5, 7, 10]
types_reticule = ["Croix", "Point", "Aucun"]
index_taille_reticule = 1
index_type_reticule = 0
epaisseur_reticule = [1, 2, 3, 4, 5]
index_epaisseur_reticule = 3

# Génération initiale
nombre_lignes = (hauteur // taille_case) * 8
nombre_colonnes = (largeur // taille_case) * 8
joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
camera_offset = [0, 0]

# Initialisation de l'angle de vue avec une valeur par défaut
angle_de_vue = 270  # 0 = droite, 90 = bas, 180 = gauche, 270 = haut

# Stocker les ennemis avec leurs positions et directions
ennemis = []

# Suivris de l'index de la case sélectionnée
index_case_selectionnee = 0

# Différentes résolutions
resolutions = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1920, 1080),
    (2560, 1440),
    (largeur, hauteur),  # Résolution native
]
resolution_index = 0 

largeur_base = 1920
hauteur_base = 1080

montrer_fps = False

volume = 0.5

# Paramètres d'endurance
endurance_max = 100
endurance_actuelle = endurance_max
taux_diminution = 0.5
taux_recuperation = 0.2
delai_mouvement_normal = 100
delai_mouvement_rapide = 40


class Ennemi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.compteur_deplacement = 0
        self.cone_vision = 8
        self.angle_vision = 120
        self.vitesse_normale = vitesse_ennemis
        self.vitesse_lente = vitesse_ennemis * 0.3
        self.vitesse_actuelle = self.vitesse_lente
        self.derniere_pos_joueur = None
        self.temps_memoire = 0
        self.duree_memoire_max = 180

    def peut_voir_joueur(self, joueur_pos, jeu):
        # Calculer la distance entre l'ennemi et le joueur
        dx = joueur_pos[0] - self.x
        dy = joueur_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > self.cone_vision:
            return False

        # Vérification de la ligne de vue (pas d'obstacles)
        x, y = self.x, self.y
        pas = 0.1
        longueur = math.sqrt(dx * dx + dy * dy)
        if longueur > 0:
            dx, dy = dx / longueur, dy / longueur
            for i in range(int(longueur / pas)):
                x += dx * pas
                y += dy * pas
                if jeu[int(y)][int(x)] == "#":
                    return False
        return True


def initialiser_ennemis(jeu, nombre_ennemis):
    ennemis = []
    cases_vides = [
        (j, i)
        for i, ligne in enumerate(jeu)
        for j, case in enumerate(ligne)
        if case == " "
    ]

    for _ in range(nombre_ennemis):
        if cases_vides:
            x, y = random.choice(cases_vides)
            ennemis.append(Ennemi(x, y))
            cases_vides.remove((x, y))
    return ennemis


def deplacer_ennemis(jeu, ennemis, joueur_pos):
    for ennemi in ennemis:
        voit_joueur = ennemi.peut_voir_joueur(joueur_pos, jeu)

        if voit_joueur:
            # Mettre à jour la dernière position connue du joueur
            ennemi.derniere_pos_joueur = joueur_pos[:]
            ennemi.temps_memoire = ennemi.duree_memoire_max
            ennemi.vitesse_actuelle = ennemi.vitesse_normale
        elif ennemi.temps_memoire > 0:
            # L'ennemi ne voit plus le joueur mais se souvient de sa position
            ennemi.temps_memoire -= 1
            ennemi.vitesse_actuelle = ennemi.vitesse_normale * 0.7
        else:
            # L'ennemi a complètement perdu la trace du joueur
            ennemi.derniere_pos_joueur = None
            ennemi.vitesse_actuelle = ennemi.vitesse_lente

        ennemi.compteur_deplacement += ennemi.vitesse_actuelle
        if ennemi.compteur_deplacement >= 1:
            ennemi.compteur_deplacement = 0

            if voit_joueur:
                cible = joueur_pos
            elif ennemi.derniere_pos_joueur is not None and ennemi.temps_memoire > 0:
                cible = ennemi.derniere_pos_joueur
            else:
                continue

            dx = cible[0] - ennemi.x
            dy = cible[1] - ennemi.y

            if abs(dx) > abs(dy):
                nouveau_x = ennemi.x + (1 if dx > 0 else -1)
                nouveau_y = ennemi.y
                if not deplacement_valide(jeu, [nouveau_x, nouveau_y]):
                    nouveau_x = ennemi.x
                    nouveau_y = ennemi.y + (1 if dy > 0 else -1)
            else:
                nouveau_y = ennemi.y + (1 if dy > 0 else -1)
                nouveau_x = ennemi.x
                if not deplacement_valide(jeu, [nouveau_x, nouveau_y]):
                    nouveau_x = ennemi.x + (1 if dx > 0 else -1)
                    nouveau_y = ennemi.y

            # Si l'ennemi atteint la dernière position connue et ne voit pas le joueur
            if not voit_joueur and ennemi.derniere_pos_joueur:
                if (
                    abs(ennemi.x - ennemi.derniere_pos_joueur[0]) <= 1
                    and abs(ennemi.y - ennemi.derniere_pos_joueur[1]) <= 1
                ):
                    ennemi.temps_memoire = 0  # Arrêter la poursuite
                    ennemi.derniere_pos_joueur = None
            else:
                # Comportement aléatoire plus lent
                if random.random() < 0.05:
                    ennemi.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

            if deplacement_valide(jeu, [nouveau_x, nouveau_y]):
                ennemi.x = nouveau_x
                ennemi.y = nouveau_y
            else:
                ennemi.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])


def verifier_collision_ennemis(joueur_pos, ennemis):
    for ennemi in ennemis:
        if abs(joueur_pos[0] - ennemi.x) < 1 and abs(joueur_pos[1] - ennemi.y) < 1:
            return True
    return False


def game_over():
    arreter_musique()
    musique_menu()
    fenetre.fill(noir)
    texte = pygame.font.Font(None, 60).render("Game Over!", True, blanc)
    texte_rect = texte.get_rect(center=(largeur // 2, hauteur // 2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    pygame.time.delay(2000) # En millisecondes
    return "menu"


def appliquer_masque_vision(surface, position, angle, length):
    masque = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    masque.fill((0, 0, 0, 200))  # Masque noir semi-transparent

    x, y = position
    start_angle = math.radians(angle - cone_angle / 2)
    end_angle = math.radians(angle + cone_angle / 2)

    points = [(x, y)]  # Point de départ (position du joueur)

    steps = 180
    for i in range(steps + 1):
        theta = start_angle + i * (end_angle - start_angle) / steps

        # Lancer un rayon
        for dist in range(0, int(length), 2):
            ray_x = x + dist * math.cos(theta)
            ray_y = y + dist * math.sin(theta)

            # Convertir en coordonnées de grille
            grille_x = int((ray_x + camera_offset[0]) / taille_case)
            grille_y = int((ray_y + camera_offset[1]) / taille_case)

            # Vérifier si on touche un mur
            if (
                0 <= grille_y < len(jeu)
                and 0 <= grille_x < len(jeu[0])
                and jeu[grille_y][grille_x] == "#"
            ):
                points.append((ray_x, ray_y))
                break
            elif dist >= length - 2:
                points.append((ray_x, ray_y))

    # Dessiner le polygone de vision du cône
    if len(points) > 2:
        pygame.draw.polygon(masque, (0, 0, 0, 0), points)

    # Ajouter le cercle de vision proche
    pygame.draw.circle(masque, (0, 0, 0, 0), (int(x), int(y)), rayon_vision_proche)

    # Appliquer le masque sur l'écran
    surface.blit(masque, (0, 0))


def generer_jeu(nb_lignes, nb_colonnes):
    # Ajuste les dimensions pour garantir un labyrinthe valide
    nb_lignes = (nb_lignes // 3) * 3 + 1
    nb_colonnes = (nb_colonnes // 3) * 3 + 1
    jeu = [["#" for _ in range(nb_colonnes)] for _ in range(nb_lignes)]

    def voisins(x, y):
        directions = [(6, 0), (-6, 0), (0, 6), (0, -6)]
        # Mélange pour générer des labyrinthes variés
        random.shuffle(directions)
        return [
            (x + dx, y + dy)
            for dx, dy in directions
            if 0 <= x + dx < nb_colonnes and 0 <= y + dy < nb_lignes
        ]

    def départ(x, y):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= y + i < nb_lignes and 0 <= x + j < nb_colonnes:
                    jeu[y + i][x + j] = " "
        for nx, ny in voisins(x, y):
            if jeu[ny][nx] == "#":
                for i in range(-1, 2):
                    for j in range(-3, 4):
                        if (
                            0 <= (y + ny) // 2 + i < nb_lignes
                            and 0 <= (x + nx) // 2 + j < nb_colonnes
                        ):
                            jeu[(y + ny) // 2 + i][(x + nx) // 2 + j] = " "
                départ(nx, ny)

    # Commencer au centre du labyrinthe
    départ(nb_colonnes // 2, nb_lignes // 2)

    # Ajoute une sortie sur un bord aléatoire
    bords = [
        (0, random.randint(1, nb_colonnes - 2)),
        (nb_lignes - 1, random.randint(1, nb_colonnes - 2)),
        (random.randint(1, nb_lignes - 2), 0),
        (random.randint(1, nb_lignes - 2), nb_colonnes - 1),
    ]
    random.shuffle(bords)
    for sortie_y, sortie_x in bords:
        if jeu[sortie_y][sortie_x] == " ":
            jeu[sortie_y][sortie_x] = "S"
            break

    return jeu


# Fonction pour placer les clés dans le labyrinthe
def placer_cles(jeu, nombre_cles):
    cles = []
    cases_vides = [
        (i, j)
        for i, ligne in enumerate(jeu)
        for j, case in enumerate(ligne)
        if case == " "
    ]
    for _ in range(nombre_cles):
        x, y = random.choice(cases_vides)
        cles.append((x, y))
        jeu[x][y] = "C"  # Ajoute une clé à cet emplacement
        cases_vides.remove((x, y))
    return cles


def est_dans_cone(joueur_pos, case_pos, angle, length):
    dx = case_pos[0] - joueur_pos[0]
    dy = case_pos[1] - joueur_pos[1]
    distance = dx * dx + dy * dy

    if distance > (length / taille_case) * (length / taille_case):
        return False

    angle = angle % 360
    angle_case = math.degrees(math.atan2(dy, dx)) % 360
    diff_angle = (angle_case - angle + 180) % 360 - 180

    return abs(diff_angle) <= cone_angle / 2


def est_visible(joueur_pos, case_pos, jeu):
    '''Vérifie si une case est visible (dans le cône ou le cercle proche, et pas de mur entre)'''
    joueur_x, joueur_y = joueur_pos
    case_x, case_y = case_pos

    # Calculer la distance entre le joueur et la case
    dx = case_x - joueur_x
    dy = case_y - joueur_y
    distance = math.sqrt(dx * dx + dy * dy)

    # Vérifier si la case est dans le cercle de vision proche
    if distance * taille_case <= rayon_vision_proche:
        # Vérifier s'il n'y a pas de mur entre le joueur et la case
        return not a_mur_entre(joueur_pos, case_pos, jeu)

    # Sinon, vérifier si c'est dans le cône de vision
    if not est_dans_cone(joueur_pos, case_pos, angle_de_vue, cone_longueur):
        return False

    # Vérifier s'il n'y a pas de mur entre le joueur et la case
    return not a_mur_entre(joueur_pos, case_pos, jeu)


def a_mur_entre(joueur_pos, case_pos, jeu):
    x1, y1 = joueur_pos
    x2, y2 = case_pos

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    x = int(x1)
    y = int(y1)

    if dx > dy:
        err = dx / 2.0
        while x != int(x2):
            err -= dy
            if err < 0:
                y += 1 if y2 > y1 else -1
                err += dx
            x += 1 if x2 > x1 else -1
            if jeu[y][x] == "#":
                return True
    else:
        err = dy / 2.0
        while y != int(y2):
            err -= dx
            if err < 0:
                x += 1 if x2 > x1 else -1
                err += dy
            y += 1 if y2 > y1 else -1
            if jeu[y][x] == "#":
                return True

    return False


def dessiner_jeu(jeu, joueur_pos, camera_offset):
    # Surface virtuelle pour le rendu de base
    surface_virtuelle = pygame.Surface((largeur_base, hauteur_base))
    surface_virtuelle.fill(noir)

    # Calculer les limites visibles avec une marge
    marge = 2
    debut_x = max(0, int(camera_offset[0] // taille_case) - marge)
    debut_y = max(0, int(camera_offset[1] // taille_case) - marge)
    fin_x = min(
        len(jeu[0]), int((camera_offset[0] + largeur) // taille_case) + marge
    )
    fin_y = min(len(jeu), int((camera_offset[1] + hauteur) // taille_case) + marge)

    # Pré-calculer les offsets de caméra
    cam_x = camera_offset[0]
    cam_y = camera_offset[1]

    # Surface temporaire pour le rendu de base
    temp_surface = pygame.Surface((largeur, hauteur))
    temp_surface.fill(noir)

    # Rendu de base (murs et sol)
    for i in range(debut_y, fin_y):
        y = i * taille_case - cam_y
        for j in range(debut_x, fin_x):
            x = j * taille_case - cam_x
            if jeu[i][j] == "#":
                pygame.draw.rect(temp_surface, mur, (x, y, taille_case, taille_case))
            else:
                pygame.draw.rect(temp_surface, sol, (x, y, taille_case, taille_case))

    surface_virtuelle.blit(temp_surface, (0, 0))

    # Appliquer le masque de vision
    joueur_centre = (
        joueur_pos[0] * taille_case - cam_x + taille_case // 2,
        joueur_pos[1] * taille_case - cam_y + taille_case // 2,
    )
    appliquer_masque_vision(
        surface_virtuelle, joueur_centre, angle_de_vue, cone_longueur
    )

    # Rendu des objets spéciaux
    for i in range(debut_y, fin_y):
        y = i * taille_case - cam_y
        for j in range(debut_x, fin_x):
            case = jeu[i][j]
            if case in ["S", "C"]:
                if est_visible(joueur_pos, (j, i), jeu):
                    x = j * taille_case - cam_x
                    couleur = sortie if case == "S" else cle
                    pygame.draw.rect(
                        surface_virtuelle, couleur, (x, y, taille_case, taille_case)
                    )

    # Calculer le centre du joueur
    joueur_x = (
        joueur_pos[0] * taille_case
        - camera_offset[0]
        - (joueur.get_width() - taille_case) // 2
    )
    joueur_y = (
        joueur_pos[1] * taille_case
        - camera_offset[1]
        - (joueur.get_height() - taille_case) // 2
    )

    # Tourner l'image du joueur pour suive la souris et convertit l'angle de vue pour correspondre à la rotation de Pygame (0° est en haut, dans le sens horaire)
    rotation_angle = -(angle_de_vue + 90)
    joueur_rotated = pygame.transform.rotate(joueur, rotation_angle)

    # Calculer la position du joueur après rotation
    joueur_x -= (joueur_rotated.get_width() - joueur.get_width()) // 2
    joueur_y -= (joueur_rotated.get_height() - joueur.get_height()) // 2

    surface_virtuelle.blit(joueur_rotated, (joueur_x, joueur_y))

    # Ajuster la taille de la surface virtuelle à la taille de la fenêtre
    scaled_surface = pygame.transform.scale(surface_virtuelle, (largeur, hauteur))
    fenetre.blit(scaled_surface, (0, 0))


# Vérification de la validité du déplacement
def deplacement_valide(jeu, pos):
    x, y = pos
    if 0 <= y < len(jeu) and 0 <= x < len(jeu[0]):
        return jeu[y][x] != "#"
    return False


# Menu de victoire
def afficher_victoire():
    arreter_musique()
    fenetre.fill(noir)
    texte = pygame.font.Font(None, 60).render("Victoire !", True, blanc)
    texte_rect = texte.get_rect(center=(largeur // 2, hauteur // 2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    pygame.time.delay(3000)


# Menu des crédits
def afficher_credits():
    # Variables pour les crédits
    vitesse_scroll = 5
    taille_titre = 100
    taille_nom = 80
    taille_roles = 50
    espacement = 120
    espacement_2 = 30
    espacement_3 = 200

    # Contenu des crédits avec les rôles
    credits_data = [
        ("Développeurs :", taille_titre),
        ("", espacement_3),
        ("Iaroslav Lushcheko", taille_nom),
        ("", espacement_2),
        ("Chef de projet, Méchaniques du jeu", taille_roles),
        ("", espacement),
        ("Eliott Raulet", taille_nom),
        ("", espacement_2),
        ("Génération du niveau, Méchaniques du jeu", taille_roles),
        ("", espacement),
        ("Ugo Guillemart", taille_nom),
        ("", espacement_2),
        ("Graphismes, Génération du niveau", taille_roles),
        ("", espacement),
        ("Mohamed El Mekkawy", taille_nom),
        ("", espacement_2),
        ("Paramètres, Customisation, Divers", taille_roles),      
        ("", espacement_3),
    ]

    # Calculer la longueur totale pour le défilement
    total_height = sum([size if text == "" else 80 for text, size in credits_data])
    y_offset = float(hauteur)

    while True:
        fenetre.fill(noir)

        current_y = int(y_offset)

        # Dessiner le texte des crédits
        for text, size in credits_data:
            if text:
                texte = pygame.font.Font(font_helpme, size).render(text, True, blanc)
                texte_rect = texte.get_rect(center=(largeur // 2, current_y))

                if -50 <= current_y <= hauteur + 50:
                    if size == taille_titre:
                        glow = pygame.font.Font(font_helpme, size).render(
                            text, True, (100, 100, 100)
                        )
                        glow_rect = glow.get_rect(center=(largeur // 2, current_y))
                        fenetre.blit(glow, (glow_rect.x + 2, glow_rect.y + 2))

            fenetre.blit(texte, texte_rect)

            current_y += size if text == "" else 80

        # Gérer les différents événements pour quitter les crédits
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        # Scroll automatique
        y_offset -= vitesse_scroll

        if y_offset < -total_height:
            y_offset = float(hauteur)

        pygame.display.flip()
        horloge.tick(60)


def bords_arrondis(surface, couleur, rect, radius):
    '''Dessine un rectangle avec des bords arrondis'''
    x, y, width, height = rect

    # Dessiner des cercles remplis pour les coins
    pygame.draw.circle(surface, couleur, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, couleur, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, couleur, (x + radius, y + height - radius), radius)
    pygame.draw.circle(
        surface, couleur, (x + width - radius, y + height - radius), radius
    )

    # Dessiner des rectangles pour remplir la surface
    pygame.draw.rect(surface, couleur, (x + radius, y, width - 2 * radius, height))
    pygame.draw.rect(surface, couleur, (x, y + radius, width, height - 2 * radius))


def draw_button(surface, rect, text, font, hover_couleur, default_couleur, text_couleur, border_radius=15, icon_text=None, icon_font=None):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_x, mouse_y):
        couleur = hover_couleur
        rect = rect.inflate(20, 20)
    else:
        couleur = default_couleur

    bords_arrondis(surface, couleur, rect, border_radius)
    
    if icon_text and icon_font:
        icon_surface = icon_font.render(icon_text, True, text_couleur)
        surface.blit(
            icon_surface,
            (
                rect.left + 10,
                rect.centery - icon_surface.get_height() // 2,
            ),
        )
        text_surface = font.render(text, True, text_couleur)
        surface.blit(
            text_surface,
            (
                rect.left + 40,
                rect.centery - text_surface.get_height() // 2,
            ),
        )
    else:
        text_surface = font.render(text, True, text_couleur)
        surface.blit(
            text_surface,
            (
                rect.centerx - text_surface.get_width() // 2,
                rect.centery - text_surface.get_height() // 2,
            ),
        )


def handle_event(event, boutons):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:
        for bouton, texte, _ in boutons:
            if bouton.collidepoint(event.pos):
                if texte == "Nouvelle Partie":
                    pygame.mouse.set_visible(False)
                    return "nouvelle_partie"
                elif texte == "Paramètres":
                    afficher_parametres()
                elif texte == "Crédits":
                    afficher_credits()
                elif texte == "Quitter":
                    pygame.quit()
                    sys.exit()
                elif texte == "Continuer":
                    pygame.mouse.set_visible(False)
                    return "continuer"
                elif texte == "Recommencer":
                    return "recommencer"
                elif texte == "Menu Principal":
                    return "menu"
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return "escape"

def afficher_menu():
    global cles_collectees, sprays_collectes, bandages_collectes, endurance_actuelle

    # Réinitialiser l'inventaire
    cles_collectees = 0
    sprays_collectes = 0
    bandages_collectes = 0
    endurance_actuelle = endurance_max

    pygame.mouse.set_visible(True)
    musique_menu()

    # Charger les différentes couches du fond
    couches_fond = [
        pygame.image.load(fond_1),
        pygame.image.load(fond_2),
        pygame.image.load(fond_3),
        pygame.image.load(fond_4),
        pygame.image.load(fond_5),
    ]

    facteur_echelle = 1.3
    echelle_largeur = int(largeur * facteur_echelle)
    echelle_hauteur = int(hauteur * facteur_echelle)
    couches_fond = [
        pygame.transform.scale(couche, (echelle_largeur, echelle_hauteur))
        for couche in couches_fond
    ]

    # Facteurs de parallaxe pour plus de mouvement
    facteurs_parralaxe = [0.02, 0.04, 0.08, 0.12, 0.16]
    decalage_x_initial = -150

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        center_x = largeur / 2
        center_y = hauteur / 2
        rel_x = (mouse_x - center_x) / (
            center_x * 0.7
        )
        rel_y = (mouse_y - center_y) / (center_y * 0.7)

        for i, layer in enumerate(couches_fond):
            decalage_x = decalage_x_initial - rel_x * facteurs_parralaxe[i] * (
                echelle_largeur - largeur
            )
            decalage_y = -rel_y * facteurs_parralaxe[i] * (echelle_hauteur - hauteur)

            fenetre.blit(layer, (decalage_x, decalage_y))

        titre = pygame.font.Font(font_november, 150).render(nom, True, blanc)
        titre_rect = titre.get_rect(center=(largeur // 2, hauteur // 6))
        fenetre.blit(titre, titre_rect)

        espace_boutton = 120
        y_depart = hauteur // 3
        boutons = [
            (
                pygame.Rect(largeur // 2 - 250, y_depart, 500, 90),
                "Nouvelle Partie",
                40
            ),
            (
                pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton, 500, 90),
                "Paramètres",
                40,
            ),
            (
                pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 2, 500, 90),
                "Crédits",
                40,
            ),
            (
                pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 3, 500, 90),
                "Quitter",
                40,
            ),
        ]

        for bouton, texte, taille_texte in boutons:
            draw_button(fenetre, bouton, texte, pygame.font.Font(font_helpme, taille_texte), (255, 0, 0), bordeaux, blanc)

        pygame.display.flip()

        for event in pygame.event.get():
            result = handle_event(event, boutons)
            if result == "nouvelle_partie":
                return

def afficher_menu_pause():
    pygame.mouse.set_visible(True)
    global resolution_index, largeur, hauteur, fenetre

    # Charger l'image de fond
    fond = pygame.image.load(fond_1)
    fond = pygame.transform.scale(fond, (largeur, hauteur))

    while True:
        fenetre.blit(fond, (0, 0))

        titre = pygame.font.Font(font_november, 100).render(nom, True, blanc)
        titre_rect = titre.get_rect(center=(largeur // 2, hauteur // 6))
        fenetre.blit(titre, titre_rect)

        # Centrer les boutons
        espace_boutton = 120
        y_depart = hauteur // 3
        boutons = [
            (
                pygame.Rect(largeur // 2 - 250, y_depart, 500, 90),
                "Continuer",
                40
            ),
            (
                pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton, 500, 90),
                "Recommencer",
                40,
            ),
            (
                pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 2, 500, 90),
                "Paramètres",
                40,
            ),
            (
                pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 3, 500, 90),
                "Menu Principal",
                40,
            ),
            (
                pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 4, 500, 90),
                "Quitter",
                40,
            ),
        ]

        for bouton, texte, taille_texte in boutons:
            draw_button(fenetre, bouton, texte, pygame.font.Font(font_helpme, taille_texte), (255, 0, 0), bordeaux, blanc)

        pygame.display.flip()

        for event in pygame.event.get():
            result = handle_event(event, boutons)
            if result in ["continuer", "recommencer", "menu"]:
                return result
            if result == "escape":
                return


# Afficher le compteur de clés
def dessiner_compteur_cles(surface, cles_collectees, nombre_cles_total):
    marge = 20
    taille_icone = 30
    espacement = 10

    fond_rect = pygame.Rect(
        largeur - (marge + taille_icone + 80),
        marge,
        taille_icone + 80,
        taille_icone + 10,
    )
    pygame.draw.rect(surface, bordeaux, fond_rect)
    pygame.draw.rect(surface, blanc, fond_rect, 2)

    # Dessiner l'icône de clé
    icone_cle = pygame.Rect(
        fond_rect.x + 5,
        fond_rect.y + (fond_rect.height - taille_icone) // 2,
        taille_icone,
        taille_icone,
    )
    pygame.draw.rect(surface, cle, icone_cle)

    # Afficher le texte du compteur
    texte = f"{cles_collectees}/{nombre_cles_total}"
    police = pygame.font.Font(None, 36)
    surface_texte = police.render(texte, True, blanc)
    pos_texte_x = icone_cle.right + espacement
    pos_texte_y = fond_rect.y + (fond_rect.height - surface_texte.get_height()) // 2

    surface.blit(surface_texte, (pos_texte_x, pos_texte_y))


# Afficher l'inventaire
def dessiner_inventaire(surface):
    # Variables pour l'inventaire
    inventaire_x = 30
    inventaire_y = hauteur - 70
    case_taille = 50
    espacement = 10
    nombre_cases = 5

    # Dessiner les cases d'inventaire
    for i in range(nombre_cases):
        x = inventaire_x + (case_taille + espacement) * i
        rect = pygame.Rect(x, inventaire_y, case_taille, case_taille)

        # Mettre en surbrillance la case sélectionnée
        if i == index_case_selectionnee:
            pygame.draw.rect(surface, (100, 100, 100), rect)
            pygame.draw.rect(surface, blanc, rect, 3)
        else:
            pygame.draw.rect(surface, (50, 50, 50), rect)
            pygame.draw.rect(surface, gris, rect, 1)


# Afficher les paramètres
def afficher_parametres():
    global resolution_index, largeur, hauteur, fenetre, index_taille_reticule, index_type_reticule, index_epaisseur_reticule, plein_ecran, montrer_fps, volume

    section_choisie = 0  # 0 = Affichage, 1 = Réticule, 2 = Son
    sections = ["Affichage", "Réticule", "Son"]

    slider_rect = pygame.Rect(0, 0, 200, 10)
    slider_pos = tailles_reticule[index_taille_reticule]
    slider_rect_epaisseur = pygame.Rect(0, 0, 200, 10)
    slider_pos_epaisseur = epaisseur_reticule[index_epaisseur_reticule]
    slider_rect_volume = pygame.Rect(0, 0, 200, 10)
    slider_pos_volume = volume * 100
    texte_parametre = str(slider_pos)
    texte_epaisseur = str(slider_pos_epaisseur)
    texte_volume = str(int(slider_pos_volume))
    glisse_slider = False
    glisse_slider_epaisseur = False
    glisse_slider_volume = False

    while True:
        fenetre.fill(noir)
        center_x = largeur // 2

        # Bouton de retour
        bouton_retour = pygame.Rect(20, 20, 200, 60)
        draw_button(fenetre, bouton_retour, " Retour", pygame.font.Font(font_helpme, 30), (255, 0, 0), bordeaux, blanc, icon_text="B", icon_font=pygame.font.Font(font_arrows, 30))

        # Centrer les sections
        section_largeur_totale = sum([200 for _ in sections])
        section_x_debut = (largeur - section_largeur_totale) // 2

        # Afficher les sections
        for i, section in enumerate(sections):
            couleur = blanc if i == section_choisie else gris
            texte = pygame.font.Font(None, 40).render(section, True, couleur)
            texte_rect = texte.get_rect(center=(section_x_debut + i * 200 + 100, 150))
            fenetre.blit(texte, texte_rect)

        # Afficher les paramètres pour la section choisie
        if section_choisie == 0:
            for i, (width, height) in enumerate(resolutions):
                resolution_texte = f"{width} x {height}"
                if plein_ecran:
                    couleur = (100, 100, 100)
                else:
                    couleur = blanc if i == resolution_index else gris
                texte = pygame.font.Font(None, 40).render(resolution_texte, True, couleur)
                texte_rect = texte.get_rect(center=(largeur // 2, 250 + i * 50))
                fenetre.blit(texte, texte_rect)

            # Boutton pour basculer en plein écran
            texte_plein_ecran = "Plein écran: " + ("Oui" if plein_ecran else "Non")
            couleur = blanc if plein_ecran else gris
            texte = pygame.font.Font(None, 40).render(texte_plein_ecran, True, couleur)
            texte_rect = texte.get_rect(
                center=(largeur // 2, 250 + len(resolutions) * 50)
            )
            fenetre.blit(texte, texte_rect)

            # Bouton pour afficher les FPS
            texte_fps = "Afficher les FPS: " + ("Oui" if montrer_fps else "Non")
            couleur = blanc if montrer_fps else gris
            texte = pygame.font.Font(None, 40).render(texte_fps, True, couleur)
            texte_rect = texte.get_rect(
                center=(largeur // 2, 250 + (len(resolutions) + 1) * 50)
            )
            fenetre.blit(texte, texte_rect)

        # Paramètres du réticule
        elif section_choisie == 1:
            center_x = largeur // 2
            apercu_x = center_x

            texte = pygame.font.Font(None, 40).render("Taille:", True, blanc)
            texte_rect = texte.get_rect(center=(center_x - 150, 250))
            fenetre.blit(texte, texte_rect)

            slider_rect.centerx = center_x
            slider_rect.centery = 300
            slider_couleur = (
                (50, 50, 50) if types_reticule[index_type_reticule] == "Aucun" else gris
            )
            pygame.draw.rect(fenetre, slider_couleur, slider_rect)

            handle_pos = slider_rect.left + (slider_pos - 1) * (slider_rect.width / 20)
            if types_reticule[index_type_reticule] != "Aucun":
                pygame.draw.circle(fenetre, blanc, (handle_pos, slider_rect.centery), 8)

            font = pygame.font.Font(None, 40)
            text_surface = font.render(
                texte_parametre,
                True,
                (
                    blanc
                    if types_reticule[index_type_reticule] != "Aucun"
                    else (50, 50, 50)
                ),
            )
            texte_rect = text_surface.get_rect(center=(center_x + 150, 300))
            fenetre.blit(text_surface, texte_rect)

            texte_epaisseur_str = "Épaisseur:"
            texte_epaisseur = pygame.font.Font(None, 40).render(
                texte_epaisseur_str, True, blanc
            )
            texte_epaisseur_rect = texte_epaisseur.get_rect(center=(center_x - 150, 370))
            fenetre.blit(texte_epaisseur, texte_epaisseur_rect)

            slider_rect_epaisseur.centerx = center_x
            slider_rect_epaisseur.centery = 420
            couleur_slider_epaisseur = (
                (50, 50, 50) if types_reticule[index_type_reticule] != "Croix" else gris
            )
            pygame.draw.rect(fenetre, couleur_slider_epaisseur, slider_rect_epaisseur)

            poignee_epaisseur_pos = slider_rect_epaisseur.left + (
                slider_pos_epaisseur - 1
            ) * (slider_rect_epaisseur.width / 4)
            if types_reticule[index_type_reticule] == "Croix":
                pygame.draw.circle(
                    fenetre,
                    blanc,
                    (poignee_epaisseur_pos, slider_rect_epaisseur.centery),
                    8,
                )


            style_text = pygame.font.Font(None, 40).render("Style:", True, blanc)
            style_rect = style_text.get_rect(center=(center_x - 150, 490))
            fenetre.blit(style_text, style_rect)

            for i, style in enumerate(types_reticule):
                couleur = blanc if i == index_type_reticule else gris
                texte = pygame.font.Font(None, 40).render(style, True, couleur)
                texte_rect = texte.get_rect(center=(center_x, 490 + i * 50))
                fenetre.blit(texte, texte_rect)

            # Aperçu du réticule
            apercu_y = 700
            apercu_texte = pygame.font.Font(None, 40).render("Aperçu", True, blanc)
            apercu_texte_rect = apercu_texte.get_rect(center=(center_x, apercu_y - 50))
            fenetre.blit(apercu_texte, apercu_texte_rect)
            apercu_taille = 150
            bords = 10
            rect_exterieur = pygame.Rect(
                apercu_x - apercu_taille // 2 - bords,
                apercu_y - apercu_taille // 2 - bords,
                apercu_taille + bords * 2,
                apercu_taille + bords * 2,
            )
            pygame.draw.rect(fenetre, gris, rect_exterieur)
            apercu_rect = pygame.Rect(
                apercu_x - apercu_taille // 2,
                apercu_y - apercu_taille // 2,
                apercu_taille,
                apercu_taille,
            )
            pygame.draw.rect(fenetre, sol, apercu_rect)
            pygame.draw.rect(fenetre, blanc, apercu_rect, 1)

            # Dessiner l'appercu du réticule
            if types_reticule[index_type_reticule] == "Croix":
                pygame.draw.line(
                    fenetre,
                    blanc,
                    (apercu_x - slider_pos, apercu_y),
                    (apercu_x + slider_pos, apercu_y),
                    int(slider_pos_epaisseur),
                )
                pygame.draw.line(
                    fenetre,
                    blanc,
                    (apercu_x, apercu_y - slider_pos),
                    (apercu_x, apercu_y + slider_pos),
                    int(slider_pos_epaisseur),
                )
            elif types_reticule[index_type_reticule] == "Point":
                pygame.draw.circle(fenetre, blanc, (apercu_x, apercu_y), slider_pos)

        # Paramètres du son
        elif section_choisie == 2:
            center_x = largeur // 2

            # Afficher le texte "Volume" et les paramètres
            texte = pygame.font.Font(None, 40).render("Volume:", True, blanc)
            texte_rect = texte.get_rect(center=(center_x - 150, 250))
            fenetre.blit(texte, texte_rect)

            # Dessiner le slider de volume
            slider_rect_volume.centerx = center_x
            slider_rect_volume.centery = 300
            pygame.draw.rect(fenetre, gris, slider_rect_volume)

            # Dessiner le curseur du slider de volume
            volume_handle_pos = (
                slider_rect_volume.left
                + (slider_pos_volume / 100) * slider_rect_volume.width
            )
            pygame.draw.circle(
                fenetre, blanc, (volume_handle_pos, slider_rect_volume.centery), 8
            )

            # Dessiner le texte du volume
            font = pygame.font.Font(None, 40)
            volume_text_surface = font.render(texte_volume, True, blanc)
            volume_texte_rect = volume_text_surface.get_rect(
                center=(center_x + 150, 300)
            )
            fenetre.blit(volume_text_surface, volume_texte_rect)

        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_LEFT and section_choisie > 0:
                    section_choisie -= 1
                elif (
                    event.key == pygame.K_RIGHT and section_choisie < len(sections) - 1
                ):
                    section_choisie += 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if (mouse_y < 200):
                    for i in range(len(sections)):
                        if (
                            section_x_debut + i * 200
                            <= mouse_x
                            <= section_x_debut + (i + 1) * 200
                        ):
                            section_choisie = i

                elif section_choisie == 0:
                    if not plein_ecran:
                        for i in range(len(resolutions)):
                            if (250 <= mouse_y <= 250 + len(resolutions) * 50):
                                click_y = (mouse_y - 250) // 50
                                if click_y < len(resolutions):
                                    resolution_index = click_y
                                    largeur, hauteur = resolutions[resolution_index]
                                    fenetre = pygame.display.set_mode(
                                        (largeur, hauteur), pygame.RESIZABLE
                                    )
                                    os.environ["SDL_VIDEO_CENTERED"] = "1"

                    if (
                        250 + len(resolutions) * 50 - 25
                        <= mouse_y
                        <= 250 + len(resolutions) * 50 + 25
                    ):
                        plein_ecran = not plein_ecran
                        flags = pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE
                        fenetre = pygame.display.set_mode((largeur, hauteur), flags)

                    if (
                        250 + (len(resolutions) + 1) * 50 - 25
                        <= mouse_y
                        <= 250 + (len(resolutions) + 1) * 50 + 25
                    ):
                        montrer_fps = not montrer_fps

                if bouton_retour.collidepoint(event.pos):
                    return

            if section_choisie == 1:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if (
                        slider_rect.collidepoint(event.pos)
                        and types_reticule[index_type_reticule] != "Aucun"
                    ):
                        glisse_slider = True
                        slider_pos = (
                            mouse_x - slider_rect.left
                        ) / slider_rect.width * 20 + 1
                        slider_pos = max(1, min(20, slider_pos))
                        texte_parametre = str(int(slider_pos))
                    if (
                        slider_rect_epaisseur.collidepoint(event.pos)
                        and types_reticule[index_type_reticule] == "Croix"
                    ):
                        glisse_slider_epaisseur = True
                        slider_pos_epaisseur = (
                            mouse_x - slider_rect_epaisseur.left
                        ) / slider_rect_epaisseur.width * 4 + 1
                        slider_pos_epaisseur = max(1, min(5, slider_pos_epaisseur))
                        texte_epaisseur = str(int(slider_pos_epaisseur))
                    for i, style in enumerate(types_reticule):
                        style_y = 490 + i * 50
                        if (
                            abs(mouse_x - center_x) < 100
                            and abs(mouse_y - style_y) < 25
                        ):
                            index_type_reticule = i
                elif event.type == pygame.MOUSEBUTTONUP:
                    glisse_slider = False
                    glisse_slider_epaisseur = False
                elif event.type == pygame.MOUSEMOTION:
                    mouse_x = event.pos[0]
                    if (
                        glisse_slider
                        and slider_rect.left <= mouse_x <= slider_rect.right
                    ):
                        slider_pos = (
                            mouse_x - slider_rect.left
                        ) / slider_rect.width * 20 + 1
                        slider_pos = max(1, min(20, slider_pos))
                        texte_parametre = str(int(slider_pos))
                    if (
                        glisse_slider_epaisseur
                        and slider_rect_epaisseur.left
                        <= mouse_x
                        <= slider_rect_epaisseur.right
                    ):
                        slider_pos_epaisseur = (
                            mouse_x - slider_rect_epaisseur.left
                        ) / slider_rect_epaisseur.width * 4 + 1
                        slider_pos_epaisseur = max(1, min(5, slider_pos_epaisseur))
                        texte_epaisseur = str(int(slider_pos_epaisseur))

            if section_choisie == 2:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if slider_rect_volume.collidepoint(event.pos):
                        glisse_slider_volume = True
                        slider_pos_volume = (
                            (mouse_x - slider_rect_volume.left)
                            / slider_rect_volume.width
                            * 100
                        )
                        slider_pos_volume = max(0, min(100, slider_pos_volume))
                        texte_volume = str(int(slider_pos_volume))
                        volume = slider_pos_volume / 100
                        pygame.mixer.music.set_volume(volume)
                elif event.type == pygame.MOUSEBUTTONUP:
                    glisse_slider_volume = False
                elif event.type == pygame.MOUSEMOTION:
                    mouse_x = event.pos[0]
                    if (
                        glisse_slider_volume
                        and slider_rect_volume.left
                        <= mouse_x
                        <= slider_rect_volume.right
                    ):
                        slider_pos_volume = (
                            (mouse_x - slider_rect_volume.left)
                            / slider_rect_volume.width
                            * 100
                        )
                        slider_pos_volume = max(0, min(100, slider_pos_volume))
                        texte_volume = str(int(slider_pos_volume))
                        volume = slider_pos_volume / 100
                        pygame.mixer.music.set_volume(volume)

        index_taille_reticule = min(
            len(tailles_reticule) - 1, max(0, int((slider_pos - 1) / 5))
        )
        index_epaisseur_reticule = min(
            len(epaisseur_reticule) - 1, max(0, int((slider_pos_epaisseur - 1) / 1))
        )

        pygame.display.flip()


# Afficher le compteur de FPS
def dessiner_fps(surface, clock):
    if montrer_fps:
        fps = int(clock.get_fps())
        police = pygame.font.Font(None, 36)
        surface_texte = police.render(f"FPS: {fps}", True, blanc)
        surface.blit(surface_texte, (10, 10))


# Musique du menu
def musique_menu():
    pygame.mixer.music.load(son_menu)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


# Musique de fond
def musique_fond():
    pygame.mixer.music.load(son_fond)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


# Fonction pour arreter la musique
def arreter_musique():
    pygame.mixer.music.stop()


# Afficher l'écran de transition de niveau
def afficher_transition_niveau(niveau):
    texte_niveau = pygame.font.Font(None, 150).render(f"Niveau {niveau}", True, blanc)
    texte_niveau_rect = texte_niveau.get_rect(center=(largeur // 2, hauteur // 2 - 75))

    texte_sous_titre = pygame.font.Font(None, 100).render(
        "Dans les abysses", True, blanc
    )
    texte_sous_titre_rect = texte_sous_titre.get_rect(
        center=(largeur // 2, hauteur // 2 + 75)
    )

    # Animation de fade in
    for alpha in range(0, 256, 5):
        fenetre.fill(noir)
        texte_niveau.set_alpha(alpha)
        texte_sous_titre.set_alpha(alpha)
        fenetre.blit(texte_niveau, texte_niveau_rect)
        fenetre.blit(texte_sous_titre, texte_sous_titre_rect)
        pygame.display.flip()
        pygame.time.delay(10)

    # Attendre 3 secondes
    pygame.time.delay(3000)

    # Animation de fade out
    for alpha in range(255, -1, -5):
        fenetre.fill(noir)
        texte_niveau.set_alpha(alpha)
        texte_sous_titre.set_alpha(alpha)
        fenetre.blit(texte_niveau, texte_niveau_rect)
        fenetre.blit(texte_sous_titre, texte_sous_titre_rect)
        pygame.display.flip()
        pygame.time.delay(10)


# Génération de la carte, des objets et des ennemis
jeu = generer_jeu(nombre_lignes, nombre_colonnes)
cles = placer_cles(jeu, nombre_cles)
ennemis = initialiser_ennemis(jeu, nombre_ennemis)


def dessiner_barre_endurance(surface):
    # Position et taille de la barre d'endurance
    largeur_barre = 200
    hauteur_barre = 20
    x = 30
    y = hauteur - 100

    # Calculer la largeur de la barre d'endurance actuelle
    largeur_actuelle = int((endurance_actuelle / endurance_max) * largeur_barre)

    # Dessiner le fond de la barre
    pygame.draw.rect(surface, gris_fonce, (x, y, largeur_barre, hauteur_barre))
    # Dessiner la barre d'endurance actuelle
    pygame.draw.rect(surface, (0, 255, 0), (x, y, largeur_actuelle, hauteur_barre))
    # Dessiner la bordure de la barre
    pygame.draw.rect(surface, blanc, (x, y, largeur_barre, hauteur_barre), 2)


# Boucle principale
afficher_menu()
pygame.mouse.set_visible(False)
musique_fond()

# Montrer l'écran de transition de niveau avant de commencer le jeu
afficher_transition_niveau(1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.mouse.set_visible(True)
                choix = afficher_menu_pause()
                pygame.mouse.set_visible(False)
                if choix == "recommencer":
                    jeu = generer_jeu(nombre_lignes, nombre_colonnes)
                    cles = placer_cles(jeu, nombre_cles)
                    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
                    cles_collectees = 0
                    ennemis = initialiser_ennemis(jeu, nombre_ennemis)
                elif choix == "menu":
                    jeu = generer_jeu(nombre_lignes, nombre_colonnes)
                    cles = placer_cles(jeu, nombre_cles)
                    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
                    cles_collectees = 0
                    ennemis = initialiser_ennemis(jeu, nombre_ennemis)
                    afficher_menu()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                index_case_selectionnee = max(0, index_case_selectionnee - 1)
            elif event.button == 5:  # Mouse wheel down
                index_case_selectionnee = min(4, index_case_selectionnee + 1)

    # Obtenir la position de la souris
    souris_x, souris_y = pygame.mouse.get_pos()

    # Calculer la position du joueur à l'écran
    joueur_ecran_x = joueur_pos[0] * taille_case - camera_offset[0] + taille_case // 2
    joueur_ecran_y = joueur_pos[1] * taille_case - camera_offset[1] + taille_case // 2

    # Calculer l'angle entre le joueur et la souris
    dx = souris_x - joueur_ecran_x
    dy = souris_y - joueur_ecran_y
    angle_de_vue = math.degrees(math.atan2(dy, dx))

    touches = pygame.key.get_pressed()
    nouvelle_pos = joueur_pos[:]

    # Vérifier si assez de temps s'est écoulé depuis le dernier mouvement
    temps_actuel = pygame.time.get_ticks()
    if temps_actuel - dernier_mouvement >= delai_mouvement:
        if touches[pygame.K_UP] or touches[pygame.K_z]:
            nouvelle_pos[1] -= 1
            dernier_mouvement = temps_actuel
        elif touches[pygame.K_DOWN] or touches[pygame.K_s]:
            nouvelle_pos[1] += 1
            dernier_mouvement = temps_actuel
        elif touches[pygame.K_LEFT] or touches[pygame.K_q]:
            nouvelle_pos[0] -= 1
            dernier_mouvement = temps_actuel
        elif touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            nouvelle_pos[0] += 1
            dernier_mouvement = temps_actuel

    # Vérifie si le déplacement est valide
    if deplacement_valide(jeu, nouvelle_pos):
        joueur_pos = nouvelle_pos

    # Mise à jour de la caméra pour suivre le joueur
    camera_offset[0] = joueur_pos[0] * taille_case - largeur // 2
    camera_offset[1] = joueur_pos[1] * taille_case - hauteur // 2

    # Vérifier la collision avec les ennemis
    if verifier_collision_ennemis(joueur_pos, ennemis):
        if game_over() == "menu":
            jeu = generer_jeu(nombre_lignes, nombre_colonnes)
            cles = placer_cles(jeu, nombre_cles)
            joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
            cles_collectees = 0
            ennemis = initialiser_ennemis(jeu, nombre_ennemis)
            afficher_menu()

    # Dessiner le jeu
    dessiner_jeu(jeu, joueur_pos, camera_offset)

    # Dessiner l'inventaire
    dessiner_inventaire(fenetre)

    # Collecte des clés
    if jeu[joueur_pos[1]][joueur_pos[0]] == "C":
        cles_collectees += 1
        jeu[joueur_pos[1]][joueur_pos[0]] = " "

    # Déplacer les ennemis
    deplacer_ennemis(jeu, ennemis, joueur_pos)

    # Dessiner les ennemis
    for ennemi in ennemis:
        x = ennemi.x * taille_case - camera_offset[0]
        y = ennemi.y * taille_case - camera_offset[1]

        # Calculer la distance entre le joueur et l'ennemi
        dx = ennemi.x - joueur_pos[0]
        dy = ennemi.y - joueur_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        # Vérifier si l'ennemi est dans le cercle proche
        if distance * taille_case <= rayon_vision_proche:
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), jeu):
                pygame.draw.rect(fenetre, ennemis, (x, y, taille_case, taille_case))
        # Sinon, vérifier s'il est dans le cône de vision
        elif est_dans_cone(
            joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, cone_longueur
        ):
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), jeu):
                pygame.draw.rect(fenetre, ennemis, (x, y, taille_case, taille_case))

    # Victoire si le joueur atteint la sortie avec toutes les clés
    if jeu[joueur_pos[1]][joueur_pos[0]] == "S" and cles_collectees == nombre_cles:
        arreter_musique()
        afficher_victoire()
        running = False

    # Dessiner le compteur de clés après avoir dessiné tout le reste
    dessiner_compteur_cles(fenetre, cles_collectees, nombre_cles)

    # Dessiner le réticule
    if not pygame.mouse.get_visible():
        mouse_x, mouse_y = pygame.mouse.get_pos()
        size = tailles_reticule[index_taille_reticule]

        if types_reticule[index_type_reticule] == "Croix":
            pygame.draw.line(
                fenetre,
                blanc,
                (mouse_x - size, mouse_y),
                (mouse_x + size, mouse_y),
                epaisseur_reticule[index_epaisseur_reticule],
            )
            pygame.draw.line(
                fenetre,
                blanc,
                (mouse_x, mouse_y - size),
                (mouse_x, mouse_y + size),
                epaisseur_reticule[index_epaisseur_reticule],
            )
        elif types_reticule[index_type_reticule] == "Point":
            pygame.draw.circle(fenetre, blanc, (mouse_x, mouse_y), size)

    # Dessiner le commpteur de FPS
    dessiner_fps(fenetre, horloge)

    # Dessiner la barre d'endurance
    # dessiner_barre_endurance(fenetre)

    pygame.display.flip()
    horloge.tick(60)  # Limiter à 60 FPS

pygame.quit()