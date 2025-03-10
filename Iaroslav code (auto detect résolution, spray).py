import pygame
import random
import sys
import math
import os
from screeninfo import get_monitors  # Ajouter cette importation

# Initialisation de Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer module

# Charger les musiques
try:
    musique_poursuite = pygame.mixer.Sound("C:/Users/luiar/Downloads/projetNSI/OST/outlast_run.mp3")
    musique_poursuite.set_volume(0.5)  # Ajuster le volume à 50%
except:
    musique_poursuite = None

# Variables pour gérer l'état de la musique
est_en_poursuite = False
temps_perdu_vue = 0
DELAI_ARRET_MUSIQUE = 2000  # 2000 millisecondes = 2 secondes

# Détection de la résolution de l'écran
try:
    monitor = get_monitors()[0]  # Obtient le moniteur principal
    largeur = monitor.width
    hauteur = monitor.height
except:
    # Résolution par défaut si la détection échoue
    largeur = 1920
    hauteur = 1080

# Ajuster la taille des cases en fonction de la résolution
taille_case = int(min(largeur, hauteur) / 20)  # Ajuste la taille des cases proportionnellement

# Recalculer les dimensions du labyrinthe en fonction de la résolution
nombre_lignes = (hauteur // taille_case) * 8
nombre_colonnes = (largeur // taille_case) * 8

# Ajuster les paramètres de vision en fonction de la résolution
rayon_vision_proche = taille_case * 2  # Ajuste le rayon de vision proche
cone_longueur = min(largeur, hauteur) / 2  # Ajuste la longueur du cône de vision

# Couleurs utilisées dans le jeu
noir = (0, 0, 0)
blanc = (255, 255, 255)
gris = (128, 128, 128)  # Gris moyen
gris_fonce = (50, 50, 50)  # Pour les cases non sélectionnées
gris_clair = (150, 150, 150)  # Pour la case sélectionnée
bordeaux = (40, 0, 0)
ENNEMIES = (255, 0, 0)  # Rouge pour les ennemis
spray = (255, 165, 0)  # Couleur orange pour le spray au poivre
marron_spray = (139, 69, 19, 100)  # Marron avec transparence

# Load and scale player image
joueur_img = pygame.image.load("C:/Users/luiar/Downloads/projetNSI/texture/personnage.png")
joueur = pygame.transform.scale(joueur_img, (taille_case * 1.25, taille_case * 1.25))  # Scale to tile size
sortie = (0, 255, 0)
mur = (100, 40, 30)
sol = (115, 109, 115)
cle = (255, 223, 0)
ennemis = (255, 0, 0)

# Move this line up, before window creation
is_fullscreen = True  # Default to fullscreen

# Then create the window
fenetre = pygame.display.set_mode((largeur, hauteur), pygame.FULLSCREEN if is_fullscreen else pygame.RESIZABLE)
pygame.display.set_caption("Echoes of the Hollow")

# Horloge pour contrôler les FPS
horloge = pygame.time.Clock()

# Paramètres de jeu
nombre_cles = 3  
cles_collectees = 0  
nombre_ennemis = 5
vitesse_ennemis = 0.6 

# Paramètres de la vision
cone_angle = 60  # Angle du cône de vision en degrés

# Génération initiale
joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
camera_offset = [0, 0]

# Initialisation de l'angle de vue avec une valeur par défaut
angle_de_vue = 270  # 0 = droite, 90 = bas, 180 = gauche, 270 = haut

# Structure pour stocker les ennemis avec leurs positions et directions
ennemis = []  # Liste qui contiendra des dictionnaires pour chaque ennemi

# Ajouter ces variables après les autres paramètres du jeu
delai_mouvement = 100  # Délai en millisecondes entre chaque mouvement
dernier_mouvement = 0  # Pour suivre le temps du dernier mouvement

# Ajouter une variable pour suivre l'index de la case sélectionnée
index_case_selectionnee = 0

# Mettre à jour la liste des résolutions disponibles
REsolUTIONS = [
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
    (largeur, hauteur)  # Ajoute la résolution native
]
resolution_index = 0  # Index de la résolution sélectionnée

# Add near the top of the file with other constants
VIRTUAL_WIDTH = largeur  # Base resolution width
VIRTUAL_HEIGHT = hauteur  # Base resolution height

# Add these constants near the top with other settings
CROSSHAIR_SIZES = [3, 5, 7, 10]  # Different crosshair sizes
CROSSHAIR_STYLES = ["Croix", "Point", "Aucun"]  # Different crosshair styles
crosshair_size_index = 1  # Default to second size (5)
crosshair_style_index = 0  # Default to Cross

# Paramètres d'endurance
endurance_max = 100  # Endurance maximale
endurance_actuelle = endurance_max  # Endurance actuelle
taux_diminution = 0.5  # Réduit pour une diminution plus lente
taux_recuperation = 0.2  # Réduit pour une récupération plus lente
delai_mouvement_normal = 100  # Délai en millisecondes pour le mouvement normal
delai_mouvement_rapide = 40  # Délai en millisecondes pour le mouvement rapide

# Au début du fichier, avec les autres constantes
VITESSE_ENNEMIE_LENTE = 0.15  # Vitesse de patrouille (très lente)
VITESSE_ENNEMIE_POURSUITE = 0.4  # Vitesse de poursuite (plus rapide mais moins que le joueur)

# Ajouter aux paramètres de jeu
nombre_sprays = 2  # Nombre de sprays sur la map
sprays_collectes = 0  # Compteur de sprays dans l'inventaire

# Ajouter aux variables globales au début du fichier
spray_actif = False
temps_spray = 0
DUREE_AFFICHAGE_SPRAY = 500  # Durée d'affichage du spray en millisecondes

class Ennemi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.compteur_deplacement = 0
        self.cone_vision = 8
        self.angle_vision = 120
        # Nouvelles vitesses
        self.vitesse_patrouille = VITESSE_ENNEMIE_LENTE
        self.vitesse_poursuite = VITESSE_ENNEMIE_POURSUITE
        self.vitesse_actuelle = self.vitesse_patrouille
        # Variables pour la mémoire
        self.derniere_pos_joueur = None
        self.temps_memoire = 0
        self.duree_memoire_max = 180
        # Variables pour la patrouille
        self.pas_patrouille = 0
        self.max_pas_patrouille = random.randint(5, 10)
        self.ralenti = False
        self.temps_ralenti = 0
        self.vitesse_ralentie = VITESSE_ENNEMIE_LENTE * 0.5  # 50% plus lent

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
    global est_en_poursuite, temps_perdu_vue
    joueur_est_vu = False
    temps_actuel = pygame.time.get_ticks()
    
    for ennemi in ennemis:
        temps_actuel = pygame.time.get_ticks()
        
        # Gérer l'effet de ralentissement
        if ennemi.ralenti:
            if temps_actuel - ennemi.temps_ralenti >= 3000:  # 3 secondes
                ennemi.ralenti = False
                # Réinitialiser la vitesse normale
                ennemi.vitesse_actuelle = ennemi.vitesse_patrouille
            else:
                ennemi.vitesse_actuelle = 0.1  # Vitesse fixée à 0.1 quand ralenti
        
        voit_joueur = ennemi.peut_voir_joueur(joueur_pos, hopital)
        
        if voit_joueur and not ennemi.ralenti:  # Ne change la vitesse que si pas ralenti
            joueur_est_vu = True
            temps_perdu_vue = 0
            ennemi.vitesse_actuelle = ennemi.vitesse_poursuite
            ennemi.derniere_pos_joueur = joueur_pos[:]
            ennemi.temps_memoire = ennemi.duree_memoire_max
            
            ennemi.compteur_deplacement += ennemi.vitesse_actuelle
            if ennemi.compteur_deplacement >= 1:
                ennemi.compteur_deplacement = 0
                
                # Déplacement vers le joueur
                dx = joueur_pos[0] - ennemi.x
                dy = joueur_pos[1] - ennemi.y
                
                if abs(dx) > abs(dy):
                    nouveau_x = ennemi.x + (1 if dx > 0 else -1)
                    nouveau_y = ennemi.y
                else:
                    nouveau_x = ennemi.x
                    nouveau_y = ennemi.y + (1 if dy > 0 else -1)
                    
                if deplacement_valide(hopital, [nouveau_x, nouveau_y]):
                    ennemi.x = nouveau_x
                    ennemi.y = nouveau_y
                
        elif not ennemi.ralenti:  # Ne change la vitesse que si pas ralenti
            ennemi.vitesse_actuelle = ennemi.vitesse_patrouille
            ennemi.compteur_deplacement += ennemi.vitesse_actuelle
            
            if ennemi.compteur_deplacement >= 1:
                ennemi.compteur_deplacement = 0
                
                # Déplacement dans la direction actuelle
                nouveau_x = ennemi.x + ennemi.direction[0]
                nouveau_y = ennemi.y + ennemi.direction[1]
                
                if deplacement_valide(hopital, [nouveau_x, nouveau_y]):
                    ennemi.x = nouveau_x
                    ennemi.y = nouveau_y
                    ennemi.pas_patrouille += 1
                    
                    # Changer de direction après un certain nombre de pas
                    if ennemi.pas_patrouille >= ennemi.max_pas_patrouille:
                        ennemi.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                        ennemi.pas_patrouille = 0
                        ennemi.max_pas_patrouille = random.randint(5, 10)
                else:
                    # Si bloqué, changer de direction
                    ennemi.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                    ennemi.pas_patrouille = 0

    # Gestion de la musique de poursuite
    if joueur_est_vu:
        if not est_en_poursuite and musique_poursuite:
            pygame.mixer.music.pause()  # Pause la musique de fond
            musique_poursuite.play(-1)  # -1 pour jouer en boucle
        est_en_poursuite = True
        temps_perdu_vue = 0
    elif est_en_poursuite:
        if temps_perdu_vue == 0:
            # Premier moment où le joueur n'est plus vu
            temps_perdu_vue = temps_actuel
        elif temps_actuel - temps_perdu_vue >= DELAI_ARRET_MUSIQUE:
            # Arrêter la musique seulement après le délai
            if musique_poursuite:
                musique_poursuite.fadeout(1000)  # Fade out sur 1 seconde
                pygame.mixer.music.unpause()  # Reprend la musique de fond
            est_en_poursuite = False
            temps_perdu_vue = 0


def verifier_collision_ennemis(joueur_pos, ennemis):
    for ennemi in ennemis:
        if (abs(joueur_pos[0] - ennemi.x) < 1 and
                abs(joueur_pos[1] - ennemi.y) < 1):
            return True
    return False


def game_over():
    arreter_musiques()  # Stop current music
    musique_menu()  # Start menu music
    fenetre.fill(noir)
    texte = pygame.font.Font(None, 60).render("Game Over!", True, blanc)
    texte_rect = texte.get_rect(center=(largeur // 2, hauteur // 2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    pygame.time.delay(2000)  # Attendre 2 secondes
    return "menu"  # Retourner au menu


def appliquer_masque_vision(surface, position, angle, length):
    masque = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
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
            grille_x = int((ray_x + camera_offset[0]) / taille_case)
            grille_y = int((ray_y + camera_offset[1]) / taille_case)

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
    pygame.draw.circle(masque, (0, 0, 0, 0),
                       (int(x), int(y)), rayon_vision_proche)

    # Appliquer le masque sur l'écran
    surface.blit(masque, (0, 0))


def generer_hopital(nb_lignes, nb_colonnes):
    # Ajuste les dimensions pour garantir un labyrinthe valide
    nb_lignes = (nb_lignes // 3) * 3 + 1
    nb_colonnes = (nb_colonnes // 3) * 3 + 1
    hopital = [["#" for _ in range(nb_colonnes)] for _ in range(nb_lignes)]

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
                    hopital[y + i][x + j] = " "
        for nx, ny in voisins(x, y):
            if hopital[ny][nx] == "#":
                for i in range(-1, 2):
                    for j in range(-3, 4):
                        if 0 <= (y + ny) // 2 + i < nb_lignes and 0 <= (x + nx) // 2 + j < nb_colonnes:
                            hopital[(y + ny) // 2 + i][(x + nx) // 2 + j] = " "
                départ(nx, ny)

    # Commencer au centre du labyrinthe
    départ(nb_colonnes // 2, nb_lignes // 2)

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
    cases_vides = [(i, j) for i, ligne in enumerate(hopital)
                   for j, case in enumerate(ligne) if case == " "]
    for _ in range(nombre_cles):
        x, y = random.choice(cases_vides)
        cles.append((x, y))
        hopital[x][y] = "C"  # Ajoute une clé à cet emplacement
        cases_vides.remove((x, y))
    return cles


def est_dans_cone(joueur_pos, case_pos, angle, length):
    """Version optimisée de la vérification du cône"""
    dx = case_pos[0] - joueur_pos[0]
    dy = case_pos[1] - joueur_pos[1]
    distance = dx*dx + dy*dy  # Pas besoin de sqrt pour la comparaison

    if distance > (length/taille_case) * (length/taille_case):
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
    if distance * taille_case <= rayon_vision_proche:
        # Vérifier s'il n'y a pas de mur entre
        return not a_mur_entre(joueur_pos, case_pos, hopital)

    # Sinon, vérifier si c'est dans le cône de vision
    if not est_dans_cone(joueur_pos, case_pos, angle_de_vue, cone_longueur):
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
    """Version optimisée du rendu"""
    # Create a virtual surface at base resolution
    virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    virtual_surface.fill(noir)

    # Calculer les limites visibles avec une marge
    marge = 2
    debut_x = max(0, int(camera_offset[0] // taille_case) - marge)
    debut_y = max(0, int(camera_offset[1] // taille_case) - marge)
    fin_x = min(len(hopital[0]), int((camera_offset[0] + largeur) // taille_case) + marge)
    fin_y = min(len(hopital), int((camera_offset[1] + hauteur) // taille_case) + marge)

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
            couleur = mur if hopital[i][j] == "#" else sol
            pygame.draw.rect(temp_surface, couleur,
                             (x, y, taille_case, taille_case))

    virtual_surface.blit(temp_surface, (0, 0))

    # Appliquer le masque de vision
    joueur_centre = (
        joueur_pos[0] * taille_case - cam_x + taille_case // 2,
        joueur_pos[1] * taille_case - cam_y + taille_case // 2
    )
    appliquer_masque_vision(virtual_surface, joueur_centre, angle_de_vue, cone_longueur)

    # Rendu des objets spéciaux
    for i in range(debut_y, fin_y):
        y = i * taille_case - cam_y
        for j in range(debut_x, fin_x):
            case = hopital[i][j]
            if case in ["S", "C", "P"]:  # P pour Pepper spray
                if est_visible(joueur_pos, (j, i), hopital):
                    x = j * taille_case - cam_x
                    if case == "S":
                        couleur = sortie  # Vert pour la sortie
                    elif case == "C":
                        couleur = cle  # Jaune pour les clés
                    elif case == "P":
                        couleur = spray  # Orange pour le spray
                    pygame.draw.rect(virtual_surface, couleur,
                                     (x, y, taille_case, taille_case))

    # Dessiner le joueur
    if joueur:
        # Calculate centered position by accounting for image size
        joueur_x = joueur_pos[0] * taille_case - camera_offset[0] - (joueur.get_width() - taille_case) // 2
        joueur_y = joueur_pos[1] * taille_case - camera_offset[1] - (joueur.get_height() - taille_case) // 2
        
        # Rotate image to face mouse
        # Convert angle_de_vue to match Pygame's rotation (0° is up, clockwise)
        rotation_angle = -(angle_de_vue + 90)  # +90 because original image faces up
        joueur_rotated = pygame.transform.rotate(joueur, rotation_angle)
        
        # Recalculate position to keep rotation centered
        joueur_x -= (joueur_rotated.get_width() - joueur.get_width()) // 2
        joueur_y -= (joueur_rotated.get_height() - joueur.get_height()) // 2
        
        virtual_surface.blit(joueur_rotated, (joueur_x, joueur_y))
    else:
        # Fallback to rectangle if image loading failed
        pygame.draw.rect(virtual_surface, joueur, (
            joueur_pos[0] * taille_case - camera_offset[0],
            joueur_pos[1] * taille_case - camera_offset[1],
            taille_case, taille_case
        ))

    # At the end of the function, scale the virtual surface to the actual window size
    scaled_surface = pygame.transform.scale(virtual_surface, (largeur, hauteur))
    fenetre.blit(scaled_surface, (0, 0))

# Vérification de la validité du déplacement


def deplacement_valide(hopital, pos):
    x, y = pos
    if 0 <= y < len(hopital) and 0 <= x < len(hopital[0]):
        return hopital[y][x] != "#"
    return False

# Fonction de victoire


def afficher_victoire():
    arreter_musiques()
    fenetre.fill(noir)
    texte = pygame.font.Font(None, 60).render("Victoire !", True, blanc)
    texte_rect = texte.get_rect(center=(largeur // 2, hauteur // 2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    pygame.time.delay(3000)


def afficher_credits():
    # Constants for animation
    SCROLL_SPEED = 5  # Reduced for smoother scrolling
    TITLE_SIZE = 100
    NAME_SIZE = 80
    ROLE_SIZE = 50
    SPACING = 120      # Regular spacing
    SPACING_2 = 30     # Small spacing (between name and role)
    SPACING_3 = 200    # Large spacing (after title)
    
    # Credits content with roles
    credits_data = [
        ("Développeurs :", TITLE_SIZE),
        ("", SPACING_3),  # Large spacing after title
        ("Iaroslav Lushcheko", NAME_SIZE),
        ("", SPACING_2),  # Small spacing between name and role
        ("Programmation, Game Design", ROLE_SIZE),
        ("", SPACING),    # Regular spacing between developers
        ("Eliott Raulet", NAME_SIZE),
        ("", SPACING_2),  # Small spacing between name and role
        ("Level Design, Game Mechanics", ROLE_SIZE),
        ("", SPACING),    # Regular spacing between developers
        ("Mohamed El Mekkawy", NAME_SIZE),
        ("", SPACING_2),  # Small spacing between name and role
        ("UI/UX, Game Systems", ROLE_SIZE),
        ("", SPACING),    # Regular spacing between developers
        ("Ugo Guillemart", NAME_SIZE),
        ("", SPACING_2),  # Small spacing between name and role
        ("Sound Design, Testing", ROLE_SIZE),
        ("", SPACING_3),  # Extra spacing at the end
    ]
    
    # Calculate total height of all text
    total_height = sum([size if text == "" else 80 for text, size in credits_data])
    y_offset = float(hauteur)  # Use float for smoother scrolling
    
    while True:
        fenetre.fill(noir)
        
        current_y = int(y_offset)  # Convert to int only for drawing
        
        # Draw each credit entry
        for text, size in credits_data:
            if text:  # Only render non-empty strings
                texte = pygame.font.Font("C:/Users/luiar/Downloads/projetNSI/HelpMe.ttf", size).render(text, True, blanc)
                texte_rect = texte.get_rect(center=(largeur // 2, current_y))
                
                # Only draw if within screen bounds with some margin
                if -50 <= current_y <= hauteur + 50:
                    # Add glow effect for titles
                    if size == TITLE_SIZE:
                        glow = pygame.font.Font("C:/Users/luiar/Downloads/projetNSI/HelpMe.ttf", size).render(text, True, (100, 100, 100))
                        glow_rect = glow.get_rect(center=(largeur // 2, current_y))
                        fenetre.blit(glow, (glow_rect.x + 2, glow_rect.y + 2))
                    
            fenetre.blit(texte, texte_rect)

            # Use the actual spacing value from the tuple
            current_y += size if text == "" else 80
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Only handle left click, ignore scroll
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        # Automatic scroll
        y_offset -= SCROLL_SPEED
        
        if y_offset < -total_height:
            y_offset = float(hauteur)
        
        pygame.display.flip()
        horloge.tick(60)


def bords_arrondis(surface, color, rect, radius):
    """Draw a rectangle with rounded corners"""
    x, y, width, height = rect

    # Dessiner des cercles remplis pour les coins
    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(
        surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius,
                       y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius,
                       y + height - radius), radius)

    # Dessiner des rectangles pour remplir la surface
    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))


def afficher_menu():
    pygame.mouse.set_visible(True)  # Show cursor in main menu
    musique_menu()  # Commencer la musique du menu
    # Charger l'image de fond
    background = pygame.image.load("C:/Users/luiar/Downloads/projetNSI/texture/fond_menu.png")
    # Ajuster la taille de l'image pour faire la taille de la fenetre
    background = pygame.transform.scale(background, (largeur, hauteur))

    while True:
        # Draw background if available, otherwise fill with black
        if background:
            fenetre.blit(background, (0, 0))
        else:
            fenetre.fill(noir)

        # Titre
        titre = pygame.font.Font(
            "C:/Users/luiar/Downloads/projetNSI/November.ttf", 150).render("Echoes of the Hollow", True, blanc)
        fenetre.blit(
            titre, (largeur // 2 - titre.get_width() // 2, hauteur - 900))

        # Récupérer la position de la souris
        souris_x, souris_y = pygame.mouse.get_pos()

        # Boutons avec leurs dimensions
        bouton_jouer = pygame.Rect(largeur // 2 - 200, 530, 400, 80)
        bouton_parametres = pygame.Rect(largeur // 2 - 200, 630, 400, 80)
        bouton_crédits = pygame.Rect(largeur // 2 - 200, 730, 400, 80)
        bouton_quitter = pygame.Rect(largeur // 2 - 200, 830, 400, 80)

        # Liste des boutons et leurs textes
        boutons = [
            (bouton_jouer, "Jouer", 50),
            (bouton_parametres, "Paramètres", 50),
            (bouton_crédits, "Crédits", 50),
            (bouton_quitter, "Quitter", 50),
        ]

        for bouton, texte, taille_texte in boutons:
            # Vérifier si la souris est sur le bouton
            if bouton.collidepoint(souris_x, souris_y):
                couleur = (255, 0, 0)  # Rouge
                # Agrandir légèrement le bouton
                bouton = bouton.inflate(20, 20)
            else:
                couleur = bordeaux

            # Dessiner le bouton arrondi
            # 15 est le rayon de courbure
            bords_arrondis(fenetre, couleur, bouton, 15)

            texte_rendu = pygame.font.Font(
                "C:/Users/luiar/Downloads/projetNSI/HelpMe.ttf", 35).render(texte, True, blanc)
            fenetre.blit(
                texte_rendu,
                (bouton.centerx - texte_rendu.get_width() // 2,
                 bouton.centery - texte_rendu.get_height() // 2),
            )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:  # Only buttons 1-3, ignore scroll
                if bouton_jouer.collidepoint(event.pos):
                    return
                if bouton_crédits.collidepoint(event.pos):
                    afficher_credits()
                if bouton_parametres.collidepoint(event.pos):
                    afficher_parametres()
                if bouton_quitter.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

# Afficher le menu pause
def afficher_menu_pause():
    pygame.mouse.set_visible(True)  # Show cursor in pause menu
    global resolution_index, largeur, hauteur, fenetre
    
    # Load the background image
    background = pygame.image.load("C:/Users/luiar/Downloads/projetNSI/texture/background_1.png")  # Ensure the path is correct
    background = pygame.transform.scale(background, (largeur, hauteur))  # Scale to fit the window

    while True:
        # Draw the background image instead of filling with black
        fenetre.blit(background, (0, 0))

        # Title at the top
        titre = pygame.font.Font("C:/Users/luiar/Downloads/projetNSI/November.ttf", 100).render("Echoes of the Hollow", True, blanc)
        titre_rect = titre.get_rect(center=(largeur // 2, hauteur // 6))
        fenetre.blit(titre, titre_rect)

        # Return button at top left with arrow
        bouton_retour = pygame.Rect(20, 20, 200, 60)  # Made wider again to fit text
        if bouton_retour.collidepoint(pygame.mouse.get_pos()):
            couleur_retour = (255, 0, 0)
            bouton_retour = bouton_retour.inflate(20, 20)
        else:
            couleur_retour = bordeaux
        bords_arrondis(fenetre, couleur_retour, bouton_retour, 15)
        
        # Draw arrow and text separately
        texte_arrow = pygame.font.Font("C:/Users/luiar/Downloads/projetNSI/Arrows.ttf", 40).render("R", True, blanc)
        texte_retour = pygame.font.Font("C:/Users/luiar/Downloads/projetNSI/HelpMe.ttf", 30).render("Retour", True, blanc)
        
        # Position arrow and text
        fenetre.blit(texte_arrow, (bouton_retour.x + 15, bouton_retour.centery - texte_arrow.get_height() // 2))
        fenetre.blit(texte_retour, (bouton_retour.x + 45, bouton_retour.centery - texte_retour.get_height() // 2))

        # Centered menu buttons with consistent gaps (moved up)
        button_gap = 120  # Consistent gap between buttons
        start_y = hauteur // 3  # Starting Y position moved up (was hauteur // 2 - 150)
        boutons = [
            (pygame.Rect(largeur // 2 - 250, start_y, 500, 90), "Continuer", 40),
            (pygame.Rect(largeur // 2 - 250, start_y + button_gap, 500, 90), "Recommencer", 40),
            (pygame.Rect(largeur // 2 - 250, start_y + button_gap * 2, 500, 90), "Paramètres", 40),
            (pygame.Rect(largeur // 2 - 250, start_y + button_gap * 3, 500, 90), "Menu Principal", 40),
            (pygame.Rect(largeur // 2 - 250, start_y + button_gap * 4, 500, 90), "Quitter", 40),
        ]

        souris_x, souris_y = pygame.mouse.get_pos()

        for bouton, texte, taille_texte in boutons:
            if bouton.collidepoint(souris_x, souris_y):
                couleur = (255, 0, 0)
                bouton = bouton.inflate(20, 20)
            else:
                couleur = bordeaux

            bords_arrondis(fenetre, couleur, bouton, 15)
            texte_rendu = pygame.font.Font("C:/Users/luiar/Downloads/projetNSI/HelpMe.ttf", taille_texte).render(texte, True, blanc)
            fenetre.blit(texte_rendu, (bouton.centerx - texte_rendu.get_width() // 2,
                                      bouton.centery - texte_rendu.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:
                if bouton_retour.collidepoint(event.pos):
                    pygame.mouse.set_visible(False)
                    return "continuer"
                for bouton, texte, _ in boutons:
                    if bouton.collidepoint(event.pos):
                        if texte == "Continuer":
                            pygame.mouse.set_visible(False)
                            return "continuer"
                        elif texte == "Recommencer":
                            return "recommencer"
                        elif texte == "Paramètres":
                            afficher_parametres()
                        elif texte == "Menu Principal":
                            return "menu"
                        elif texte == "Quitter":
                            pygame.quit()
                            sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

# Placer cette fonction après les autres définitions de fonctions et avant la boucle principale


def dessiner_compteur_cles(surface, cles_collectees, nombre_cles_total):
    # Position du compteur (coin supérieur droit)
    marge = 20
    taille_icone = 30
    espacement = 10

    # Dessiner le fond du compteur
    fond_rect = pygame.Rect(
        largeur - (marge + taille_icone + 80),
        marge,
        taille_icone + 80,
        taille_icone + 10
    )
    pygame.draw.rect(surface, bordeaux, fond_rect)
    pygame.draw.rect(surface, blanc, fond_rect, 2)  # Bordure blanche

    # Dessiner l'icône de clé
    icone_cle = pygame.Rect(
        largeur - (marge + taille_icone),
        marge + 5,
        taille_icone,
        taille_icone
    )
    pygame.draw.rect(surface, cle, icone_cle)

    # Afficher le texte du compteur
    texte = f"{cles_collectees}/{nombre_cles_total}"
    police = pygame.font.Font(None, 36)
    surface_texte = police.render(texte, True, blanc)
    pos_texte = (
        largeur - (marge + taille_icone + espacement +
                   surface_texte.get_width()),
        marge + 8
    )
    surface.blit(surface_texte, pos_texte)

# Modifier la fonction pour dessiner l'inventaire


def dessiner_inventaire(surface):
    # Position et taille de l'inventaire
    inv_x = 20  # Position à gauche
    inv_y = hauteur - 70  # Position en bas
    case_taille = 50
    espacement = 10
    
    # Dessiner les cases d'inventaire horizontalement
    for i in range(5):  # 5 cases d'inventaire
        x = inv_x + (case_taille + espacement) * i  # Déplacement horizontal
        pygame.draw.rect(surface, gris_fonce, (x, inv_y, case_taille, case_taille))
        if i == index_case_selectionnee:
            pygame.draw.rect(surface, gris_clair, (x, inv_y, case_taille, case_taille), 2)
        else:
            pygame.draw.rect(surface, gris, (x, inv_y, case_taille, case_taille), 1)
        
        # Afficher les sprays dans l'inventaire
        if i == 0 and sprays_collectes > 0:
            pygame.draw.rect(surface, spray, (x + 5, inv_y + 5, case_taille - 10, case_taille - 10))
            texte = pygame.font.Font(None, 20).render(str(sprays_collectes), True, blanc)
            surface.blit(texte, (x + case_taille - 15, inv_y + case_taille - 15))


def afficher_parametres():
    global resolution_index, largeur, hauteur, fenetre, crosshair_size_index, crosshair_style_index, is_fullscreen
    
    selected_section = 0  # 0 = Display, 1 = Crosshair
    sections = ["Affichage", "Réticule"]
    
    # Add these variables at the start of the function
    slider_rect = pygame.Rect(0, 0, 200, 10)
    slider_pos = CROSSHAIR_SIZES[crosshair_size_index]
    typing_active = False
    text_input = str(slider_pos)
    dragging_slider = False  # Initialize dragging_slider variable
    
    while True:
        fenetre.fill(noir)
        center_x = largeur // 2  # Move this line here, before any section checks

        # Center sections at the top
        section_total_width = sum([200 for _ in sections])
        section_start_x = (largeur - section_total_width) // 2

        # Draw sections at the top
        for i, section in enumerate(sections):
            color = blanc if i == selected_section else gris
            texte = pygame.font.Font(None, 40).render(section, True, color)
            text_rect = texte.get_rect(center=(section_start_x + i * 200 + 100, 50))
            fenetre.blit(texte, text_rect)

        # Display Settings Section
        if selected_section == 0:
            # Resolutions list
            for i, (width, height) in enumerate(REsolUTIONS):
                resolution_texte = f"{width} x {height}"
                if is_fullscreen:
                    color = (100, 100, 100)  # Dark gray for disabled state
                else:
                    color = blanc if i == resolution_index else gris
                texte = pygame.font.Font(None, 40).render(resolution_texte, True, color)
                text_rect = texte.get_rect(center=(largeur // 2, 150 + i * 50))
                fenetre.blit(texte, text_rect)
            
            # Fullscreen toggle
            fullscreen_text = "Plein écran: " + ("Oui" if is_fullscreen else "Non")
            color = blanc if is_fullscreen else gris
            texte = pygame.font.Font(None, 40).render(fullscreen_text, True, color)
            text_rect = texte.get_rect(center=(largeur // 2, 150 + len(REsolUTIONS) * 50))
            fenetre.blit(texte, text_rect)

        # Crosshair Settings Section
        elif selected_section == 1:
            center_x = largeur // 2
            preview_x = center_x

            # Draw "Taille" text and controls
            texte = pygame.font.Font(None, 40).render("Taille:", True, blanc)
            text_rect = texte.get_rect(center=(center_x - 150, 150))
            fenetre.blit(texte, text_rect)

            # Draw slider (grayed out if "Aucun" is selected)
            slider_rect.centerx = center_x
            slider_rect.centery = 150
            slider_color = (50, 50, 50) if CROSSHAIR_STYLES[crosshair_style_index] == "Aucun" else gris
            pygame.draw.rect(fenetre, slider_color, slider_rect)
            
            # Draw slider handle
            handle_pos = slider_rect.left + (slider_pos - 1) * (slider_rect.width / 20)
            if CROSSHAIR_STYLES[crosshair_style_index] != "Aucun":
                pygame.draw.circle(fenetre, blanc, (handle_pos, slider_rect.centery), 8)
            
            # Draw text input (without border)
            font = pygame.font.Font(None, 40)
            text_surface = font.render(text_input, True, blanc if CROSSHAIR_STYLES[crosshair_style_index] != "Aucun" else (50, 50, 50))
            text_rect = text_surface.get_rect(center=(center_x + 150, 150))
            fenetre.blit(text_surface, text_rect)

            # Draw "Style" text and styles
            style_text = pygame.font.Font(None, 40).render("Style:", True, blanc)
            style_rect = style_text.get_rect(center=(center_x - 150, 220))
            fenetre.blit(style_text, style_rect)

            # Crosshair style selection
            for i, style in enumerate(CROSSHAIR_STYLES):
                color = blanc if i == crosshair_style_index else gris
                texte = pygame.font.Font(None, 40).render(style, True, color)
                text_rect = texte.get_rect(center=(center_x, 220 + i * 50))
                fenetre.blit(texte, text_rect)

            # Add preview section with bigger gap
            preview_y = 500  # Increased from 400
            preview_text = pygame.font.Font(None, 40).render("Aperçu", True, blanc)
            preview_text_rect = preview_text.get_rect(center=(center_x, preview_y - 50))
            fenetre.blit(preview_text, preview_text_rect)

            # Preview box
            preview_size = 150
            border_padding = 10
            outer_rect = pygame.Rect(preview_x - preview_size//2 - border_padding, 
                                   preview_y - preview_size//2 - border_padding,
                                   preview_size + border_padding*2, 
                                   preview_size + border_padding*2)
            pygame.draw.rect(fenetre, gris, outer_rect)
            preview_rect = pygame.Rect(preview_x - preview_size//2, preview_y - preview_size//2, 
                                     preview_size, preview_size)
            pygame.draw.rect(fenetre, sol, preview_rect)
            pygame.draw.rect(fenetre, blanc, preview_rect, 1)

            # Draw crosshair preview
            if CROSSHAIR_STYLES[crosshair_style_index] == "Croix":
                pygame.draw.line(fenetre, blanc, (preview_x - slider_pos, preview_y), 
                               (preview_x + slider_pos, preview_y))
                pygame.draw.line(fenetre, blanc, (preview_x, preview_y - slider_pos), 
                               (preview_x, preview_y + slider_pos))
            elif CROSSHAIR_STYLES[crosshair_style_index] == "Point":
                pygame.draw.circle(fenetre, blanc, (preview_x, preview_y), slider_pos)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_LEFT and selected_section > 0:
                    selected_section -= 1
                elif event.key == pygame.K_RIGHT and selected_section < len(sections) - 1:
                    selected_section += 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Section selection
                if mouse_y < 100:  # Click in the section headers area
                    for i in range(len(sections)):
                        if section_start_x + i * 200 <= mouse_x <= section_start_x + (i + 1) * 200:
                            selected_section = i

                elif selected_section == 0:  # Display settings
                    # Resolution selection - only process if not in fullscreen
                    if not is_fullscreen:
                        for i in range(len(REsolUTIONS)):
                            if 150 <= mouse_y <= 150 + len(REsolUTIONS) * 50:
                                click_y = (mouse_y - 150) // 50
                                if click_y < len(REsolUTIONS):
                                    resolution_index = click_y
                                    largeur, hauteur = REsolUTIONS[resolution_index]
                                    fenetre = pygame.display.set_mode((largeur, hauteur), pygame.RESIZABLE)
                                    os.environ['SDL_VIDEO_CENTERED'] = '1'
                    
                    # Fullscreen toggle
                    if 150 + len(REsolUTIONS) * 50 - 25 <= mouse_y <= 150 + len(REsolUTIONS) * 50 + 25:
                        is_fullscreen = not is_fullscreen
                        flags = pygame.FULLSCREEN if is_fullscreen else pygame.RESIZABLE
                        fenetre = pygame.display.set_mode((largeur, hauteur), flags)

            if selected_section == 1:  # Crosshair settings
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    # Handle slider click/drag
                    if slider_rect.collidepoint(event.pos) and CROSSHAIR_STYLES[crosshair_style_index] != "Aucun":
                        dragging_slider = True
                        # Update slider position immediately on click
                        slider_pos = (mouse_x - slider_rect.left) / slider_rect.width * 20 + 1
                        slider_pos = max(1, min(20, slider_pos))
                        text_input = str(int(slider_pos))
                    # Style selection
                    for i, style in enumerate(CROSSHAIR_STYLES):
                        style_y = 220 + i * 50
                        if abs(mouse_x - center_x) < 100 and abs(mouse_y - style_y) < 25:
                            crosshair_style_index = i
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging_slider = False
                elif event.type == pygame.MOUSEMOTION and dragging_slider:
                    mouse_x = event.pos[0]
                    if slider_rect.left <= mouse_x <= slider_rect.right:
                        slider_pos = (mouse_x - slider_rect.left) / slider_rect.width * 20 + 1
                        slider_pos = max(1, min(20, slider_pos))
                        text_input = str(int(slider_pos))

        # Update crosshair size from slider
        crosshair_size_index = min(len(CROSSHAIR_SIZES) - 1, 
                                 max(0, int((slider_pos - 1) / 5)))

        pygame.display.flip()

# Add these functions after other function definitions


def musique_menu():
    pygame.mixer.music.load("C:/Users/luiar/Downloads/projetNSI/OST/S.T.A.L.K.E.R..mp3")  # Ensure the path is correct
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


def musique_fond():
    pygame.mixer.music.load("C:/Users/luiar/Downloads/projetNSI/OST/Amnesia_02.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


def arreter_musiques():
    global est_en_poursuite, temps_perdu_vue
    if musique_poursuite:
        musique_poursuite.stop()
    pygame.mixer.stop()
    est_en_poursuite = False
    temps_perdu_vue = 0


def placer_sprays(hopital, nombre_sprays):
    cases_vides = [(j, i) for i, ligne in enumerate(hopital)
                   for j, case in enumerate(ligne) if case == " "]
    for _ in range(nombre_sprays):
        if cases_vides:
            x, y = random.choice(cases_vides)
            hopital[y][x] = "P"  # P pour Pepper spray au lieu de S
            cases_vides.remove((x, y))

def redimensionner_jeu(nouvelle_largeur, nouvelle_hauteur):
    global largeur, hauteur, taille_case, nombre_lignes, nombre_colonnes
    
    # Mettre à jour les dimensions de la fenêtre
    largeur = nouvelle_largeur
    hauteur = nouvelle_hauteur
    
    # Recalculer la taille des cases
    taille_case = int(min(largeur, hauteur) / 20)
    
    # Recalculer les dimensions du labyrinthe
    nombre_lignes = (hauteur // taille_case) * 2
    nombre_colonnes = (largeur // taille_case) * 2
    
    # Générer un nouveau labyrinthe avec les nouvelles dimensions
    nouveau_hopital = generer_hopital(nombre_lignes, nombre_colonnes)
    
    # Replacer les objets dans le nouveau labyrinthe
    placer_cles(nouveau_hopital, nombre_cles)
    placer_sprays(nouveau_hopital, nombre_sprays)
    
    return nouveau_hopital

# Ensuite, la génération des objets
hopital = generer_hopital(nombre_lignes, nombre_colonnes)
cles = placer_cles(hopital, nombre_cles)
placer_sprays(hopital, nombre_sprays)
ennemis = initialiser_ennemis(hopital, nombre_ennemis)

# Placer après les autres définitions de fonctions (comme deplacer_ennemis, verifier_collision_ennemis, etc.)
# et avant la boucle principale du jeu

def dessiner_cone_spray(surface, position, angle, length):
    masque = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    
    x, y = position
    angle_spray = 30  # Angle du cône plus fin (30 degrés)
    start_angle = math.radians(angle - angle_spray / 2)
    end_angle = math.radians(angle + angle_spray / 2)

    # Points pour le polygone du spray
    points = [(x, y)]  # Point de départ (position du joueur)

    # Pour chaque rayon du cône
    steps = 180  # Plus de précision pour un rendu plus lisse
    for i in range(steps + 1):
        theta = start_angle + i * (end_angle - start_angle) / steps
        ray_x = x + length * math.cos(theta)
        ray_y = y + length * math.sin(theta)
        points.append((ray_x, ray_y))

    # Dessiner le polygone du spray
    if len(points) > 2:
        pygame.draw.polygon(masque, marron_spray, points)

    # Appliquer le masque sur l'écran
    surface.blit(masque, (0, 0))

def utiliser_spray(joueur_pos, angle_de_vue, ennemis, hopital):
    global sprays_collectes, spray_actif, temps_spray
    if sprays_collectes <= 0:
        return
    
    spray_actif = True
    temps_spray = pygame.time.get_ticks()
    
    # Paramètres du cône de spray
    portee_spray = 5 * taille_case  # Portée du spray en pixels
    
    # Pour chaque ennemi
    for ennemi in ennemis:
        # Vérifier si l'ennemi est dans le cône
        if est_dans_cone(joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, portee_spray):
            # Vérifier s'il n'y a pas de mur entre le joueur et l'ennemi
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), hopital):
                # Ralentir l'ennemi
                ennemi.ralenti = True
                ennemi.temps_ralenti = pygame.time.get_ticks()
                ennemi.vitesse_actuelle = 0.1  # Vitesse ralentie fixée à 0.1
    
    sprays_collectes -= 1

# Boucle principale
afficher_menu()
pygame.mouse.set_visible(False)  # Hide cursor during gameplay
musique_fond()  # Start game music
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.mouse.set_visible(True)  # Show cursor in menu
                choix = afficher_menu_pause()
                pygame.mouse.set_visible(False)  # Hide cursor when returning to game
                if choix == "recommencer":
                    hopital = generer_hopital(nombre_lignes, nombre_colonnes)
                    cles = placer_cles(hopital, nombre_cles)
                    placer_sprays(hopital, nombre_sprays)
                    bandages_collectes = 0  # Réinitialiser le compteur
                    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
                    cles_collectees = 0
                    ennemis = initialiser_ennemis(hopital, nombre_ennemis)
                    arreter_musiques()  # Arrêter toutes les musiques
                    musique_fond()  # Relancer la musique de fond du jeu
                elif choix == "menu":
                    # Réinitialiser le jeu
                    hopital = generer_hopital(nombre_lignes, nombre_colonnes)
                    cles = placer_cles(hopital, nombre_cles)
                    placer_sprays(hopital, nombre_sprays)
                    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
                    cles_collectees = 0
                    ennemis = initialiser_ennemis(hopital, nombre_ennemis)
                    # Retourner au menu
                    afficher_menu()
                    arreter_musiques()  # Arrêter la musique du menu
                    musique_fond()  # Démarrer la musique du jeu
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                index_case_selectionnee = max(0, index_case_selectionnee - 1)
            elif event.button == 5:  # Mouse wheel down
                index_case_selectionnee = min(4, index_case_selectionnee + 1)
            if event.button == 1:  # Clic gauche
                utiliser_spray(joueur_pos, angle_de_vue, ennemis, hopital)
        if event.type == pygame.VIDEORESIZE and not is_fullscreen:
            largeur, hauteur = event.size
            fenetre = pygame.display.set_mode((largeur, hauteur), pygame.RESIZABLE)
            hopital = redimensionner_jeu(largeur, hauteur)
            # Réinitialiser la position du joueur et des ennemis
            joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
            ennemis = initialiser_ennemis(hopital, nombre_ennemis)

    # Obtenir la position de la souris
    souris_x, souris_y = pygame.mouse.get_pos()

    # Calculer la position du joueur à l'écran
    joueur_ecran_x = joueur_pos[0] * taille_case - \
        camera_offset[0] + taille_case // 2
    joueur_ecran_y = joueur_pos[1] * taille_case - \
        camera_offset[1] + taille_case // 2

    # Calculer l'angle entre le joueur et la souris
    dx = souris_x - joueur_ecran_x
    dy = souris_y - joueur_ecran_y
    angle_de_vue = math.degrees(math.atan2(dy, dx))  # Direct angle calculation without smoothing

    # Obtenir les touches pressées
    touches = pygame.key.get_pressed()
    nouvelle_pos = joueur_pos[:]

    # Gestion de l'endurance et de la vitesse
    if touches[pygame.K_LSHIFT] or touches[pygame.K_RSHIFT]:
        if endurance_actuelle > 0:
            delai_mouvement = delai_mouvement_rapide
            endurance_actuelle = max(0, endurance_actuelle - taux_diminution)
        else:
            delai_mouvement = delai_mouvement_normal
    else:
        delai_mouvement = delai_mouvement_normal
        endurance_actuelle = min(endurance_max, endurance_actuelle + taux_recuperation)

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
    if deplacement_valide(hopital, nouvelle_pos):
        joueur_pos = nouvelle_pos

    # Mise à jour de la caméra pour suivre le joueur
    camera_offset[0] = joueur_pos[0] * taille_case - largeur // 2
    camera_offset[1] = joueur_pos[1] * taille_case - hauteur // 2

    # Vérifier la collision avec les ennemis
    if verifier_collision_ennemis(joueur_pos, ennemis):
        if game_over() == "menu":
            # Réinitialiser le jeu
            hopital = generer_hopital(nombre_lignes, nombre_colonnes)
            cles = placer_cles(hopital, nombre_cles)
            placer_sprays(hopital, nombre_sprays)
            joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
            cles_collectees = 0
            ennemis = initialiser_ennemis(hopital, nombre_ennemis)
            # Retourner au menu
            afficher_menu()
            arreter_musiques()  # Arrêter la musique du menu
            musique_fond()  # Démarrer la musique du jeu

    # Dessiner l'hôpital
    dessiner_hopital(hopital, joueur_pos, camera_offset)

    # Dessiner l'inventaire
    dessiner_inventaire(fenetre)

    # Dessiner la barre d'endurance
    barre_endurance_longueur = 200  # Longueur de la barre d'endurance
    barre_endurance_hauteur = 20  # Hauteur de la barre d'endurance
    barre_endurance_x = 10  # Position X de la barre
    barre_endurance_y = 10  # Position Y de la barre
    
    # Couleurs pour la barre d'endurance
    couleur_fond = (139, 0, 0)  # Rouge foncé pour le fond
    couleur_endurance = (50, 205, 50)  # Vert clair pour l'endurance
    couleur_bordure = (255, 255, 255)  # Blanc pour la bordure
    
    # Dessiner le fond de la barre
    pygame.draw.rect(fenetre, couleur_fond, (barre_endurance_x, barre_endurance_y, 
                    barre_endurance_longueur, barre_endurance_hauteur))
    
    # Dessiner la barre d'endurance actuelle
    longueur_actuelle = int(barre_endurance_longueur * (endurance_actuelle / endurance_max))
    pygame.draw.rect(fenetre, couleur_endurance, (barre_endurance_x, barre_endurance_y,
                    longueur_actuelle, barre_endurance_hauteur))

    # Dessiner la bordure
    pygame.draw.rect(fenetre, couleur_bordure, (barre_endurance_x, barre_endurance_y,
                    barre_endurance_longueur, barre_endurance_hauteur), 2)

    # Collecte des clés
    if hopital[joueur_pos[1]][joueur_pos[0]] == "C":
        cles_collectees += 1
        hopital[joueur_pos[1]][joueur_pos[0]] = " "

    # Collecte du spray
    if hopital[joueur_pos[1]][joueur_pos[0]] == "P":  # P pour Pepper spray
        sprays_collectes += 1
        hopital[joueur_pos[1]][joueur_pos[0]] = " "

    # Déplacer les ennemis
    deplacer_ennemis(hopital, ennemis, joueur_pos)

    # Dessiner les ennemis
    for ennemi in ennemis:
        x = ennemi.x * taille_case - camera_offset[0]
        y = ennemi.y * taille_case - camera_offset[1]
        
        # Calculer la distance entre le joueur et l'ennemi
        dx = ennemi.x - joueur_pos[0]
        dy = ennemi.y - joueur_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Vérifier si l'ennemi est dans le cercle proche
        if distance * taille_case <= rayon_vision_proche:
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), hopital):
                pygame.draw.rect(fenetre, ENNEMIES, (x, y, taille_case, taille_case))
        # Sinon, vérifier s'il est dans le cône de vision
        elif est_dans_cone(joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, cone_longueur):
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), hopital):
                pygame.draw.rect(fenetre, ENNEMIES, (x, y, taille_case, taille_case))

    # Victoire si le joueur atteint la sortie avec toutes les clés
    if hopital[joueur_pos[1]][joueur_pos[0]] == "S" and cles_collectees == nombre_cles:
        arreter_musiques()
        afficher_victoire()
        running = False

    # Dessiner le compteur de clés après avoir dessiné tout le reste
    dessiner_compteur_cles(fenetre, cles_collectees, nombre_cles)

    # Draw custom cursor based on selected style
    if not pygame.mouse.get_visible():
        mouse_x, mouse_y = pygame.mouse.get_pos()
        size = CROSSHAIR_SIZES[crosshair_size_index]
        
        if CROSSHAIR_STYLES[crosshair_style_index] == "Croix":
            pygame.draw.line(fenetre, blanc, (mouse_x - size, mouse_y), (mouse_x + size, mouse_y))
            pygame.draw.line(fenetre, blanc, (mouse_x, mouse_y - size), (mouse_x, mouse_y + size))
        elif CROSSHAIR_STYLES[crosshair_style_index] == "Point":
            pygame.draw.circle(fenetre, blanc, (mouse_x, mouse_y), size)

    # Après avoir dessiné le labyrinthe et avant d'afficher l'interface
    if spray_actif:
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - temps_spray < DUREE_AFFICHAGE_SPRAY:
            # Calculer la position du joueur à l'écran
            joueur_ecran_x = joueur_pos[0] * taille_case - camera_offset[0] + taille_case // 2
            joueur_ecran_y = joueur_pos[1] * taille_case - camera_offset[1] + taille_case // 2
            dessiner_cone_spray(fenetre, (joueur_ecran_x, joueur_ecran_y), angle_de_vue, 5 * taille_case)
        else:
            spray_actif = False

    pygame.display.flip()
    horloge.tick(60)  # Limiter à 60 FPS

pygame.quit()
