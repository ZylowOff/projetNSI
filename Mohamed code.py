import pygame
import random
import sys
import math
import os
import json
import ctypes

myappid = 'echoesofthehollow.tropheensi.2025'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

pygame.init()
pygame.mixer.init()

largeur = 1920
hauteur = 1080
taille_case = 50

noir = '#000000'
blanc = '#ffffff'
gris = '#969696'
gris2 = '#584a5a'
sortie = '#00ff00'
mur = '#64281e'
sol = '#736d73'
cle = '#ffdf00'
ennemi_couleur = '#ff0000'
bordeaux = '#280000'
dark_purple = '#180c1a'
light_purple = '#4b0082'
hover_purple = '#6428a0'

fichier_parametres = "./settings.json"
joueur_img = pygame.image.load("./assets/characters/personnage.png")
joueur = pygame.transform.scale(joueur_img, (taille_case * 1.25, taille_case * 1.25))
button_img = pygame.image.load("./assets/bouton.png")
button = pygame.transform.scale(button_img, (525, 100))
button_hover_img = pygame.image.load("./assets/bouton2.png")
button_hover_img = pygame.transform.scale(button_hover_img, (525, 140))
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
icone = pygame.image.load("./assets/icone.png")
logo_img = pygame.image.load("./assets/logo.png")
logo_width, logo_height = logo_img.get_size()
desired_width = largeur // 3
aspect_ratio = logo_height / logo_width
scaled_logo = pygame.transform.scale(logo_img, (desired_width, int(desired_width * aspect_ratio)))
nom = "Echoes of the Hollow"

pygame.display.set_caption(nom)
pygame.display.set_icon(icone)
plein_ecran = True
fenetre = pygame.display.set_mode(
    (largeur, hauteur), pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE
)

horloge = pygame.time.Clock()

nombre_cles = 3
cles_collectees = 0
nombre_ennemis = 3
vitesse_ennemis = 0.4
delai_mouvement = 35
dernier_mouvement = 0

cone_angle = 60
cone_longueur = 600
rayon_vision_proche = 100

nombre_lignes = (hauteur // taille_case) * 8
nombre_colonnes = (largeur // taille_case) * 8

joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
camera_offset = [0, 0]
angle_de_vue = 270

ennemis = []

index_case_selectionnee = 0

# endurance_max = 100
# endurance_actuelle = endurance_max
# taux_diminution = 0.5
# taux_recuperation = 0.2
# delai_mouvement_normal = 100
# delai_mouvement_rapide = 40

montrer_fps = False
volume = 0.5
resolutions = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1920, 1080),
    (2560, 1440),
    (largeur, hauteur)
]
resolution_index = 0 
controles = {
    "Haut": pygame.K_z,
    "Bas": pygame.K_s,
    "Gauche": pygame.K_q,
    "Droite": pygame.K_d
}

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
        dx = joueur_pos[0] - self.x
        dy = joueur_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > self.cone_vision:
            return False

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
            ennemi.derniere_pos_joueur = joueur_pos[:]
            ennemi.temps_memoire = ennemi.duree_memoire_max
            ennemi.vitesse_actuelle = ennemi.vitesse_normale
        elif ennemi.temps_memoire > 0:
            ennemi.temps_memoire -= 1
            ennemi.vitesse_actuelle = ennemi.vitesse_normale * 0.7
        else:
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

            if not voit_joueur and ennemi.derniere_pos_joueur:
                if (
                    abs(ennemi.x - ennemi.derniere_pos_joueur[0]) <= 1
                    and abs(ennemi.y - ennemi.derniere_pos_joueur[1]) <= 1
                ):
                    ennemi.temps_memoire = 0
                    ennemi.derniere_pos_joueur = None
            else:
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
    pygame.time.delay(2000)
    return "menu"


def appliquer_masque_vision(surface, position, angle, length):
    masque = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    masque.fill((0, 0, 0, 200))

    x, y = position
    start_angle = math.radians(angle - cone_angle / 2)
    end_angle = math.radians(angle + cone_angle / 2)

    points = [(x, y)]

    steps = 180
    for i in range(steps + 1):
        theta = start_angle + i * (end_angle - start_angle) / steps

        for dist in range(0, int(length), 2):
            ray_x = x + dist * math.cos(theta)
            ray_y = y + dist * math.sin(theta)

            grille_x = int((ray_x + camera_offset[0]) / taille_case)
            grille_y = int((ray_y + camera_offset[1]) / taille_case)

            if (
                0 <= grille_y < len(jeu)
                and 0 <= grille_x < len(jeu[0])
                and jeu[grille_y][grille_x] == "#"
            ):
                points.append((ray_x, ray_y))
                break
            elif dist >= length - 2:
                points.append((ray_x, ray_y))

    if len(points) > 2:
        pygame.draw.polygon(masque, (0, 0, 0, 0), points)

    pygame.draw.circle(masque, (0, 0, 0, 0), (int(x), int(y)), rayon_vision_proche)

    surface.blit(masque, (0, 0))


def generer_jeu(nb_lignes, nb_colonnes):
    nb_lignes = (nb_lignes // 3) * 3 + 1
    nb_colonnes = (nb_colonnes // 3) * 3 + 1
    jeu = [["#" for _ in range(nb_colonnes)] for _ in range(nb_lignes)]

    def voisins(x, y):
        directions = [(6, 0), (-6, 0), (0, 6), (0, -6)]
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

    départ(nb_colonnes // 2, nb_lignes // 2)

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
        jeu[x][y] = "C"
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
    joueur_x, joueur_y = joueur_pos
    case_x, case_y = case_pos

    dx = case_x - joueur_x
    dy = case_y - joueur_y
    distance = math.sqrt(dx * dx + dy * dy)

    if distance * taille_case <= rayon_vision_proche:
        return not a_mur_entre(joueur_pos, case_pos, jeu)

    if not est_dans_cone(joueur_pos, case_pos, angle_de_vue, cone_longueur):
        return False

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
    surface_virtuelle = pygame.Surface((largeur, hauteur))
    surface_virtuelle.fill(noir)
    
    marge = 2
    debut_x = max(0, int(camera_offset[0] // taille_case) - marge)
    debut_y = max(0, int(camera_offset[1] // taille_case) - marge)
    fin_x = min(
        len(jeu[0]), int((camera_offset[0] + largeur) // taille_case) + marge
    )
    fin_y = min(len(jeu), int((camera_offset[1] + hauteur) // taille_case) + marge)

    cam_x = camera_offset[0]
    cam_y = camera_offset[1]

    temp_surface = pygame.Surface((largeur, hauteur))
    temp_surface.fill(noir)

    for i in range(debut_y, fin_y):
        y = i * taille_case - cam_y
        for j in range(debut_x, fin_x):
            x = j * taille_case - cam_x
            if jeu[i][j] == "#":
                pygame.draw.rect(temp_surface, mur, (x, y, taille_case, taille_case))
            else:
                pygame.draw.rect(temp_surface, sol, (x, y, taille_case, taille_case))

    surface_virtuelle.blit(temp_surface, (0, 0))

    joueur_centre = (
        joueur_pos[0] * taille_case - cam_x + taille_case // 2,
        joueur_pos[1] * taille_case - cam_y + taille_case // 2,
    )
    appliquer_masque_vision(
        surface_virtuelle, joueur_centre, angle_de_vue, cone_longueur
    )

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

    rotation_angle = -(angle_de_vue + 90)
    joueur_rotated = pygame.transform.rotate(joueur, rotation_angle)

    joueur_x -= (joueur_rotated.get_width() - joueur.get_width()) // 2
    joueur_y -= (joueur_rotated.get_height() - joueur.get_height()) // 2

    surface_virtuelle.blit(joueur_rotated, (joueur_x, joueur_y))

    scaled_surface = pygame.transform.scale(surface_virtuelle, (largeur, hauteur))
    fenetre.blit(scaled_surface, (0, 0))


def deplacement_valide(jeu, pos):
    x, y = pos
    if 0 <= y < len(jeu) and 0 <= x < len(jeu[0]):
        return jeu[y][x] != "#"
    return False


def afficher_victoire():
    arreter_musique()
    fenetre.fill(noir)
    texte = pygame.font.Font(None, 60).render("Victoire !", True, blanc)
    texte_rect = texte.get_rect(center=(largeur // 2, hauteur // 2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    pygame.time.delay(3000)


def afficher_credits():
    vitesse_scroll = 5
    taille_titre = 100
    taille_nom = 80
    taille_roles = 50
    espacement = 120
    espacement_2 = 30
    espacement_3 = 200

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

    total_height = sum([size if text == "" else 80 for text, size in credits_data])
    y_offset = float(hauteur)

    while True:
        fenetre.fill(dark_purple)

        current_y = int(y_offset)

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

        y_offset -= vitesse_scroll

        if y_offset < -total_height:
            y_offset = float(hauteur)

        pygame.display.flip()
        horloge.tick(60)


def bords_arrondis(surface, couleur, rect, radius):
    x, y, width, height = rect

    pygame.draw.circle(surface, couleur, (x + radius, y + radius), radius)
    pygame.draw.circle(surface, couleur, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, couleur, (x + radius, y + height - radius), radius)
    pygame.draw.circle(
        surface, couleur, (x + width - radius, y + height - radius), radius
    )

    pygame.draw.rect(surface, couleur, (x + radius, y, width - 2 * radius, height))
    pygame.draw.rect(surface, couleur, (x, y + radius, width, height - 2 * radius))


def draw_button(surface, rect, text, font, hover_color, default_color, text_color, border_radius=15, icon_text=None, icon_font=None):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_x, mouse_y):
        color = hover_color
    else:
        color = default_color

    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    
    if icon_text and icon_font:
        icon_surface = icon_font.render(icon_text, True, text_color)
        icon_rect = icon_surface.get_rect(center=(rect.left + 30, rect.centery))
        surface.blit(icon_surface, icon_rect)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(icon_rect.right + 10, rect.centery))
    else:
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
    
    surface.blit(text_surface, text_rect)


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

    cles_collectees = 0
    # sprays_collectees = 0
    # bandages_collectes = 0
    # endurance_actuelle = endurance_max

    pygame.mouse.set_visible(True)
    musique_menu()

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

    facteurs_parralaxe = [0.02, 0.04, 0.08, 0.12, 0.16]
    decalage_x_initial = -150

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        center_x = largeur / 2
        center_y = hauteur / 2
        rel_x = (mouse_x - center_x) / (center_x * 0.7)
        rel_y = (mouse_y - center_y) / (center_y * 0.7)

        for i, layer in enumerate(couches_fond):
            decalage_x = decalage_x_initial - rel_x * facteurs_parralaxe[i] * (echelle_largeur - largeur)
            decalage_y = -rel_y * facteurs_parralaxe[i] * (echelle_hauteur - hauteur)
            fenetre.blit(layer, (decalage_x, decalage_y))

        logo_rect = scaled_logo.get_rect(center=(largeur // 2, hauteur // 4.5))
        fenetre.blit(scaled_logo, logo_rect)

        espace_boutton = 150  # Adjusted space between buttons
        y_depart = hauteur // 2.5
        boutons = [
            (pygame.Rect(largeur // 2 - 250, y_depart, 500, 90), "Nouvelle Partie", 40),
            (pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton, 500, 90), "Paramètres", 40),
            (pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 2, 500, 90), "Crédits", 40),
            (pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 3, 500, 90), "Quitter", 40),
        ]

        for bouton, texte, taille_texte in boutons:
            draw_button(fenetre, bouton, texte, pygame.font.Font(font_helpme, taille_texte), hover_purple, light_purple, blanc)

        pygame.display.flip()

        for event in pygame.event.get():
            result = handle_event(event, boutons)
            if result == "nouvelle_partie":
                return


def afficher_menu_pause():
    pygame.mouse.set_visible(True)
    global resolution_index, largeur, hauteur, fenetre

    fond = pygame.image.load(fond_1)
    fond = pygame.transform.scale(fond, (largeur, hauteur))

    while True:
        fenetre.blit(fond, (0, 0))

        titre = pygame.font.Font(font_november, 100).render(nom, True, blanc)
        titre_rect = titre.get_rect(center=(largeur // 2, hauteur // 6))
        fenetre.blit(titre, titre_rect)

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
            draw_button(fenetre, bouton, texte, pygame.font.Font(font_helpme, taille_texte), '#6428a0', '#301934', blanc)

        pygame.display.flip()

        for event in pygame.event.get():
            result = handle_event(event, boutons)
            if result in ["continuer", "recommencer", "menu"]:
                return result
            if result == "escape":
                return


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

    icone_cle = pygame.Rect(
        fond_rect.x + 5,
        fond_rect.y + (fond_rect.height - taille_icone) // 2,
        taille_icone,
        taille_icone,
    )
    pygame.draw.rect(surface, cle, icone_cle)

    texte = f"{cles_collectees}/{nombre_cles_total}"
    police = pygame.font.Font(None, 36)
    surface_texte = police.render(texte, True, blanc)
    pos_texte_x = icone_cle.right + espacement
    pos_texte_y = fond_rect.y + (fond_rect.height - surface_texte.get_height()) // 2

    surface.blit(surface_texte, (pos_texte_x, pos_texte_y))


def dessiner_inventaire(surface):
    inventaire_x = 30
    inventaire_y = hauteur - 70
    case_taille = 50
    espacement = 10
    nombre_cases = 5

    for i in range(nombre_cases):
        x = inventaire_x + (case_taille + espacement) * i
        rect = pygame.Rect(x, inventaire_y, case_taille, case_taille)

        if i == index_case_selectionnee:
            pygame.draw.rect(surface, (100, 100, 100), rect)
            pygame.draw.rect(surface, blanc, rect, 3)
        else:
            pygame.draw.rect(surface, (50, 50, 50), rect)
            pygame.draw.rect(surface, gris, rect, 1)


def afficher_parametres():
    global resolution_index, largeur, hauteur, fenetre, plein_ecran, montrer_fps, volume, controles

    section_choisie = 0  # 0 = Affichage, 1 = Son, 2 = Contrôles
    sections = ["Affichage", "Son", "Contrôles"]

    slider_rect = pygame.Rect(0, 0, 200, 10)
    slider_rect_volume = pygame.Rect(0, 0, 200, 10)
    slider_pos_volume = volume * 100
    texte_parametre = str(slider_pos_volume)
    texte_volume = str(int(slider_pos_volume))
    glisse_slider = False
    glisse_slider_volume = False

    controle_selectione = None
    texte_controles = ["Haut", "Bas", "Gauche", "Droite"]

    section_alpha = [100] * len(sections)
    section_target_alpha = [100] * len(sections)
    section_alpha[section_choisie] = 255
    section_target_alpha[section_choisie] = 255
    section_alpha_speed = 5

    presets = {
        "ZQSD": {"Haut": pygame.K_z, "Bas": pygame.K_s, "Gauche": pygame.K_q, "Droite": pygame.K_d},
        "WASD": {"Haut": pygame.K_w, "Bas": pygame.K_s, "Gauche": pygame.K_a, "Droite": pygame.K_d},
        "Flèches": {"Haut": pygame.K_UP, "Bas": pygame.K_DOWN, "Gauche": pygame.K_LEFT, "Droite": pygame.K_RIGHT},
        "Personalizé": controles
    }
    preset_selectionne = "Personalizé"

    while True:
        fenetre.fill(pygame.Color(dark_purple))  # Ensure dark_purple is used here
        center_x = largeur // 2

        bouton_retour = pygame.Rect(50, 50, 200, 60)
        draw_button(fenetre, bouton_retour, "Retour", pygame.font.Font(font_helpme, 30), hover_purple, light_purple, blanc, icon_text="B", icon_font=pygame.font.Font(font_arrows, 30))

        bouton_sauvegarde = pygame.Rect(center_x - 150, hauteur - 150, 300, 60)
        draw_button(fenetre, bouton_sauvegarde, "Sauvegarder", pygame.font.Font(font_helpme, 30), hover_purple, light_purple, blanc)

        section_largeur_totale = sum([200 for _ in sections])
        section_x_debut = (largeur - section_largeur_totale) // 2

        for i, section in enumerate(sections):
            couleur = blanc if i == section_choisie else gris
            texte = pygame.font.Font(None, 40).render(section, True, couleur)
            texte.set_alpha(section_alpha[i])
            texte_rect = texte.get_rect(center=(section_x_debut + i * 200 + 100, 150))
            fenetre.blit(texte, texte_rect)

            if section_alpha[i] < section_target_alpha[i]:
                section_alpha[i] = min(section_alpha[i] + section_alpha_speed, section_target_alpha[i])
            elif section_alpha[i] > section_target_alpha[i]:
                section_alpha[i] = max(section_alpha[i] - section_alpha_speed, section_target_alpha[i])

        if section_choisie == 0:
            for i, (width, height) in enumerate(resolutions):
                resolution_texte = f"{width} x {height}"
                couleur = blanc if i == resolution_index else gris
                texte = pygame.font.Font(None, 40).render(resolution_texte, True, couleur)
                texte_rect = texte.get_rect(center=(largeur // 2, 250 + i * 50))

                if i == resolution_index:
                    case_rect = texte_rect.inflate(20, 10)
                    pygame.draw.rect(fenetre, light_purple, case_rect)
                    pygame.draw.rect(fenetre, blanc, case_rect, 2)

                fenetre.blit(texte, texte_rect)

            texte_plein_ecran = "Plein écran: " + ("Oui" if plein_ecran else "Non")
            couleur = blanc if plein_ecran else gris
            texte = pygame.font.Font(None, 40).render(texte_plein_ecran, True, couleur)
            texte_rect = texte.get_rect(center=(largeur // 2, 250 + len(resolutions) * 50))
            fenetre.blit(texte, texte_rect)

            texte_fps = "Afficher les FPS: " + ("Oui" if montrer_fps else "Non")
            couleur = blanc if montrer_fps else gris
            texte = pygame.font.Font(None, 40).render(texte_fps, True, couleur)
            texte_rect = texte.get_rect(center=(largeur // 2, 250 + (len(resolutions) + 1) * 50))
            fenetre.blit(texte, texte_rect)

        elif section_choisie == 1:
            center_x = largeur // 2

            texte = pygame.font.Font(None, 40).render("Volume:", True, blanc)
            texte_rect = texte.get_rect(center=(center_x - 150, 250))
            fenetre.blit(texte, texte_rect)

            slider_rect_volume.centerx = center_x
            slider_rect_volume.centery = 300
            pygame.draw.rect(fenetre, gris, slider_rect_volume)
            pygame.draw.rect(fenetre, blanc, slider_rect_volume, 2)

            volume_handle_pos = slider_rect_volume.left + (slider_pos_volume / 100) * slider_rect_volume.width
            pygame.draw.circle(fenetre, blanc, (volume_handle_pos, slider_rect_volume.centery), 8)

            font = pygame.font.Font(None, 40)
            volume_text_surface = font.render(texte_volume, True, blanc)
            volume_texte_rect = volume_text_surface.get_rect(center=(center_x + 150, 300))
            fenetre.blit(volume_text_surface, volume_texte_rect)

        elif section_choisie == 2:
            preset_y = 300
            preset_x = center_x - 130  # Adjust the x position for presets column
            control_x = center_x + 130  # Adjust the x position for controls column

            # Draw "Presets" label
            texte_presets = pygame.font.Font(None, 40).render("Presets:", True, blanc)
            texte_presets_rect = texte_presets.get_rect(center=(preset_x, preset_y - 50))
            fenetre.blit(texte_presets, texte_presets_rect)

            # Draw "Controls" label
            texte_controls = pygame.font.Font(None, 40).render("Controls:", True, blanc)
            texte_controls_rect = texte_controls.get_rect(center=(control_x, preset_y - 50))
            fenetre.blit(texte_controls, texte_controls_rect)

            for preset in presets:
                couleur = blanc if preset == preset_selectionne else gris2
                texte = pygame.font.Font(None, 40).render(preset, True, couleur)
                texte_rect = texte.get_rect(center=(preset_x, preset_y))
                fenetre.blit(texte, texte_rect)
                preset_y += 50

            control_y = 300  # Adjusted y position for controls column
            for i, action in enumerate(texte_controles):
                key_name = pygame.key.name(controles[action]).upper()
                couleur = blanc if preset_selectionne == "Personalizé" else gris2
                texte = pygame.font.Font(None, 40).render(f"{action}: {key_name}", True, couleur)
                texte_rect = texte.get_rect(center=(control_x, control_y + i * 50))
                fenetre.blit(texte, texte_rect)

                if preset_selectionne == "Personalizé":
                    if controle_selectione == action:
                        pygame.draw.rect(fenetre, (100, 100, 100), texte_rect.inflate(10, 10), 2)
                    elif texte_rect.collidepoint(pygame.mouse.get_pos()):
                        pygame.draw.rect(fenetre, (100, 100, 100), texte_rect.inflate(10, 10), 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_LEFT and section_choisie > 0:
                    section_choisie -= 1
                    section_target_alpha[section_choisie + 1] = 100
                    section_target_alpha[section_choisie] = 255
                elif event.key == pygame.K_RIGHT and section_choisie < len(sections) - 1:
                    section_choisie += 1
                    section_target_alpha[section_choisie - 1] = 100
                    section_target_alpha[section_choisie] = 255
                elif controle_selectione and preset_selectionne == "Personalizé":
                    controles[controle_selectione] = event.key
                    controle_selectione = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if bouton_retour.collidepoint(event.pos):
                    return
                if bouton_sauvegarde.collidepoint(event.pos):
                    save_settings()
                if mouse_y < 200:
                    for i in range(len(sections)):
                        if section_x_debut + i * 200 <= mouse_x <= section_x_debut + (i + 1) * 200:
                            section_choisie = i
                            section_target_alpha = [100] * len(sections)
                            section_target_alpha[section_choisie] = 255

                elif section_choisie == 0:
                    if not plein_ecran:
                        for i in range(len(resolutions)):
                            if 250 <= mouse_y <= 250 + len(resolutions) * 50:
                                click_y = (mouse_y - 250) // 50
                                if click_y < len(resolutions):
                                    resolution_index = click_y
                                    largeur, hauteur = resolutions[resolution_index]
                                    fenetre = pygame.display.set_mode((largeur, hauteur), pygame.RESIZABLE)
                                    os.environ["SDL_VIDEO_CENTERED"] = "1"

                    if 250 + len(resolutions) * 50 - 25 <= mouse_y <= 250 + len(resolutions) * 50 + 25:
                        plein_ecran = not plein_ecran
                        flags = pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE
                        fenetre = pygame.display.set_mode((largeur, hauteur), flags)

                    if 250 + (len(resolutions) + 1) * 50 - 25 <= mouse_y <= 250 + (len(resolutions) + 1) * 50 + 25:
                        montrer_fps = not montrer_fps

                elif section_choisie == 1:
                    if slider_rect_volume.collidepoint(event.pos):
                        glisse_slider_volume = True
                        slider_pos_volume = (mouse_x - slider_rect_volume.left) / slider_rect_volume.width * 100
                        slider_pos_volume = max(0, min(100, slider_pos_volume))
                        texte_volume = str(int(slider_pos_volume))
                        volume = slider_pos_volume / 100
                        pygame.mixer.music.set_volume(volume)
                elif event.type == pygame.MOUSEBUTTONUP:
                    glisse_slider_volume = False
                elif event.type == pygame.MOUSEMOTION:
                    mouse_x = event.pos[0]
                    if glisse_slider_volume and slider_rect_volume.left <= mouse_x <= slider_rect_volume.right:
                        slider_pos_volume = (mouse_x - slider_rect_volume.left) / slider_rect_volume.width * 100
                        slider_pos_volume = max(0, min(100, slider_pos_volume))
                        texte_volume = str(int(slider_pos_volume))
                        volume = slider_pos_volume / 100
                        pygame.mixer.music.set_volume(volume)

                elif section_choisie == 2:
                    preset_y = 300
                    for preset in presets:
                        preset_rect = pygame.Rect(preset_x - 100, preset_y - 20, 200, 40)
                        if preset_rect.collidepoint(event.pos):
                            preset_selectionne = preset
                            controles = presets[preset]
                            break
                        preset_y += 50

                    if preset_selectionne == "Personalizé":
                        for i, action in enumerate(texte_controles):
                            texte_rect = pygame.font.Font(None, 40).render(f"{action}: {pygame.key.name(controles[action]).upper()}", True, blanc).get_rect(center=(control_x, 300 + i * 50))
                            if texte_rect.collidepoint(event.pos):
                                controle_selectione = action

        pygame.display.flip()


def dessiner_fps(surface, clock):
    if montrer_fps:
        fps = int(clock.get_fps())
        police = pygame.font.Font(None, 36)
        surface_texte = police.render(f"FPS: {fps}", True, blanc)
        surface.blit(surface_texte, (10, 10))


def musique_menu():
    pygame.mixer.music.load(son_menu)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)

def musique_fond():
    pygame.mixer.music.load(son_fond)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)


def arreter_musique():
    pygame.mixer.music.stop()


def afficher_transition_niveau(niveau):
    texte_niveau = pygame.font.Font(None, 150).render(f"Niveau {niveau}", True, blanc)
    texte_niveau_rect = texte_niveau.get_rect(center=(largeur // 2, hauteur // 2 - 75))

    texte_sous_titre = pygame.font.Font(None, 100).render(
        "Dans les abysses", True, blanc
    )
    texte_sous_titre_rect = texte_sous_titre.get_rect(
        center=(largeur // 2, hauteur // 2 + 75)
    )

    for alpha in range(0, 256, 5):
        fenetre.fill(dark_purple)
        texte_niveau.set_alpha(alpha)
        texte_sous_titre.set_alpha(alpha)
        fenetre.blit(texte_niveau, texte_niveau_rect)
        fenetre.blit(texte_sous_titre, texte_sous_titre_rect)
        pygame.display.flip()
        pygame.time.delay(10)

    pygame.time.delay(3000)

    for alpha in range(255, -1, -5):
        fenetre.fill(dark_purple)
        texte_niveau.set_alpha(alpha)
        texte_sous_titre.set_alpha(alpha)
        fenetre.blit(texte_niveau, texte_niveau_rect)
        fenetre.blit(texte_sous_titre, texte_sous_titre_rect)
        pygame.display.flip()
        pygame.time.delay(10)


''' barre d'endurance
def dessiner_barre_endurance(surface):
    largeur_barre = 200
    hauteur_barre = 20
    x = 30
    y = hauteur - 100

    largeur_actuelle = int((endurance_actuelle / endurance_max) * largeur_barre)

    pygame.draw.rect(surface, gris, (x, y, largeur_barre, hauteur_barre))
    pygame.draw.rect(surface, (0, 255, 0), (x, y, largeur_actuelle, hauteur_barre))
    pygame.draw.rect(surface, blanc, (x, y, largeur_barre, hauteur_barre), 2)
    '''


def load_settings():
    global resolution_index, largeur, hauteur, plein_ecran, montrer_fps, volume, controles
    parametres_par_defaut = {
        "resolution_index": 5,
        "plein_ecran": True,
        "montrer_fps": False,
        "volume": 0.5,
        "controles": {
            "Haut": pygame.K_z,
            "Bas": pygame.K_s,
            "Gauche": pygame.K_q,
            "Droite": pygame.K_d
        }
    }
    try:
        with open(fichier_parametres, "r") as file:
            settings = json.load(file)
            resolution_index = settings.get("resolution_index", parametres_par_defaut["resolution_index"])
            largeur, hauteur = resolutions[resolution_index]
            plein_ecran = settings.get("plein_ecran", parametres_par_defaut["plein_ecran"])
            montrer_fps = settings.get("montrer_fps", parametres_par_defaut["montrer_fps"])
            volume = settings.get("volume", parametres_par_defaut["volume"])
            pygame.mixer.music.set_volume(volume)
            controles = settings.get("controles", parametres_par_defaut["controles"])
    except FileNotFoundError:
        save_settings(parametres_par_defaut)

def save_settings(settings=None):
    if settings is None:
        settings = {
            "resolution_index": resolution_index,
            "plein_ecran": plein_ecran,
            "montrer_fps": montrer_fps,
            "volume": volume,
            "controles": controles
        }
    with open(fichier_parametres, "w") as file:
        json.dump(settings, file, indent=4)

jeu = generer_jeu(nombre_lignes, nombre_colonnes)
cles = placer_cles(jeu, nombre_cles)
ennemis = initialiser_ennemis(jeu, nombre_ennemis)

load_settings()
pygame.mixer.music.set_volume(volume)
afficher_menu()
pygame.mouse.set_visible(False)
musique_fond()
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
            if event.button == 4:
                index_case_selectionnee = max(0, index_case_selectionnee - 1)
            elif event.button == 5:
                index_case_selectionnee = min(4, index_case_selectionnee + 1)

    souris_x, souris_y = pygame.mouse.get_pos()

    joueur_ecran_x = joueur_pos[0] * taille_case - camera_offset[0] + taille_case // 2
    joueur_ecran_y = joueur_pos[1] * taille_case - camera_offset[1] + taille_case // 2

    dx = souris_x - joueur_ecran_x
    dy = souris_y - joueur_ecran_y
    angle_de_vue = math.degrees(math.atan2(dy, dx))

    touches = pygame.key.get_pressed()
    nouvelle_pos = joueur_pos[:]

    temps_actuel = pygame.time.get_ticks()
    if temps_actuel - dernier_mouvement >= delai_mouvement:
        if touches[controles["Haut"]]:
            nouvelle_pos[1] -= 1
            dernier_mouvement = temps_actuel
        elif touches[controles["Bas"]]:
            nouvelle_pos[1] += 1
            dernier_mouvement = temps_actuel
        elif touches[controles["Gauche"]]:
            nouvelle_pos[0] -= 1
            dernier_mouvement = temps_actuel
        elif touches[controles["Droite"]]:
            nouvelle_pos[0] += 1
            dernier_mouvement = temps_actuel

    if deplacement_valide(jeu, nouvelle_pos):
        joueur_pos = nouvelle_pos

    camera_offset[0] = joueur_pos[0] * taille_case - largeur // 2
    camera_offset[1] = joueur_pos[1] * taille_case - hauteur // 2

    if verifier_collision_ennemis(joueur_pos, ennemis):
        if game_over() == "menu":
            jeu = generer_jeu(nombre_lignes, nombre_colonnes)
            cles = placer_cles(jeu, nombre_cles)
            joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
            cles_collectees = 0
            ennemis = initialiser_ennemis(jeu, nombre_ennemis)
            afficher_menu()

    dessiner_jeu(jeu, joueur_pos, camera_offset)

    dessiner_inventaire(fenetre)

    if jeu[joueur_pos[1]][joueur_pos[0]] == "C":
        cles_collectees += 1
        jeu[joueur_pos[1]][joueur_pos[0]] = " "

    deplacer_ennemis(jeu, ennemis, joueur_pos)

    for ennemi in ennemis:
        x = ennemi.x * taille_case - camera_offset[0]
        y = ennemi.y * taille_case - camera_offset[1]

        dx = ennemi.x - joueur_pos[0]
        dy = ennemi.y - joueur_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)

        if distance * taille_case <= rayon_vision_proche:
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), jeu):
                pygame.draw.rect(fenetre, ennemi_couleur, (x, y, taille_case, taille_case))
        elif est_dans_cone(
            joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, cone_longueur
        ):
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), jeu):
                pygame.draw.rect(fenetre, ennemis, (x, y, taille_case, taille_case))

    if jeu[joueur_pos[1]][joueur_pos[0]] == "S" and cles_collectees == nombre_cles:
        arreter_musique()
        afficher_victoire()
        running = False

    dessiner_compteur_cles(fenetre, cles_collectees, nombre_cles)

    if not pygame.mouse.get_visible():
        mouse_x, mouse_y = pygame.mouse.get_pos()
        crosshair_size = 5
        crosshair_color = blanc

        pygame.draw.line(
            fenetre,
            crosshair_color,
            (mouse_x - crosshair_size, mouse_y),
            (mouse_x + crosshair_size, mouse_y),
            1
        )

        pygame.draw.line(
            fenetre,
            crosshair_color,
            (mouse_x, mouse_y - crosshair_size),
            (mouse_x, mouse_y + crosshair_size),
            1
        )

    dessiner_fps(fenetre, horloge)
    # dessiner_barre_endurance(fenetre)

    pygame.display.flip()
    horloge.tick(60)

pygame.quit().tick(60)
pygame.quit()
