import pygame
import random
import sys
import math

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
LARGEUR = 1500  # Default width (will be overridden by fullscreen)
HAUTEUR = 900   # Default height (will be overridden by fullscreen)
TAILLE_CASE = 50  # Taille d'une case dans le labyrinthe

# Couleurs utilisées dans le jeu
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
GRIS = (200, 200, 200)
JOUEUR = (41, 27, 14)
SORTIE = (0, 255, 0)
MUR = (100, 40, 30)
SOL = (115, 109, 115)
CLE = (255, 223, 0)
ENNEMIES = (255, 0, 0)
BORDEAUX = (40, 0, 0)

# Création de la fenêtre principale
fenetre = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGEUR, HAUTEUR = fenetre.get_size()  # Get actual screen dimensions
pygame.display.set_caption("Jeu Hôpital")

# Horloge pour contrôler les FPS
horloge = pygame.time.Clock()

# Paramètres de jeu
NOMBRE_CLES = 3  # Nombre de clés à collecter pour gagner
cles_collectees = 0  # Compteur de clés collectées
NOMBRE_ENNEMIES = 5
VITESSE_ENNEMIE = 0.4  # Augmentation de la vitesse des ennemis

# Paramètres de la vision
cone_angle = 60  # Angle du cône de vision en degrés
cone_length = 600  # Augmentation de la longueur du cône de vision (était 375)

# Ajouter cette constante avec les autres paramètres de vision
RAYON_VISION_PROCHE = 100  # Rayon du cercle de vision autour du joueur

# Génération initiale
NB_LIGNES = (HAUTEUR // TAILLE_CASE) * 8
NB_COLONNES = (LARGEUR // TAILLE_CASE) * 8
print("NB_LIGNES :", NB_LIGNES, "NB_COLONNES :", NB_COLONNES)  # Vérification
joueur_pos = [NB_COLONNES // 2, NB_LIGNES // 2]
camera_offset = [0, 0]

# Initialisation de l'angle de vue avec une valeur par défaut
angle_de_vue = 270  # 0 = droite, 90 = bas, 180 = gauche, 270 = haut
derniere_direction = (0, 0)  # Direction initiale (aucune touche appuyée)

# Structure pour stocker les ennemis avec leurs positions et directions
ennemis = []  # Liste qui contiendra des dictionnaires pour chaque ennemi

# Paramètres du joueur
FPS = 60
VITESSE_NORMALE = 5  # Cases par seconde
VITESSE_SPRINT = 10  # Cases par seconde pendant le sprint
ENDURANCE_MAX = 100
TAUX_RECUPERATION = 0.5
COUT_SPRINT = 2
endurance = ENDURANCE_MAX
dernier_mouvement = pygame.time.get_ticks()  # Initialiser le temps du dernier mouvement

# Optimisation des constantes globales
TAILLE_CACHE = 100  # Taille du cache pour les calculs trigonométriques
cos_cache = {i: math.cos(math.radians(i)) for i in range(360)}
sin_cache = {i: math.sin(math.radians(i)) for i in range(360)}

# Ajouter une variable pour suivre l'index de la case sélectionnée
index_case_selectionnee = 0

# Ajouter ces variables pour les résolutions
RESOLUTIONS = [
    ("Plein écran", (0, 0), pygame.FULLSCREEN),
    ("1920x1080", (1920, 1080), 0),
    ("1280x720", (1280, 720), 0),
    ("800x600", (800, 600), 0)
]
resolution_actuelle = 0  # Index de la résolution actuelle (0 = plein écran par défaut)

class Ennemi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.compteur_deplacement = 0
        self.cone_vision = 8
        self.angle_vision = 120
        self.vitesse_normale = VITESSE_ENNEMIE
        self.vitesse_lente = VITESSE_ENNEMIE * 0.3
        self.vitesse_actuelle = self.vitesse_lente
        # Nouvelles variables pour la mémoire
        self.derniere_pos_joueur = None
        self.temps_memoire = 0
        self.duree_memoire_max = 180  # Environ 3 secondes à 60 FPS

    def peut_voir_joueur(self, joueur_pos, hopital):
        # Calculer la distance entre l'ennemi et le joueur
        dx = joueur_pos[0] - self.x
        dy = joueur_pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > self.cone_vision:
            return False
            
        # Vérification de la ligne de vue (pas d'obstacles)
        x, y = self.x, self.y
        pas = 0.1
        longueur = math.sqrt(dx*dx + dy*dy)
        if longueur > 0:
            dx, dy = dx/longueur, dy/longueur
            for i in range(int(longueur/pas)):
                x += dx * pas
                y += dy * pas
                if hopital[int(y)][int(x)] == "#":
                    return False
        return True

def musique_menu():
    pygame.mixer.music.load("C:/Users/iaroslavlushcheko/Desktop/projet NSI/OST/S.T.A.L.K.E.R..mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def musique_fond():
    pygame.mixer.music.load("C:/Users/iaroslavlushcheko/Desktop/projet NSI/OST/Amnesia-02.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

def arreter_musique():
    pygame.mixer.music.stop()

def initialiser_ennemis(hopital, nombre_ennemis):
    ennemis = []
    cases_vides = [(j, i) for i, ligne in enumerate(hopital) 
                   for j, case in enumerate(ligne) if case == " "]
    
    for _ in range(nombre_ennemis):
        if cases_vides:
            x, y = random.choice(cases_vides)
            ennemis.append(Ennemi(x, y))
            cases_vides.remove((x, y))
    return ennemis

def deplacer_ennemis(hopital, ennemis, joueur_pos):
    for ennemi in ennemis:
        voit_joueur = ennemi.peut_voir_joueur(joueur_pos, hopital)
        
        if voit_joueur:
            # Mettre à jour la dernière position connue du joueur
            ennemi.derniere_pos_joueur = joueur_pos[:]
            ennemi.temps_memoire = ennemi.duree_memoire_max
            ennemi.vitesse_actuelle = ennemi.vitesse_normale
        elif ennemi.temps_memoire > 0:
            # L'ennemi ne voit plus le joueur mais se souvient de sa position
            ennemi.temps_memoire -= 1
            ennemi.vitesse_actuelle = ennemi.vitesse_normale * 0.7  # Légèrement plus lent pendant la poursuite de mémoire
        else:
            # L'ennemi a complètement perdu la trace du joueur
            ennemi.derniere_pos_joueur = None
            ennemi.vitesse_actuelle = ennemi.vitesse_lente

        ennemi.compteur_deplacement += ennemi.vitesse_actuelle
        if ennemi.compteur_deplacement >= 1:
            ennemi.compteur_deplacement = 0
            
            if voit_joueur or (ennemi.derniere_pos_joueur is not None and ennemi.temps_memoire > 0):
                # Utiliser soit la position actuelle du joueur, soit la dernière position connue
                cible = joueur_pos if voit_joueur else ennemi.derniere_pos_joueur
                
                dx = cible[0] - ennemi.x
                dy = cible[1] - ennemi.y
                
                if abs(dx) > abs(dy):
                    nouveau_x = ennemi.x + (1 if dx > 0 else -1)
                    nouveau_y = ennemi.y
                    if not deplacement_valide(hopital, [nouveau_x, nouveau_y]):
                        nouveau_x = ennemi.x
                        nouveau_y = ennemi.y + (1 if dy > 0 else -1)
                else:
                    nouveau_y = ennemi.y + (1 if dy > 0 else -1)
                    nouveau_x = ennemi.x
                    if not deplacement_valide(hopital, [nouveau_x, nouveau_y]):
                        nouveau_x = ennemi.x + (1 if dx > 0 else -1)
                        nouveau_y = ennemi.y
                        
                # Si l'ennemi atteint la dernière position connue et ne voit pas le joueur
                if not voit_joueur and ennemi.derniere_pos_joueur:
                    if abs(ennemi.x - ennemi.derniere_pos_joueur[0]) <= 1 and \
                       abs(ennemi.y - ennemi.derniere_pos_joueur[1]) <= 1:
                        ennemi.temps_memoire = 0  # Arrêter la poursuite
                        ennemi.derniere_pos_joueur = None
            else:
                # Comportement aléatoire plus lent
                if random.random() < 0.05:  # Réduit la fréquence des changements de direction
                    ennemi.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                
                nouveau_x = ennemi.x + ennemi.direction[0]
                nouveau_y = ennemi.y + ennemi.direction[1]
            
            if deplacement_valide(hopital, [nouveau_x, nouveau_y]):
                ennemi.x = nouveau_x
                ennemi.y = nouveau_y
            else:
                ennemi.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

def dessiner_vision_ennemis(surface, ennemi, camera_offset):
    # Dessiner le cône de vision des ennemis (pour le débogage)
    x = ennemi.x * TAILLE_CASE - camera_offset[0] + TAILLE_CASE // 2
    y = ennemi.y * TAILLE_CASE - camera_offset[1] + TAILLE_CASE // 2
    
    # Déterminer l'angle de base selon la direction
    angle_base = 0
    if ennemi.direction == (0, -1): angle_base = 270
    elif ennemi.direction == (0, 1): angle_base = 90
    elif ennemi.direction == (-1, 0): angle_base = 180
    elif ennemi.direction == (1, 0): angle_base = 0
    
    start_angle = math.radians(angle_base - ennemi.angle_vision / 2)
    end_angle = math.radians(angle_base + ennemi.angle_vision / 2)
    
    points = [(x, y)]
    steps = 20
    for i in range(steps + 1):
        theta = start_angle + (end_angle - start_angle) * i / steps
        px = x + math.cos(theta) * ennemi.cone_vision * TAILLE_CASE / 10
        py = y + math.sin(theta) * ennemi.cone_vision * TAILLE_CASE / 10
        points.append((px, py))
    
    # Dessiner le cône de vision en semi-transparent
    s = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    pygame.draw.polygon(s, (255, 0, 0, 30), points)
    surface.blit(s, (0, 0))

def verifier_collision_ennemis(joueur_pos, ennemis):
    for ennemi in ennemis:
        if (abs(joueur_pos[0] - ennemi.x) < 1 and 
            abs(joueur_pos[1] - ennemi.y) < 1):
            return True
    return False

def game_over():
    fenetre.fill(NOIR)
    texte = pygame.font.Font(None, 60).render("Game Over!", True, BLANC)
    texte_rect = texte.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    pygame.time.delay(2000)  # Attendre 2 secondes
    return "menu"  # Retourner au menu

def dessiner_vision_cone(surface, position, angle, length):
    x, y = position
    start_angle = math.radians(angle - cone_angle / 2)
    end_angle = math.radians(angle + cone_angle / 2)
    points = [position]
    steps = 50
    for i in range(steps + 1):
        theta = start_angle + i * (end_angle - start_angle) / steps
        points.append((x + length * math.cos(theta), y + length * math.sin(theta)))
    pygame.draw.polygon(surface, BLANC, points)

def appliquer_masque_vision(surface, position, angle, length):
    masque = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    masque.fill((0, 0, 0, 200))  # Masque noir semi-transparent
    
    x, y = position
    start_angle = math.radians(angle - cone_angle / 2)
    end_angle = math.radians(angle + cone_angle / 2)
    
    # Points pour le polygone de vision
    points = [(x, y)]  # Point de départ (position du joueur)
    
    # Pour chaque rayon du cône
    steps = 180  # Plus de précision pour un rendu plus lisse
    for i in range(steps + 1):
        theta = start_angle + i * (end_angle - start_angle) / steps
        
        # Lancer un rayon
        for dist in range(0, int(length), 2):  # Pas plus petit pour plus de précision
            ray_x = x + dist * math.cos(theta)
            ray_y = y + dist * math.sin(theta)
            
            # Convertir en coordonnées de grille
            grille_x = int((ray_x + camera_offset[0]) / TAILLE_CASE)
            grille_y = int((ray_y + camera_offset[1]) / TAILLE_CASE)
            
            # Vérifier si on touche un mur
            if (0 <= grille_y < len(hopital) and 
                0 <= grille_x < len(hopital[0]) and 
                hopital[grille_y][grille_x] == "#"):
                points.append((ray_x, ray_y))
                break
            elif dist >= length - 2:  # Si on atteint la distance maximale
                points.append((ray_x, ray_y))
    
    # Dessiner le polygone de vision du cône
    if len(points) > 2:
        pygame.draw.polygon(masque, (0, 0, 0, 0), points)
    
    # Ajouter le cercle de vision proche
    pygame.draw.circle(masque, (0, 0, 0, 0), (int(x), int(y)), RAYON_VISION_PROCHE)
    
    # Appliquer le masque sur l'écran
    surface.blit(masque, (0, 0))

def generer_hopital(nb_lignes, nb_colonnes):
    nb_lignes = (nb_lignes // 3) * 3 + 1  # Ajuste les dimensions pour garantir un labyrinthe valide
    nb_colonnes = (nb_colonnes // 3)* 3 + 1
    hopital = [["#" for _ in range(nb_colonnes)] for _ in range(nb_lignes)]

    def voisins(x, y):
        directions = [(6, 0), (-6, 0), (0, 6), (0, -6)]
        random.shuffle(directions)  # Mélange pour générer des labyrinthes variés
        return [
            (x + dx, y + dy)
            for dx, dy in directions
            if 0 <= x + dx < nb_colonnes and 0 <= y + dy < nb_lignes
        ]

    def départ(x, y):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if 0 <= y + i < nb_lignes and 0 <= x + j < nb_colonnes:
                    hopital[y + i][x + j] = " "
        for nx, ny in voisins(x, y):
            if hopital[ny][nx] == "#":
                for i in range(-1, 2):
                    for j in range(-3, 4):
                        if 0 <= (y + ny) // 2 + i < nb_lignes and 0 <= (x + nx) // 2 + j < nb_colonnes:
                            hopital[(y + ny) // 2 + i][(x + nx) // 2 + j] = " "
                départ(nx, ny)

    départ(nb_colonnes // 2, nb_lignes // 2)  # Commencer au centre du labyrinthe

    # Ajoute une sortie sur un bord aléatoire
    bords = [
        (0, random.randint(1, nb_colonnes - 2)),  # Bord supérieur
        (nb_lignes - 1, random.randint(1, nb_colonnes - 2)),  # Bord inférieur
        (random.randint(1, nb_lignes - 2), 0),  # Bord gauche
        (random.randint(1, nb_lignes - 2), nb_colonnes - 1)  # Bord droit
    ]
    random.shuffle(bords)
    for sortie_y, sortie_x in bords:
        if hopital[sortie_y][sortie_x] == " ":
            hopital[sortie_y][sortie_x] = "S"  # Marque la sortie
            break

    return hopital

# Fonction pour placer les clés dans le labyrinthe
def placer_cles(hopital, nombre_cles):
    cles = []
    cases_vides = [(i, j) for i, ligne in enumerate(hopital) for j, case in enumerate(ligne) if case == " "]
    for _ in range(nombre_cles):
        x, y = random.choice(cases_vides)
        cles.append((x, y))
        hopital[x][y] = "C"  # Ajoute une clé à cet emplacement
        cases_vides.remove((x, y))
    return cles

def placer_ennemies(hopital, NOMBRE_ENNEMIES):
    ennemies = []
    case_vide = [(i, j) for i, ligne in enumerate(hopital) for j, case in enumerate(ligne) if case == " "]
    for j in range(NOMBRE_ENNEMIES):
        x, y = random.choice(case_vide)
        ennemies.append((x, y))
        hopital[x][y] = "Y"  # Ajoute un ennemie à cet emplacement
        case_vide.remove((x, y))
    return ennemies

def est_dans_cone(joueur_pos, case_pos, angle, length):
    """Version optimisée de la vérification du cône"""
    dx = case_pos[0] - joueur_pos[0]
    dy = case_pos[1] - joueur_pos[1]
    distance = dx*dx + dy*dy  # Pas besoin de sqrt pour la comparaison
    
    if distance > (length/TAILLE_CASE) * (length/TAILLE_CASE):
        return False
        
    angle = angle % 360
    angle_case = math.degrees(math.atan2(dy, dx)) % 360
    diff_angle = (angle_case - angle + 180) % 360 - 180
    
    return abs(diff_angle) <= cone_angle / 2

def est_visible(joueur_pos, case_pos, hopital):
    """Vérifie si une case est visible (dans le cône ou le cercle proche, et pas de mur entre)"""
    joueur_x, joueur_y = joueur_pos
    case_x, case_y = case_pos
    
    # Calculer la distance entre le joueur et la case
    dx = case_x - joueur_x
    dy = case_y - joueur_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Vérifier si la case est dans le cercle de vision proche
    if distance * TAILLE_CASE <= RAYON_VISION_PROCHE:
        # Vérifier s'il n'y a pas de mur entre
        return not a_mur_entre(joueur_pos, case_pos, hopital)
    
    # Sinon, vérifier si c'est dans le cône de vision
    if not est_dans_cone(joueur_pos, case_pos, angle_de_vue, cone_length):
        return False
    
    # Vérifier s'il n'y a pas de mur entre
    return not a_mur_entre(joueur_pos, case_pos, hopital)

def a_mur_entre(joueur_pos, case_pos, hopital):
    """Version optimisée de la vérification des murs"""
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
            if hopital[y][x] == "#":
                return True
    else:
        err = dy / 2.0
        while y != int(y2):
            err -= dx
            if err < 0:
                x += 1 if x2 > x1 else -1
                err += dy
            y += 1 if y2 > y1 else -1
            if hopital[y][x] == "#":
                return True
                
    return False

def dessiner_hopital(hopital, joueur_pos, camera_offset):
    fenetre.fill(NOIR)
    
    # Calculer les limites visibles
    marge = 1  # Réduit la marge pour moins de calculs
    debut_x = max(0, int(camera_offset[0] // TAILLE_CASE) - marge)
    debut_y = max(0, int(camera_offset[1] // TAILLE_CASE) - marge)
    fin_x = min(len(hopital[0]), int((camera_offset[0] + LARGEUR) // TAILLE_CASE) + marge)
    fin_y = min(len(hopital), int((camera_offset[1] + HAUTEUR) // TAILLE_CASE) + marge)
    
    # Pré-calculer les offsets
    cam_x = camera_offset[0]
    cam_y = camera_offset[1]
    
    # Rendu optimisé
    for i in range(debut_y, fin_y):
        y = i * TAILLE_CASE - cam_y
        for j in range(debut_x, fin_x):
            x = j * TAILLE_CASE - cam_x
            case = hopital[i][j]
            if case == "#":
                pygame.draw.rect(fenetre, MUR, (x, y, TAILLE_CASE, TAILLE_CASE))
            elif case == " ":
                pygame.draw.rect(fenetre, SOL, (x, y, TAILLE_CASE, TAILLE_CASE))
            elif case in ["S", "C"] and est_visible(joueur_pos, (j, i), hopital):
                couleur = SORTIE if case == "S" else CLE
                pygame.draw.rect(fenetre, couleur, (x, y, TAILLE_CASE, TAILLE_CASE))
    
    # Dessiner le joueur
    pygame.draw.rect(fenetre, JOUEUR, (
        joueur_pos[0] * TAILLE_CASE - cam_x,
        joueur_pos[1] * TAILLE_CASE - cam_y,
        TAILLE_CASE, TAILLE_CASE
    ))
    
    # Appliquer le masque de vision
    joueur_centre = (
        joueur_pos[0] * TAILLE_CASE - cam_x + TAILLE_CASE // 2,
        joueur_pos[1] * TAILLE_CASE - cam_y + TAILLE_CASE // 2
    )
    appliquer_masque_vision(fenetre, joueur_centre, angle_de_vue, cone_length)

# Vérification de la validité du déplacement
def deplacement_valide(hopital, pos):
    x, y = pos
    if 0 <= y < len(hopital) and 0 <= x < len(hopital[0]):
        return hopital[y][x] != "#"
    return False

# Fonction de victoire
def afficher_victoire():
    fenetre.fill(NOIR)
    texte = pygame.font.Font(None, 60).render("Victoire !", True, BLANC)
    texte_rect = texte.get_rect(center=(LARGEUR // 2, HAUTEUR // 2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    pygame.time.delay(3000)

def afficher_credits():
    while True:
        fenetre.fill(NOIR)

        # Afficher les noms en colonne avec une taille de police plus grande
        noms = [
            "Iaroslav Lushcheko",
            "Eliott Raulet",
            "Mohamed El Mekkawy",
            "Ugo Guillemart"
        ]
        
        # Ajuster la position de départ pour centrer verticalement
        for i, nom in enumerate(noms):
            texte = pygame.font.Font(None, 80).render(nom, True, BLANC)  # Taille de police augmentée
            texte_rect = texte.get_rect(center=(LARGEUR // 2, HAUTEUR // 2 - 50 + i * 90))  # Ajustement de la position
            fenetre.blit(texte, texte_rect)

        # Vérifier les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Retour au menu principal
                    return

        pygame.display.flip()

def changer_resolution(index):
    global LARGEUR, HAUTEUR, fenetre, resolution_actuelle
    resolution_actuelle = index
    taille, flags = RESOLUTIONS[index][1:3]
    if flags == pygame.FULLSCREEN:
        fenetre = pygame.display.set_mode((0, 0), flags)
        LARGEUR, HAUTEUR = fenetre.get_size()
    else:
        fenetre = pygame.display.set_mode(taille)
        LARGEUR, HAUTEUR = taille
    return "continuer"

def afficher_menu():
    pygame.mixer.init()
    musique_menu()
    
    while True:
        fenetre.fill(NOIR)
        
        # Titre
        titre = pygame.font.Font(None, 150).render("Creepy Hospital", True, BLANC)
        titre_rect = titre.get_rect(center=(LARGEUR // 2, HAUTEUR // 4))
        fenetre.blit(titre, titre_rect)
        
        souris_x, souris_y = pygame.mouse.get_pos()
        hauteur_base = HAUTEUR // 2
        espacement = 100

        boutons = [
            (pygame.Rect(LARGEUR // 2 - 170, hauteur_base, 340, 70), "Paramètres", 50),
            (pygame.Rect(LARGEUR // 2 - 230, hauteur_base + espacement, 460, 100), "Jouer", 100),
            (pygame.Rect(LARGEUR // 2 - 150, hauteur_base + espacement * 2, 300, 70), "Crédits", 50),
            (pygame.Rect(LARGEUR // 2 - 120, hauteur_base + espacement * 3, 240, 70), "Quitter", 50),
        ]
        
        for bouton, texte, taille_texte in boutons:
            if bouton.collidepoint(souris_x, souris_y):
                couleur = (255, 0, 0)
                bouton = bouton.inflate(20, 20)
            else:
                couleur = BORDEAUX
            pygame.draw.rect(fenetre, couleur, bouton)
            texte_rendu = pygame.font.Font(None, taille_texte).render(texte, True, BLANC)
            fenetre.blit(texte_rendu, (bouton.centerx - texte_rendu.get_width() // 2, bouton.centery - texte_rendu.get_height() // 2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for bouton, texte, _ in boutons:
                    if bouton.collidepoint(event.pos):
                        if texte == "Jouer":
                            arreter_musique()
                            musique_fond()
                            return
                        elif texte == "Crédits":
                            afficher_credits()
                        elif texte == "Paramètres":
                            afficher_parametres()
                        elif texte == "Quitter":
                            pygame.quit()
                            sys.exit()

def afficher_parametres():
    global resolution_actuelle
    while True:
        fenetre.fill(NOIR)

        # Titre des paramètres
        titre = pygame.font.Font(None, 60).render("Paramètres", True, BLANC)
        titre_rect = titre.get_rect(center=(LARGEUR // 2, 50))
        fenetre.blit(titre, titre_rect)

        # Liste des résolutions
        hauteur_base = 150
        espacement = 60
        boutons_resolution = []
        
        for i, (nom_res, _, _) in enumerate(RESOLUTIONS):
            rect = pygame.Rect(LARGEUR // 2 - 150, hauteur_base + i * espacement, 300, 50)
            couleur = (255, 0, 0) if i == resolution_actuelle else BLANC
            texte = pygame.font.Font(None, 40).render(nom_res, True, couleur)
            texte_rect = texte.get_rect(center=rect.center)
            boutons_resolution.append((rect, texte, texte_rect))

        # Vérifier les événements
        souris_x, souris_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, (rect, _, _) in enumerate(boutons_resolution):
                    if rect.collidepoint(event.pos):
                        changer_resolution(i)
                        return

        # Dessiner les boutons
        for rect, texte, texte_rect in boutons_resolution:
            if rect.collidepoint(souris_x, souris_y):
                pygame.draw.rect(fenetre, BORDEAUX, rect)
            fenetre.blit(texte, texte_rect)

        pygame.display.flip()

def dessiner_inventaire(surface):
    # Position et taille de l'inventaire
    inventaire_x = 10
    inventaire_y = HAUTEUR - 70
    case_taille = 50
    espacement = 10
    
    # Dessiner les cases d'inventaire
    for i in range(9):  # 9 cases d'inventaire
        x = inventaire_x + (case_taille + espacement) * i
        rect = pygame.Rect(x, inventaire_y, case_taille, case_taille)
        
        # Mettre en surbrillance la case sélectionnée
        if i == index_case_selectionnee:
            pygame.draw.rect(surface, (100, 100, 100), rect)  # Case sélectionnée en gris
            pygame.draw.rect(surface, BLANC, rect, 3)  # Bordure blanche plus épaisse
        else:
            pygame.draw.rect(surface, (50, 50, 50), rect)  # Cases non sélectionnées en gris foncé
            pygame.draw.rect(surface, GRIS, rect, 1)  # Bordure grise fine

def dessiner_compteur_cles(surface, cles_collectees, total_cles):
    # Position du compteur (en haut à droite)
    x = LARGEUR - 100
    y = 20
    
    # Dessiner le texte
    texte = f"Clés: {cles_collectees}/{total_cles}"
    font = pygame.font.Font(None, 36)
    texte_surface = font.render(texte, True, BLANC)
    surface.blit(texte_surface, (x, y))

def afficher_menu_pause():
    musique_menu()
    
    while True:
        fenetre.fill(NOIR)
        
        titre = pygame.font.Font(None, 100).render("Pause", True, BLANC)
        titre_rect = titre.get_rect(center=(LARGEUR // 2, HAUTEUR // 4))
        fenetre.blit(titre, titre_rect)
        
        hauteur_base = HAUTEUR // 2
        espacement = 80
        boutons = [
            (pygame.Rect(LARGEUR // 2 - 150, hauteur_base, 300, 60), "Continuer"),
            (pygame.Rect(LARGEUR // 2 - 150, hauteur_base + espacement, 300, 60), "Recommencer"),
            (pygame.Rect(LARGEUR // 2 - 150, hauteur_base + espacement * 2, 300, 60), "Menu Principal")
        ]
        
        souris_x, souris_y = pygame.mouse.get_pos()
        
        for bouton, texte in boutons:
            if bouton.collidepoint(souris_x, souris_y):
                couleur = (255, 0, 0)
                bouton = bouton.inflate(20, 20)
            else:
                couleur = BORDEAUX
            pygame.draw.rect(fenetre, couleur, bouton)
            texte_rendu = pygame.font.Font(None, 40).render(texte, True, BLANC)
            fenetre.blit(texte_rendu, (bouton.centerx - texte_rendu.get_width() // 2, bouton.centery - texte_rendu.get_height() // 2))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    arreter_musique()
                    musique_fond()
                    return "continuer"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for bouton, texte in boutons:
                    if bouton.collidepoint(event.pos):
                        if texte == "Continuer":
                            arreter_musique()
                            musique_fond()
                            return "continuer"
                        elif texte == "Recommencer":
                            return "recommencer"
                        elif texte == "Menu Principal":
                            return "menu"

def dessiner_barre_endurance(surface):
    # Position et dimensions de la barre d'endurance
    x = 10
    y = 10
    largeur = 200
    hauteur = 20
    
    # Dessiner le fond de la barre
    pygame.draw.rect(surface, GRIS, (x, y, largeur, hauteur))
    
    # Dessiner la barre d'endurance
    largeur_endurance = (endurance / ENDURANCE_MAX) * largeur
    couleur_endurance = (0, 255, 0) if endurance > 30 else (255, 0, 0)  # Vert si > 30%, rouge sinon
    pygame.draw.rect(surface, couleur_endurance, (x, y, largeur_endurance, hauteur))
    
    # Dessiner le contour
    pygame.draw.rect(surface, BLANC, (x, y, largeur, hauteur), 2)

# Génération objet
hopital = generer_hopital(NB_LIGNES, NB_COLONNES)
cles = placer_cles(hopital, NOMBRE_CLES)
ennemis = initialiser_ennemis(hopital, NOMBRE_ENNEMIES)

# Boucle principale
afficher_menu()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                choix = afficher_menu_pause()
                if choix == "recommencer":
                    hopital = generer_hopital(NB_LIGNES, NB_COLONNES)
                    cles = placer_cles(hopital, NOMBRE_CLES)
                    joueur_pos = [NB_COLONNES // 2, NB_LIGNES // 2]
                    cles_collectees = 0
                    ennemis = initialiser_ennemis(hopital, NOMBRE_ENNEMIES)
                elif choix == "menu":
                    # Réinitialiser le jeu
                    hopital = generer_hopital(NB_LIGNES, NB_COLONNES)
                    cles = placer_cles(hopital, NOMBRE_CLES)
                    joueur_pos = [NB_COLONNES // 2, NB_LIGNES // 2]
                    cles_collectees = 0
                    ennemis = initialiser_ennemis(hopital, NOMBRE_ENNEMIES)
                    # Retourner au menu
                    afficher_menu()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Molette de la souris vers le haut
                index_case_selectionnee = (index_case_selectionnee - 1) % 9  # Sélectionner la case précédente
            elif event.button == 5:  # Molette de la souris vers le bas
                index_case_selectionnee = (index_case_selectionnee + 1) % 9  # Sélectionner la case suivante

    # Obtenir la position de la souris
    souris_x, souris_y = pygame.mouse.get_pos()
    
    # Calculer la position du joueur à l'écran
    joueur_ecran_x = joueur_pos[0] * TAILLE_CASE - camera_offset[0] + TAILLE_CASE // 2
    joueur_ecran_y = joueur_pos[1] * TAILLE_CASE - camera_offset[1] + TAILLE_CASE // 2
    
    # Calculer l'angle entre le joueur et la souris
    dx = souris_x - joueur_ecran_x
    dy = souris_y - joueur_ecran_y
    angle_de_vue = math.degrees(math.atan2(dy, dx))
    
    touches = pygame.key.get_pressed()
    nouvelle_pos = joueur_pos[:]
    
    # Calculer le delta temps
    temps_actuel = pygame.time.get_ticks()
    delta_temps = (temps_actuel - dernier_mouvement) / 1000.0  # Convertir en secondes
    dernier_mouvement = temps_actuel
    
    # Gestion du sprint
    est_en_sprint = touches[pygame.K_LSHIFT] and endurance > 0
    vitesse_actuelle = VITESSE_SPRINT if est_en_sprint else VITESSE_NORMALE
    
    # Récupération de l'endurance quand on ne sprinte pas
    if not est_en_sprint and endurance < ENDURANCE_MAX:
        endurance = min(ENDURANCE_MAX, endurance + TAUX_RECUPERATION)
    
    # Calculer le déplacement en fonction du temps
    deplacement = vitesse_actuelle * delta_temps
    
    # Gestion des mouvements
    dx = 0
    dy = 0
    if touches[pygame.K_UP] or touches[pygame.K_z]:
        dy -= deplacement
    if touches[pygame.K_DOWN] or touches[pygame.K_s]:
        dy += deplacement
    if touches[pygame.K_LEFT] or touches[pygame.K_q]:
        dx -= deplacement
    if touches[pygame.K_RIGHT] or touches[pygame.K_d]:
        dx += deplacement
    
    # Normaliser le déplacement diagonal
    if dx != 0 and dy != 0:
        dx *= 0.707  # 1/√2
        dy *= 0.707
    
    # Appliquer le déplacement
    if dx != 0 or dy != 0:
        nouvelle_pos = [
            joueur_pos[0] + dx,
            joueur_pos[1] + dy
        ]
        
        # Vérifier si le déplacement est valide
        nouvelle_pos_arrondie = [round(nouvelle_pos[0]), round(nouvelle_pos[1])]
        if deplacement_valide(hopital, nouvelle_pos_arrondie):
            joueur_pos = nouvelle_pos
            if est_en_sprint:
                endurance = max(0, endurance - COUT_SPRINT * delta_temps)

    # Arrondir la position pour l'affichage
    pos_affichage = [round(joueur_pos[0]), round(joueur_pos[1])]

    # Mise à jour de la caméra pour suivre le joueur
    camera_offset[0] = joueur_pos[0] * TAILLE_CASE - LARGEUR // 2
    camera_offset[1] = joueur_pos[1] * TAILLE_CASE - HAUTEUR // 2

    # Vérifier la collision avec les ennemis
    if verifier_collision_ennemis(joueur_pos, ennemis):
        if game_over() == "menu":
            # Réinitialiser le jeu
            hopital = generer_hopital(NB_LIGNES, NB_COLONNES)
            cles = placer_cles(hopital, NOMBRE_CLES)
            joueur_pos = [NB_COLONNES // 2, NB_LIGNES // 2]
            cles_collectees = 0
            ennemis = initialiser_ennemis(hopital, NOMBRE_ENNEMIES)
            # Retourner au menu
            afficher_menu()

    # Dessiner l'hôpital
    dessiner_hopital(hopital, joueur_pos, camera_offset)

    # Dessiner l'inventaire
    dessiner_inventaire(fenetre)

    # Collecte des clés
    pos_grille = [int(joueur_pos[1]), int(joueur_pos[0])]  # Convertir en entiers
    if hopital[pos_grille[0]][pos_grille[1]] == "C":
        cles_collectees += 1
        hopital[pos_grille[0]][pos_grille[1]] = " "

    # Déplacer les ennemis
    deplacer_ennemis(hopital, ennemis, joueur_pos)
    
    # Dessiner les ennemis
    for ennemi in ennemis:
        x = ennemi.x * TAILLE_CASE - camera_offset[0]
        y = ennemi.y * TAILLE_CASE - camera_offset[1]
        
        # Calculer la distance entre le joueur et l'ennemi
        dx = ennemi.x - joueur_pos[0]
        dy = ennemi.y - joueur_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Vérifier si l'ennemi est dans le cercle proche
        if distance * TAILLE_CASE <= RAYON_VISION_PROCHE:
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), hopital):
                pygame.draw.rect(fenetre, ENNEMIES, (x, y, TAILLE_CASE, TAILLE_CASE))
        # Sinon, vérifier s'il est dans le cône de vision
        elif est_dans_cone(joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, cone_length):
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), hopital):
                pygame.draw.rect(fenetre, ENNEMIES, (x, y, TAILLE_CASE, TAILLE_CASE))

    # Victoire si le joueur atteint la sortie avec toutes les clés
    if hopital[pos_grille[0]][pos_grille[1]] == "S" and cles_collectees == NOMBRE_CLES:
        afficher_victoire()
        running = False

    # Dessiner le compteur de clés après avoir dessiné tout le reste
    dessiner_compteur_cles(fenetre, cles_collectees, NOMBRE_CLES)
    
    # Dessiner la barre d'endurance
    dessiner_barre_endurance(fenetre)
    
    pygame.display.flip()
    horloge.tick(FPS)  # Limiter à 60 FPS

pygame.quit()
