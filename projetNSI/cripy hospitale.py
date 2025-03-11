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
    print("Erreur lors du chargement de la musique de poursuite")
    musique_poursuite = None

# Charger les sons de pas
try:
    son_pas = pygame.mixer.Sound("C:/Users/luiar/Downloads/projetNSI/OST/course.wav")
    son_course = pygame.mixer.Sound("C:/Users/luiar/Downloads/projetNSI/OST/course.wav")
    son_pas.set_volume(100)  # Ajuster le volume
    son_course.set_volume(100)  # Ajuster le volume
except:
    print("Erreur lors du chargement des sons de pas")
    son_pas = None
    son_course = None

# Variables pour gérer les sons
son_pas_actif = False
son_course_actif = False

# Variables pour gérer l'état de la musique
est_en_poursuite = False
temps_perdu_vue = 0
DELAI_ARRET_MUSIQUE = 120  # Frames (environ 2 secondes à 60 FPS)

# Variables pour gérer les sons de pas
temps_dernier_pas = 0
DELAI_PAS_MARCHE = 500  # Délai entre les pas en millisecondes (marche)
DELAI_PAS_COURSE = 300  # Délai entre les pas en millisecondes (course)
son_en_cours = None

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
nombre_lignes = (hauteur // taille_case) * 2
nombre_colonnes = (largeur // taille_case) * 2

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
JOUEUR = (0, 0, 255)  # Add this line - blue color for player

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
cles_collectees = 3  
nombre_ennemis = 1
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
VITESSE_PATROUILLE = 0.15
VITESSE_POURSUITE = 0.25
VITESSE_RALENTIE = 0.1

# Ajouter aux paramètres de jeu
nombre_sprays = 2  # Nombre de sprays sur la map
sprays_collectes = 0  # Compteur de sprays dans l'inventaire

# Ajouter aux variables globales au début du fichier
spray_actif = False
temps_spray = 0
DUREE_AFFICHAGE_SPRAY = 500  # Durée d'affichage du spray en millisecondes

# Ajouter ces variables globales au début du fichier
VITESSE_BASE = 0.25
VITESSE_SPRINT = 0.35
derniere_position = [0, 0]

# Au début du fichier, ajoutez ces variables
musique_ambiance = None
musique_ambiance_position = 0

# Ajouter ces constantes pour le jardin après les autres constantes
DENSITE_BUISSONS = 0.03
REDUCTION_VISION_BUISSON = 1
VITESSE_NORMALE = 1

# Ajouter ces couleurs après les autres couleurs
HERBE = (34, 139, 34)
BUISSON = (0, 100, 0)
ARBRE = (255, 105, 180)
BARRIERE = (139, 69, 19)

COULEURS_JARDIN = {
    "X": BARRIERE,
    "B": BUISSON,
    "A": ARBRE,
    "S": sortie,
    "J": JOUEUR,
    " ": HERBE,
}

# Ajouter cette variable pour suivre le niveau actuel
niveau_actuel = 1

# Ajouter cette constante en haut du fichier ou près des autres constantes
VITESSE_NORMALE_JARDIN = 0.15  # Vitesse normale réduite pour le jardin

# 1. Ajouter aux constantes de couleur (après les autres couleurs)
bouteille_verre = (139, 69, 19)  # Couleur marron pour la bouteille

# 2. Ajouter aux paramètres de jeu (après les autres paramètres)
nombre_bouteilles = 2  # Nombre de bouteilles sur la map
bouteilles_collectees = 0  # Compteur pour l'inventaire

# Ajouter aux variables globales
bouteilles_lancees = []  # Liste pour stocker les bouteilles en vol
VITESSE_BOUTEILLE = 0.5  # Vitesse de la bouteille lancée
DUREE_DISTRACTION = 180  # 3 secondes à 60 FPS

# Ajouter aux variables globales
inventaire = [None] * 5  # 5 cases d'inventaire, None = case vide

class Jardin:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.nb_lignes = (hauteur // taille_case) * 2
        self.nb_colonnes = (largeur // taille_case) * 2
        self.grille = self.generer_jardin()
        self.preparer_textures()
        # Ajouter la position initiale du joueur
        self.joueur_pos = [self.nb_colonnes // 2, self.nb_lignes // 2]
        self.camera_offset = [0, 0]  # Add this line

    def generer_jardin(self):
        # Créer une grille plus grande
        grille = [[" " for _ in range(self.nb_colonnes)] for _ in range(self.nb_lignes)]

        # Placer les barrières sur les bords
        for i in range(self.nb_lignes):
            grille[i][0] = grille[i][-1] = "X"
        for j in range(self.nb_colonnes):
            grille[0][j] = grille[-1][j] = "X"

        # Augmenter le nombre de buissons proportionnellement à la taille
        nombre_buissons = int(self.nb_lignes * self.nb_colonnes * DENSITE_BUISSONS * 2)
        for _ in range(nombre_buissons):
            x, y = random.randint(1, self.nb_colonnes - 3), random.randint(1, self.nb_lignes - 3)
            if grille[y][x] == " ":
                for dy in range(2):
                    for dx in range(2):
                        if y + dy < self.nb_lignes and x + dx < self.nb_colonnes:
                            grille[y + dy][x + dx] = "B"

        # Augmenter le nombre d'arbres
        nombre_arbres = random.randint(40, 120)  # Doublé le nombre d'arbres
        for _ in range(nombre_arbres):
            x, y = random.randint(1, self.nb_colonnes - 2), random.randint(1, self.nb_lignes - 2)
            if grille[y][x] == " ":
                grille[y][x] = "A"
                # Créer des groupes d'arbres plus grands
                if random.random() < 0.7 and y + 2 < self.nb_lignes - 1 and x + 2 < self.nb_colonnes - 1:
                    for dy in range(3):
                        for dx in range(3):
                            if grille[y + dy][x + dx] == " ":
                                grille[y + dy][x + dx] = "A"

        self.placer_sortie(grille)
        return grille

    def placer_sortie(self, grille):
        bord = random.choice(["haut", "bas", "gauche", "droite"])
        if bord in ["haut", "bas"]:
            x = random.randint(1, self.nb_colonnes - 2)
            y = 0 if bord == "haut" else self.nb_lignes - 1
            grille[y][x] = "S"
            if x > 0: grille[y][x - 1] = "X"
            if x < self.nb_colonnes - 1: grille[y][x + 1] = "X"
        else:
            x = 0 if bord == "gauche" else self.nb_colonnes - 1
            y = random.randint(1, self.nb_lignes - 2)
            grille[y][x] = "S"
            if y > 0: grille[y - 1][x] = "X"
            if y < self.nb_lignes - 1: grille[y + 1][x] = "X"

    def preparer_textures(self):
        self.textures = {}
        for cle, couleur in COULEURS_JARDIN.items():
            texture = pygame.Surface((taille_case, taille_case))
            texture.fill(couleur)
            self.textures[cle] = texture

    def obtenir_grille(self):
        return self.grille

    def est_dans_buisson(self):
        # Convertir la position du joueur en coordonnées de grille
        x = int(self.joueur_pos[0])
        y = int(self.joueur_pos[1])
        
        # Vérifier si la position est valide dans la grille
        if 0 <= y < self.nb_lignes and 0 <= x < self.nb_colonnes:
            return self.grille[y][x] == "B"
        return False

    def dessiner(self, surface, angle_vue):
        # Calculer les limites visibles avec une marge
        debut_x = max(0, int(self.camera_offset[0] // taille_case) - 2)
        debut_y = max(0, int(self.camera_offset[1] // taille_case) - 2)
        fin_x = min(self.nb_colonnes, int((self.camera_offset[0] + largeur) // taille_case) + 2)
        fin_y = min(self.nb_lignes, int((self.camera_offset[1] + hauteur) // taille_case) + 2)

        # Remplir l'écran avec la couleur de l'herbe
        surface.fill(HERBE)

        # Dessiner les éléments du jardin
        for y in range(debut_y, fin_y):
            for x in range(debut_x, fin_x):
                element = self.grille[y][x]
                if element in self.textures:
                    pos_x = x * taille_case - self.camera_offset[0]
                    pos_y = y * taille_case - self.camera_offset[1]
                    surface.blit(self.textures[element], (pos_x, pos_y))

        # Dessiner le joueur avec rotation
        joueur_x = self.joueur_pos[0] * taille_case - self.camera_offset[0]
        joueur_y = self.joueur_pos[1] * taille_case - self.camera_offset[1]
        
        if joueur:  # Si l'image du joueur est chargée
            # Rotation de l'image du joueur
            rotation_angle = -(angle_vue + 90)  # +90 car l'image d'origine pointe vers le haut
            joueur_rotated = pygame.transform.rotate(joueur, rotation_angle)
            
            # Recalculer la position pour garder la rotation centrée
            joueur_rect = joueur_rotated.get_rect(center=(joueur_x + taille_case//2, joueur_y + taille_case//2))
            surface.blit(joueur_rotated, joueur_rect)
        else:
            # Fallback si l'image n'est pas chargée
            pygame.draw.rect(surface, JOUEUR, (joueur_x, joueur_y, taille_case, taille_case))

        # Ajuster la vision si le joueur est dans un buisson
        if self.est_dans_buisson():
            # Créer un masque plus sombre pour réduire la vision
            masque = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
            masque.fill((0, 0, 0, 150))  # Plus opaque pour réduire la vision
            surface.blit(masque, (0, 0))

class ennemi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.pas_patrouille = 0
        self.max_pas_patrouille = random.randint(5, 10)
        self.derniere_pos_joueur = None
        self.temps_memoire = 0
        self.duree_memoire_max = 180  # 3 secondes à 60 FPS
        self.vitesse_patrouille = VITESSE_PATROUILLE
        self.vitesse_poursuite = VITESSE_POURSUITE
        self.vitesse_actuelle = self.vitesse_patrouille
        self.ralenti = False
        self.temps_ralenti = 0
        self.distrait = False
        self.temps_distraction = 0

    def peut_voir_joueur(self, joueur_pos, hopital):
        if self.distrait:
            return False
        if self.ralenti:
            return False
            
        dx = joueur_pos[0] - self.x
        dy = joueur_pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 8:  # Distance de vision maximale
            return False
            
        # Vérifier s'il y a un mur entre l'ennemi et le joueur
        return not a_mur_entre([self.x, self.y], joueur_pos, hopital)

    def mettre_a_jour(self, hopital, joueur_pos):
        if self.distrait:
            if self.temps_distraction > 0:
                self.temps_distraction -= 1
                # Se déplacer vers le point de distraction
                if self.derniere_pos_joueur:
                    dx = self.derniere_pos_joueur[0] - self.x
                    dy = self.derniere_pos_joueur[1] - self.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance > 0.1:
                        self.x += (dx/distance) * self.vitesse_actuelle
                        self.y += (dy/distance) * self.vitesse_actuelle
            else:
                self.distrait = False
                self.derniere_pos_joueur = None

# Ensuite, placez cette fonction après la définition de la classe ennemi
def initialiser_ennemis(hopital, nombre_ennemis):
    ennemis = []
    cases_vides = [(j, i) for i, ligne in enumerate(hopital)
                   for j, case in enumerate(ligne) if case == " "]
    for _ in range(nombre_ennemis):
        if cases_vides:
            x, y = random.choice(cases_vides)
            ennemis.append(ennemi(x, y))
            cases_vides.remove((x, y))
    return ennemis

def deplacer_ennemis(hopital, ennemis, joueur_pos):
    global est_en_poursuite, temps_perdu_vue, musique_ambiance_position
    joueur_est_vu = False
    temps_actuel = pygame.time.get_ticks()
    
    for ennemi in ennemis:
        voit_joueur = ennemi.peut_voir_joueur(joueur_pos, hopital)
        
        if voit_joueur and not ennemi.ralenti:
            joueur_est_vu = True
            temps_perdu_vue = 0
            ennemi.vitesse_actuelle = ennemi.vitesse_poursuite
            ennemi.derniere_pos_joueur = joueur_pos[:]
            ennemi.temps_memoire = ennemi.duree_memoire_max
            
            # Démarrer la musique de poursuite si pas déjà active
            if not est_en_poursuite:
                est_en_poursuite = True
                if musique_poursuite:
                    musique_ambiance_position = pygame.mixer.music.get_pos()
                    pygame.mixer.music.pause()
                    musique_poursuite.play(-1)
        
        elif not ennemi.ralenti:
            ennemi.vitesse_actuelle = ennemi.vitesse_patrouille
            
            # Comportement de patrouille quand le joueur n'est pas vu
            if not ennemi.derniere_pos_joueur:
                ennemi.pas_patrouille += 1
                if ennemi.pas_patrouille >= ennemi.max_pas_patrouille:
                    ennemi.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                    ennemi.pas_patrouille = 0
                    ennemi.max_pas_patrouille = random.randint(5, 10)
                
                nouvelle_x = ennemi.x + ennemi.direction[0] * ennemi.vitesse_patrouille
                nouvelle_y = ennemi.y + ennemi.direction[1] * ennemi.vitesse_patrouille
                
                if deplacement_valide(hopital, [nouvelle_x, ennemi.y]):
                    ennemi.x = nouvelle_x
                if deplacement_valide(hopital, [ennemi.x, nouvelle_y]):
                    ennemi.y = nouvelle_y
        
        # Poursuite basée sur la dernière position connue
        if ennemi.derniere_pos_joueur:
            dx = ennemi.derniere_pos_joueur[0] - ennemi.x
            dy = ennemi.derniere_pos_joueur[1] - ennemi.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0.1:
                dx = dx / distance * ennemi.vitesse_actuelle
                dy = dy / distance * ennemi.vitesse_actuelle
                
                nouvelle_pos_x = ennemi.x + dx
                if deplacement_valide(hopital, [nouvelle_pos_x, ennemi.y]):
                    ennemi.x = nouvelle_pos_x
                
                nouvelle_pos_y = ennemi.y + dy
                if deplacement_valide(hopital, [ennemi.x, nouvelle_pos_y]):
                    ennemi.y = nouvelle_pos_y
            else:
                ennemi.derniere_pos_joueur = None
                ennemi.temps_memoire = 0
        
        # Gestion de la mémoire et du ralentissement
        if ennemi.temps_memoire > 0:
            ennemi.temps_memoire -= 1
            if ennemi.temps_memoire <= 0:
                ennemi.derniere_pos_joueur = None
        
        if ennemi.ralenti:
            if pygame.time.get_ticks() - ennemi.temps_ralenti > 2000:  # 2 secondes
                ennemi.ralenti = False
                ennemi.vitesse_actuelle = ennemi.vitesse_patrouille

    # Gestion de la musique de poursuite
    if not joueur_est_vu and est_en_poursuite:
        temps_perdu_vue += 1
        if temps_perdu_vue >= DELAI_ARRET_MUSIQUE:
            est_en_poursuite = False
            if musique_poursuite:
                musique_poursuite.stop()
                pygame.mixer.music.unpause()

    # Vérification des collisions avec le joueur
    if verifier_collision_ennemis(joueur_pos, ennemis):
        return "game_over"
    
    return None


def verifier_collision_ennemis(joueur_pos, ennemis):
    pos_x_int = int(joueur_pos[0])
    pos_y_int = int(joueur_pos[1])
    
    for ennemi in ennemis:
        ennemi_x = int(ennemi.x)
        ennemi_y = int(ennemi.y)
        
        # Vérifier si l'ennemi touche le joueur
        if (abs(pos_x_int - ennemi_x) < 1 and 
            abs(pos_y_int - ennemi_y) < 1):
            return True
    return False


def game_over():
    global running, cles_collectees, sprays_collectes, bouteilles_collectees, endurance_actuelle
    
    # Arrêter toutes les musiques
    arreter_musiques()
    
    # Afficher l'écran de game over
    fenetre.fill(noir)
    font = pygame.font.Font(None, 74)
    texte = font.render("Game Over", True, (255, 0, 0))
    texte_rect = texte.get_rect(center=(largeur//2, hauteur//2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    
    # Attendre quelques secondes
    pygame.time.wait(2000)
    
    # Réinitialiser l'inventaire
    cles_collectees = 0
    sprays_collectes = 0
    bouteilles_collectees = 0
    endurance_actuelle = endurance_max
    
    # Réinitialiser le jeu
    hopital = generer_hopital(nombre_lignes, nombre_colonnes)
    cles = placer_cles(hopital, nombre_cles)
    placer_sprays(hopital, nombre_sprays)
    placer_bouteilles(hopital, nombre_bouteilles)  # Ajouter cette ligne
    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
    ennemis = initialiser_ennemis(hopital, nombre_ennemis)
    
    # Retourner au menu principal
    pygame.mouse.set_visible(True)
    afficher_menu()
    pygame.mouse.set_visible(False)
    musique_fond()
    
    return "menu"


def appliquer_masque_vision(surface, position, angle, length):
    masque = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    masque.fill((0, 0, 0, 200))  # Masque noir semi-transparent

    x, y = position
    start_angle = math.radians(angle - cone_angle / 2)
    end_angle = math.radians(angle + cone_angle / 2)

    # Points pour le polygone de vision
    points = [(x, y)]  # Point de départ (position du joueur)

    # Réduire le nombre de rayons et augmenter le pas
    steps = 30  # Réduit de 180 à 30 rayons
    ray_step = 5  # Augmente le pas de 2 à 5

    # Pré-calculer les valeurs trigonométriques pour éviter les calculs répétés
    angle_step = (end_angle - start_angle) / steps
    cos_angles = [math.cos(start_angle + i * angle_step) for i in range(steps + 1)]
    sin_angles = [math.sin(start_angle + i * angle_step) for i in range(steps + 1)]

    # Pour chaque rayon du cône
    for i in range(steps + 1):
        # Utiliser les valeurs pré-calculées
        cos_theta = cos_angles[i]
        sin_theta = sin_angles[i]
        
        # Lancer un rayon avec un pas plus grand
        for dist in range(0, int(length), ray_step):
            ray_x = x + dist * cos_theta
            ray_y = y + dist * sin_theta

            # Convertir en coordonnées de grille une seule fois
            grille_x = int((ray_x + camera_offset[0]) / taille_case)
            grille_y = int((ray_y + camera_offset[1]) / taille_case)

            # Vérifier les limites de la grille et collision avec mur
            if (0 <= grille_y < len(hopital) and 
                0 <= grille_x < len(hopital[0]) and 
                hopital[grille_y][grille_x] == "#"):
                points.append((ray_x, ray_y))
                break
            elif dist >= length - ray_step:
                points.append((ray_x, ray_y))

    # Dessiner le polygone de vision du cône si on a assez de points
    if len(points) > 2:
        pygame.draw.polygon(masque, (0, 0, 0, 0), points)

    # Ajouter le cercle de vision proche
    pygame.draw.circle(masque, (0, 0, 0, 0), (int(x), int(y)), rayon_vision_proche)

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


def est_dans_cone(pos_joueur, pos_cible, angle_vue, longueur_cone):
    dx = pos_cible[0] - pos_joueur[0]
    dy = pos_cible[1] - pos_joueur[1]
    
    # Calculer la distance
    distance = math.sqrt(dx*dx + dy*dy)
    if distance > longueur_cone:
        return False
        
    # Calculer l'angle vers la cible
    angle_cible = (math.degrees(math.atan2(dy, dx)) + 360) % 360
    
    # Calculer la différence d'angle
    diff_angle = (angle_cible - angle_vue + 180) % 360 - 180
    
    # Vérifier si la cible est dans le cône
    return abs(diff_angle) <= 30  # 30 degrés de chaque côté


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
    """Version optimisée et sécurisée de la vérification des murs"""
    x1, y1 = joueur_pos
    x2, y2 = case_pos

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    x = int(x1)
    y = int(y1)

    # Vérifier que les positions de départ et d'arrivée sont dans les limites
    hauteur = len(hopital)
    largeur = len(hopital[0]) if hauteur > 0 else 0
    
    if not (0 <= x < largeur and 0 <= y < hauteur):
        return True
    
    if not (0 <= int(x2) < largeur and 0 <= int(y2) < hauteur):
        return True

    if dx > dy:
        err = dx / 2.0
        step_y = 1 if y2 > y1 else -1
        step_x = 1 if x2 > x1 else -1
        
        while x != int(x2):
            err -= dy
            if err < 0:
                y += step_y
                err += dx
            x += step_x
            
            # Vérifier les limites avant d'accéder à hopital
            if not (0 <= x < largeur and 0 <= y < hauteur):
                return True
            if hopital[y][x] == "#":
                return True
    else:
        err = dy / 2.0
        step_x = 1 if x2 > x1 else -1
        step_y = 1 if y2 > y1 else -1
        
        while y != int(y2):
            err -= dx
            if err < 0:
                x += step_x
                err += dy
            y += step_y
            
            # Vérifier les limites avant d'accéder à hopital
            if not (0 <= x < largeur and 0 <= y < hauteur):
                return True
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
            x = j * taille_case - cam_x
            case = hopital[i][j]
            if case in ["S", "C", "P", "V"]:  # Ajout de "V" pour les bouteilles
                if est_visible(joueur_pos, (j, i), hopital):
                    if case == "S":
                        couleur = sortie
                    elif case == "C":
                        couleur = cle
                    elif case == "P":
                        couleur = spray
                    elif case == "V":
                        couleur = bouteille_verre
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
    # Vérifier les quatre coins de la hitbox du joueur
    positions_a_verifier = [
        (int(pos[0]), int(pos[1])),  # Coin supérieur gauche
        (int(pos[0] + 0.9), int(pos[1])),  # Coin supérieur droit
        (int(pos[0]), int(pos[1] + 0.9)),  # Coin inférieur gauche
        (int(pos[0] + 0.9), int(pos[1] + 0.9))  # Coin inférieur droit
    ]
    
    for x, y in positions_a_verifier:
        if not (0 <= y < len(hopital) and 0 <= x < len(hopital[0])):
            return False
        if hopital[y][x] == "#":
            return False
    return True

# Fonction de victoire


def afficher_victoire():
    fenetre.fill(noir)
    font = pygame.font.Font(None, 74)
    
    texte = font.render("Félicitations ! Jeu terminé !", True, blanc)
    text_rect = texte.get_rect(center=(largeur//2, hauteur//2))
    fenetre.blit(texte, text_rect)
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
    global cles_collectees, sprays_collectes, bouteilles_collectees, endurance_actuelle
    
    # Réinitialiser l'inventaire
    cles_collectees = 0
    sprays_collectes = 0
    bouteilles_collectees = 0
    endurance_actuelle = endurance_max
    
    pygame.mouse.set_visible(True)
    musique_menu()

    # Charger les différentes couches du fond
    background_layers = [
        pygame.image.load("C:/Users/luiar/Downloads/projetNSI/texture/background_1.png"),
        pygame.image.load("C:/Users/luiar/Downloads/projetNSI/texture/background_2.png"),
        pygame.image.load("C:/Users/luiar/Downloads/projetNSI/texture/background_3.png"),
        pygame.image.load("C:/Users/luiar/Downloads/projetNSI/texture/background_4.png"),
        pygame.image.load("C:/Users/luiar/Downloads/projetNSI/texture/background_5.png")
    ]
    
    # Augmenter encore le facteur d'échelle pour plus de marge de mouvement
    scale_factor = 1.3  # Augmenté à 1.3 pour plus d'amplitude
    scaled_width = int(largeur * scale_factor)
    scaled_height = int(hauteur * scale_factor)
    background_layers = [pygame.transform.scale(layer, (scaled_width, scaled_height)) 
                        for layer in background_layers]
    
    # Augmenter les facteurs de parallaxe pour plus de mouvement
    parallax_factors = [0.02, 0.04, 0.08, 0.12, 0.16]  # Facteurs plus importants
    initial_offset_x = -150  # Décalage initial plus important

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculer le décalage relatif avec plus d'amplitude
        center_x = largeur / 2
        center_y = hauteur / 2
        rel_x = (mouse_x - center_x) / (center_x * 0.7)  # Réduit le diviseur pour plus d'amplitude
        rel_y = (mouse_y - center_y) / (center_y * 0.7)

        for i, layer in enumerate(background_layers):
            # Calculer les décalages avec plus d'amplitude
            offset_x = initial_offset_x - rel_x * parallax_factors[i] * (scaled_width - largeur)
            offset_y = -rel_y * parallax_factors[i] * (scaled_height - hauteur)
            
            fenetre.blit(layer, (offset_x, offset_y))

        # Reste du code inchangé...
        titre = pygame.font.Font(
            "C:/Users/luiar/Downloads/projetNSI/November.ttf", 150).render("Echoes of the Hollow", True, blanc)
        titre_rect = titre.get_rect(center=(largeur//2, hauteur//6))
        fenetre.blit(titre, titre_rect)

        button_gap = 120
        start_y = hauteur // 3
        boutons = [
            (pygame.Rect(largeur // 2 - 250, start_y, 500, 90), "Nouvelle Partie", 40),
            (pygame.Rect(largeur // 2 - 250, start_y + button_gap, 500, 90), "Paramètres", 40),
            (pygame.Rect(largeur // 2 - 250, start_y + button_gap * 2, 500, 90), "Crédits", 40),
            (pygame.Rect(largeur // 2 - 250, start_y + button_gap * 3, 500, 90), "Quitter", 40),
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
                for bouton, texte, _ in boutons:
                    if bouton.collidepoint(event.pos):
                        if texte == "Nouvelle Partie":
                            pygame.mouse.set_visible(False)
                            return
                        elif texte == "Paramètres":
                            afficher_parametres()
                        elif texte == "Crédits":
                            afficher_credits()
                        elif texte == "Quitter":
                            pygame.quit()
                            sys.exit()

# Afficher le menu pause
def afficher_menu_pause():
    global cles_collectees, sprays_collectes, bouteilles_collectees, endurance_actuelle
    
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

def trouver_case_disponible():
    """Trouve la première case vide dans l'inventaire"""
    for i in range(len(inventaire)):
        if inventaire[i] is None:
            return i
    return -1

def ajouter_objet(type_objet):
    """Ajoute un objet dans la première case disponible"""
    case = trouver_case_disponible()
    if case != -1:
        inventaire[case] = type_objet
        return True
    return False

def utiliser_objet_selectionne():
    """Utilise l'objet dans la case sélectionnée"""
    global sprays_collectes, bouteilles_collectees
    
    if index_case_selectionnee < len(inventaire):
        objet = inventaire[index_case_selectionnee]
        if objet == "spray" and sprays_collectes > 0:
            utiliser_spray(joueur_pos, angle_de_vue, ennemis, hopital)
            sprays_collectes -= 1
            if sprays_collectes == 0:
                inventaire[index_case_selectionnee] = None
        elif objet == "bouteille" and bouteilles_collectees > 0:
            utiliser_bouteille(joueur_pos, angle_de_vue)
            bouteilles_collectees -= 1
            if bouteilles_collectees == 0:
                inventaire[index_case_selectionnee] = None

def dessiner_inventaire(surface):
    # Position et taille de l'inventaire
    inv_x = 20
    inv_y = hauteur - 70
    case_taille = 50
    espacement = 10
    
    # Dessiner les cases d'inventaire
    for i in range(len(inventaire)):
        x = inv_x + (case_taille + espacement) * i
        pygame.draw.rect(surface, gris_fonce, (x, inv_y, case_taille, case_taille))
        if i == index_case_selectionnee:
            pygame.draw.rect(surface, gris_clair, (x, inv_y, case_taille, case_taille), 2)
        else:
            pygame.draw.rect(surface, gris, (x, inv_y, case_taille, case_taille), 1)
        
        # Afficher l'objet dans la case
        if inventaire[i] == "spray":
            pygame.draw.rect(surface, spray, (x + 5, inv_y + 5, case_taille - 10, case_taille - 10))
            texte = pygame.font.Font(None, 20).render(str(sprays_collectes), True, blanc)
            surface.blit(texte, (x + case_taille - 15, inv_y + case_taille - 15))
        elif inventaire[i] == "bouteille":
            pygame.draw.rect(surface, bouteille_verre, (x + 5, inv_y + 5, case_taille - 10, case_taille - 10))
            texte = pygame.font.Font(None, 20).render(str(bouteilles_collectees), True, blanc)
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
    pygame.mixer.music.load("C:/Users/luiar/Downloads/projetNSI/OST/menu_musique.mp3")  # Ensure the path is correct
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


def musique_fond():
    pygame.mixer.music.load("C:/Users/luiar/Downloads/projetNSI/OST/Amnesia_02.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)


def arreter_musiques():
    global est_en_poursuite, temps_perdu_vue, son_pas_actif, son_course_actif
    if musique_poursuite:
        musique_poursuite.stop()
    if son_pas:
        son_pas.stop()
        son_pas_actif = False
    if son_course:
        son_course.stop()
        son_course_actif = False
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

# 3. Ajouter la fonction pour placer les bouteilles (avant l'initialisation du jeu)
def placer_bouteilles(hopital, nombre):
    cases_vides = []
    for y in range(len(hopital)):
        for x in range(len(hopital[0])):
            if hopital[y][x] == " ":
                cases_vides.append((y, x))
    
    for _ in range(nombre):
        if cases_vides:
            y, x = random.choice(cases_vides)
            hopital[y][x] = "V"  # V pour bouteille en Verre
            cases_vides.remove((y, x))

# Ensuite, la génération des objets
hopital = generer_hopital(nombre_lignes, nombre_colonnes)
cles = placer_cles(hopital, nombre_cles)
placer_sprays(hopital, nombre_sprays)
placer_bouteilles(hopital, nombre_bouteilles)  # Cette ligne fonctionnera maintenant
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

# Modifiez la fonction qui démarre la musique d'ambiance
def demarrer_musique_ambiance():
    try:
        pygame.mixer.music.load("C:/Users/luiar/Downloads/projetNSI/OST/Amnesia_02.mp3")
        pygame.mixer.music.play(-1)
    except:
        print("Erreur lors du chargement de la musique d'ambiance")

# Ajoutez cette fonction au début du jeu
demarrer_musique_ambiance()

# Ajouter une classe pour les bouteilles lancées
class BouteilleLancee:
    def __init__(self, x, y, angle):
        self.x = float(x)  # Position en flottant pour un mouvement plus fluide
        self.y = float(y)
        self.angle = angle
        angle_rad = math.radians(angle)
        # Garder la même vitesse rapide
        self.dx = math.cos(angle_rad) * 0.8
        self.dy = -math.sin(angle_rad) * 0.8  # Le signe négatif est important ici
        self.brisee = False
        self.temps_brisure = 0
        self.position_brisure = None

def utiliser_bouteille(pos_joueur, angle):
    global bouteilles_collectees, bouteilles_lancees
    if bouteilles_collectees > 0:
        # Obtenir la position exacte du curseur
        pos_souris = pygame.mouse.get_pos()
        
        # Convertir la position du joueur en coordonnées écran
        joueur_ecran_x = pos_joueur[0] * taille_case - camera_offset[0]
        joueur_ecran_y = pos_joueur[1] * taille_case - camera_offset[1]
        
        # Calculer l'angle vers le curseur
        dx = pos_souris[0] - joueur_ecran_x
        dy = pos_souris[1] - joueur_ecran_y
        angle_reel = math.degrees(math.atan2(-dy, dx))  # -dy car l'axe Y est inversé
        
        bouteilles_collectees -= 1
        nouvelle_bouteille = BouteilleLancee(pos_joueur[0], pos_joueur[1], angle_reel)
        bouteilles_lancees.append(nouvelle_bouteille)

def mettre_a_jour_bouteilles(hopital, ennemis):
    global bouteilles_lancees
    nouvelles_bouteilles = []
    
    for bouteille in bouteilles_lancees:
        if not bouteille.brisee:
            pas = 0.2
            distance_parcourue = 0
            distance_max = 1.0
            
            while distance_parcourue < distance_max and not bouteille.brisee:
                nouvelle_x = bouteille.x + bouteille.dx * pas
                nouvelle_y = bouteille.y + bouteille.dy * pas
                
                pos_grille_x = int(nouvelle_x)
                pos_grille_y = int(nouvelle_y)
                
                if (0 <= pos_grille_y < len(hopital) and 
                    0 <= pos_grille_x < len(hopital[0])):
                    if hopital[pos_grille_y][pos_grille_x] == "#":
                        bouteille.brisee = True
                        bouteille.position_brisure = [bouteille.x, bouteille.y]
                        bouteille.temps_brisure = DUREE_DISTRACTION
                        
                        for ennemi in ennemis:
                            distance = distance_entre_points([ennemi.x, ennemi.y], bouteille.position_brisure)
                            if distance < 8:
                                ennemi.distrait = True
                                ennemi.derniere_pos_joueur = bouteille.position_brisure
                                ennemi.temps_distraction = DUREE_DISTRACTION
                        break
                    else:
                        bouteille.x = nouvelle_x
                        bouteille.y = nouvelle_y
                else:
                    bouteille.brisee = True
                    break
                
                distance_parcourue += pas
                
        if bouteille.brisee:
            if bouteille.temps_brisure > 0:
                bouteille.temps_brisure -= 1
                nouvelles_bouteilles.append(bouteille)
        else:
            nouvelles_bouteilles.append(bouteille)
    
    bouteilles_lancees = nouvelles_bouteilles

def dessiner_bouteilles(surface, camera_offset):
    for bouteille in bouteilles_lancees:
        # Convertir les coordonnées du monde en coordonnées d'écran
        pos_x = int(bouteille.x * taille_case - camera_offset[0])
        pos_y = int(bouteille.y * taille_case - camera_offset[1])
        
        if not bouteille.brisee:
            # Dessiner la bouteille en vol
            taille_bouteille = taille_case // 2
            
            # Créer une surface pour la bouteille avec transparence
            surface_bouteille = pygame.Surface((taille_bouteille, taille_bouteille), pygame.SRCALPHA)
            
            # Dessiner la bouteille comme un rectangle allongé
            pygame.draw.rect(surface_bouteille, bouteille_verre, 
                           (taille_bouteille//4, 0, 
                            taille_bouteille//2, taille_bouteille))
            
            # Rotation de la bouteille selon sa direction
            angle_rotation = -math.degrees(math.atan2(bouteille.dy, bouteille.dx))
            surface_bouteille_rotated = pygame.transform.rotate(surface_bouteille, angle_rotation)
            rect_rotated = surface_bouteille_rotated.get_rect(center=(pos_x, pos_y))
            
            surface.blit(surface_bouteille_rotated, rect_rotated)
            
            # Dessiner une petite traînée derrière la bouteille
            for i in range(3):
                alpha = 150 - i * 50  # Diminuer l'opacité progressivement
                pos_trainee_x = int(pos_x - bouteille.dx * taille_case * i)
                pos_trainee_y = int(pos_y - bouteille.dy * taille_case * i)
                surface_trainee = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(surface_trainee, (*bouteille_verre[:3], alpha), (2, 2), 2)
                surface.blit(surface_trainee, (pos_trainee_x - 2, pos_trainee_y - 2))
        else:
            # Dessiner les éclats de verre quand la bouteille est brisée
            for i in range(8):  # Augmenter le nombre d'éclats
                angle = random.uniform(0, 360)
                distance = random.uniform(0, taille_case/2)
                eclat_x = pos_x + math.cos(math.radians(angle)) * distance
                eclat_y = pos_y + math.sin(math.radians(angle)) * distance
                taille_eclat = random.randint(1, 3)
                pygame.draw.circle(surface, (200, 200, 200, 150), 
                                 (int(eclat_x), int(eclat_y)), taille_eclat)

def distance_entre_points(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

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
                    # Réinitialiser le jeu et l'inventaire
                    hopital = generer_hopital(nombre_lignes, nombre_colonnes)
                    cles = placer_cles(hopital, nombre_cles)
                    placer_sprays(hopital, nombre_sprays)
                    placer_bouteilles(hopital, nombre_bouteilles)  # Ajouter cette ligne
                    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
                    ennemis = initialiser_ennemis(hopital, nombre_ennemis)
                    cles_collectees = 0
                    sprays_collectes = 0
                    bouteilles_collectees = 0
                    endurance_actuelle = endurance_max
                    arreter_musiques()
                    musique_fond()
                elif choix == "menu":
                    # Réinitialiser le jeu et l'inventaire
                    hopital = generer_hopital(nombre_lignes, nombre_colonnes)
                    cles = placer_cles(hopital, nombre_cles)
                    placer_sprays(hopital, nombre_sprays)
                    placer_bouteilles(hopital, nombre_bouteilles)  # Ajouter cette ligne
                    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
                    ennemis = initialiser_ennemis(hopital, nombre_ennemis)
                    cles_collectees = 0
                    sprays_collectes = 0
                    bouteilles_collectees = 0
                    endurance_actuelle = endurance_max
                    afficher_menu()
                    arreter_musiques()
                    musique_fond()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Mouse wheel up
                index_case_selectionnee = max(0, index_case_selectionnee - 1)
            elif event.button == 5:  # Mouse wheel down
                index_case_selectionnee = min(4, index_case_selectionnee + 1)
            elif event.button == 1:  # Clic gauche
                utiliser_objet_selectionne()
        if event.type == pygame.VIDEORESIZE and not is_fullscreen:
            largeur, hauteur = event.size
            fenetre = pygame.display.set_mode((largeur, hauteur), pygame.RESIZABLE)
            hopital = redimensionner_jeu(largeur, hauteur)
            # Réinitialiser la position du joueur et des ennemis
            joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
            ennemis = initialiser_ennemis(hopital, nombre_ennemis)

    # Calculer l'angle de vue en fonction de la position de la souris
    souris_x, souris_y = pygame.mouse.get_pos()
    
    # Calculer la position du joueur à l'écran
    joueur_ecran_x = joueur_pos[0] * taille_case - camera_offset[0]
    joueur_ecran_y = joueur_pos[1] * taille_case - camera_offset[1]
    
    # Calculer l'angle entre le joueur et la souris
    dx = souris_x - joueur_ecran_x
    dy = souris_y - joueur_ecran_y
    angle_de_vue = (math.degrees(math.atan2(dy, dx)) + 360) % 360

    # Mise à jour de la vision des ennemis
    for ennemi in ennemis:
        if ennemi.peut_voir_joueur(joueur_pos, hopital):
            if not est_dans_cone(joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, cone_longueur):
                ennemi.derniere_pos_joueur = joueur_pos[:]
                ennemi.temps_memoire = ennemi.duree_memoire_max

    # Gestion du mouvement
    touches = pygame.key.get_pressed()
    nouvelle_pos_x = joueur_pos[0]
    nouvelle_pos_y = joueur_pos[1]
    
    # Gestion du sprint
    est_en_sprint = (touches[pygame.K_LSHIFT] or touches[pygame.K_RSHIFT]) and endurance_actuelle > 0
    
    # Déterminer la vitesse en fonction du sprint
    if est_en_sprint and (touches[pygame.K_z] or touches[pygame.K_s] or touches[pygame.K_q] or touches[pygame.K_d] or 
                         touches[pygame.K_UP] or touches[pygame.K_DOWN] or touches[pygame.K_LEFT] or touches[pygame.K_RIGHT]):
        vitesse = VITESSE_SPRINT
        endurance_actuelle = max(0, endurance_actuelle - taux_diminution)
    else:
        vitesse = VITESSE_BASE
        # Récupération d'endurance seulement si on ne court pas
        if endurance_actuelle < endurance_max:
            endurance_actuelle = min(endurance_max, endurance_actuelle + taux_recuperation)
    
    # Calculer le déplacement
    dx = 0
    dy = 0
    
    if touches[pygame.K_z] or touches[pygame.K_UP]:
        dy -= vitesse
    if touches[pygame.K_s] or touches[pygame.K_DOWN]:
        dy += vitesse
    if touches[pygame.K_q] or touches[pygame.K_LEFT]:
        dx -= vitesse
    if touches[pygame.K_d] or touches[pygame.K_RIGHT]:
        dx += vitesse
        
    # Normaliser le mouvement diagonal
    if dx != 0 and dy != 0:
        dx *= 0.707
        dy *= 0.707
    
    # Tester d'abord le mouvement horizontal
    if deplacement_valide(hopital, [nouvelle_pos_x + dx, nouvelle_pos_y]):
        nouvelle_pos_x += dx
    
    # Puis le mouvement vertical
    if deplacement_valide(hopital, [nouvelle_pos_x, nouvelle_pos_y + dy]):
        nouvelle_pos_y += dy
    
    # Mettre à jour la position du joueur
    joueur_pos[0] = nouvelle_pos_x
    joueur_pos[1] = nouvelle_pos_y
    
    # Convertir les positions en entiers pour les vérifications
    pos_x_int = int(joueur_pos[0])
    pos_y_int = int(joueur_pos[1])
    
    # Vérifier les cases autour du joueur pour la collecte (rayon de 1 case)
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            check_x = pos_x_int + dx
            check_y = pos_y_int + dy
            
            # Vérifier que la position est valide
            if 0 <= check_y < len(hopital) and 0 <= check_x < len(hopital[0]):
                case = hopital[check_y][check_x]
                # Collecte des objets
                if case == "C":
                    cles_collectees += 1
                    hopital[check_y][check_x] = " "
                elif case == "P":
                    if ajouter_objet("spray"):
                        sprays_collectes += 1
                        hopital[check_y][check_x] = " "
                elif case == "V":
                    if ajouter_objet("bouteille"):
                        bouteilles_collectees += 1
                        hopital[check_y][check_x] = " "

    # Mise à jour fluide de la caméra
    camera_cible_x = joueur_pos[0] * taille_case - largeur // 2
    camera_cible_y = joueur_pos[1] * taille_case - hauteur // 2
    
    # Interpolation douce de la caméra
    facteur_lissage = 0.1
    camera_offset[0] += (camera_cible_x - camera_offset[0]) * facteur_lissage
    camera_offset[1] += (camera_cible_y - camera_offset[1]) * facteur_lissage

    # S'assurer que la position finale respecte toujours les limites
    camera_offset[0] = max(0, min(camera_offset[0], len(hopital[0]) * taille_case - largeur))
    camera_offset[1] = max(0, min(camera_offset[1], len(hopital) * taille_case - hauteur))

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

    # Déplacer les ennemis
    resultat = deplacer_ennemis(hopital, ennemis, joueur_pos)
    if resultat == "game_over":
        etat_jeu = game_over()
        if etat_jeu == "menu":
            # Réinitialiser le jeu
            hopital = generer_hopital(nombre_lignes, nombre_colonnes)
            joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
            cles_collectees = 0
            ennemis = initialiser_ennemis(hopital, nombre_ennemis)
            continue

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

    # Mettre à jour et dessiner les bouteilles
    mettre_a_jour_bouteilles(hopital, ennemis)
    dessiner_bouteilles(fenetre, camera_offset)

    pygame.display.flip()
    horloge.tick(60)  # Limiter à 60 FPS

def dessiner_barre_endurance(surface):
    # Position et taille de la barre
    x = 20
    y = hauteur - 40
    largeur_max = 200
    hauteur_barre = 20
    
    # Dessiner le fond de la barre
    pygame.draw.rect(surface, (50, 50, 50), (x, y, largeur_max, hauteur_barre))
    
    # Dessiner l'endurance actuelle
    largeur_endurance = (endurance_actuelle / endurance_max) * largeur_max
    pygame.draw.rect(surface, (0, 255, 0), (x, y, largeur_endurance, hauteur_barre))
    
    # Dessiner le contour
    pygame.draw.rect(surface, blanc, (x, y, largeur_max, hauteur_barre), 2)

def mettre_a_jour_camera(joueur_pos):
    global camera_offset
    
    # Calculer la position souhaitée de la caméra (centrée sur le joueur)
    camera_x = joueur_pos[0] * taille_case - largeur // 2
    camera_y = joueur_pos[1] * taille_case - hauteur // 2
    
    # Calculer les limites de la carte en pixels
    limite_droite = len(hopital[0]) * taille_case - largeur
    limite_bas = len(hopital) * taille_case - hauteur
    
    # Limiter la position de la caméra pour ne pas voir hors de la carte
    camera_x = max(0, min(camera_x, limite_droite))
    camera_y = max(0, min(camera_y, limite_bas))
    
    # Interpolation douce vers la nouvelle position
    vitesse_camera = 0.1  # Ajustez cette valeur pour une transition plus ou moins rapide
    camera_offset[0] += (camera_x - camera_offset[0]) * vitesse_camera
    camera_offset[1] += (camera_y - camera_offset[1]) * vitesse_camera
    
    # S'assurer que la position finale respecte toujours les limites
    camera_offset[0] = max(0, min(camera_offset[0], limite_droite))
    camera_offset[1] = max(0, min(camera_offset[1], limite_bas))

pygame.quit()