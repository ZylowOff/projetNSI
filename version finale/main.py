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
taille_case = int(min(largeur, hauteur) / 20)
nombre_lignes = (hauteur // taille_case) * 2
nombre_colonnes = (largeur // taille_case) * 2
rayon_vision_proche = taille_case * 2
cone_longueur = min(largeur, hauteur) / 2
cone_angle = 60

icone = pygame.image.load("icone.png")

logo_img = pygame.image.load("logo.png")
largeur_voulue = largeur // 3
ratio_aspect = logo_img.get_height() / logo_img.get_width()
logo = pygame.transform.scale(logo_img, (largeur_voulue, int(largeur_voulue * ratio_aspect)))

font_helpme = "HelpMe.ttf"

fichier_parametres = "settings.json"
volume = 0.5
controles = {
    "Haut": pygame.K_z,
    "Bas": pygame.K_s,
    "Gauche": pygame.K_q,
    "Droite": pygame.K_d
}
plein_ecran = True
montrer_fps = False

try:
    musique_poursuite = pygame.mixer.Sound("./OST/outlast_run.mp3")
    musique_poursuite.set_volume(0.5)
except:
    print("Erreur lors du chargement de la musique de poursuite")
    musique_poursuite = None

try:
    son_pas = pygame.mixer.Sound("./OST/course.wav")
    son_course = pygame.mixer.Sound("./OST/course.wav")
    son_pas.set_volume(100)
    son_course.set_volume(100)
except:
    print("Erreur lors du chargement des sons de pas")
    son_pas = None
    son_course = None
son_pas_actif = False
son_course_actif = False
est_en_poursuite = False
temps_perdu_vue = 0
delai_arret_musique = 120
temps_dernier_pas = 0
delai_pas_marche = 500
delai_pas_course = 300
son_en_cours = None
musique_ambiance = None
musique_ambiance_position = 0

nombre_cles = 3
cles_collectees = 3
nombre_ennemis = 1
vitesse_ennemis = 0.6

joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
camera_offset = [0, 0]
angle_de_vue = 270

liste_ennemis = []

delai_mouvement = 100
dernier_mouvement = 0

index_case_selectionnee = 0

resolutions = [
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
    (largeur, hauteur)
]
resolution_index = 0

endurance_max = 100
endurance_actuelle = endurance_max
taux_diminution = 0.5
taux_recuperation = 0.2
delai_mouvement_normal = 100
delai_mouvement_rapide = 40

vitesse_partrouile = 0.15
vitesse_poursuite = 0.25
vitesse_ralenti = 0.1

vitesse_base = 0.25
vitesse_sprint = 0.35
derniere_position = [0, 0]

nombre_sprays = 2
sprays_collectes = 0

spray_actif = False
temps_spray = 0
duree_affichage_spray = 500

niveau_actuel = 1

nombre_bouteilles = 2
bouteilles_collectees = 0
bouteilles_lancees = []
vitesse_bouteille = 0.5
vitesse_distraction = 180

inventaire = [None] * 5

noir = '#000000'
blanc = '#ffffff'
gris = '#808080'
gris_fonce = '#323232'
gris_clair = '#969696'
gris2 = '#584a5a'
bordeaux = '#280000'
couleur_ennemis = (255, 0, 0, 1)
spray = '#ffa500'
marron_spray = (139, 69, 19, 100)
joueur = '#0000ff'
violet_fonce = '#180c1a'
violet = '#4b0082'
violet_hover = '#6428a0'
sortie = '#00ff00'
mur = '#64281e'
sol = '#736d73'
cle = '#ffdf00'
bouteille_verre = '#8b4513'

joueur_img = pygame.image.load("./texture/personnage.png")
joueur = pygame.transform.scale(joueur_img, (taille_case * 1.25, taille_case * 1.25))

zombie_img = pygame.image.load("./texture/zombie.png")
zombie_img = pygame.transform.scale(zombie_img, (taille_case * 1.25, taille_case * 1.25))

fenetre = pygame.display.set_mode((largeur, hauteur), pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE)
pygame.display.set_caption("Echoes of the Hollow")
pygame.display.set_icon(icone)

horloge = pygame.time.Clock()


class Ennemi:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.pas_patrouille = 0
        self.max_pas_patrouille = random.randint(5, 10)
        self.derniere_pos_joueur = None
        self.temps_memoire = 0
        self.duree_memoire_max = 180
        self.vitesse_patrouille = vitesse_partrouile
        self.vitesse_poursuite = vitesse_poursuite
        self.vitesse_actuelle = self.vitesse_patrouille
        self.ralenti = False
        self.temps_ralenti = 0
        self.distrait = False
        self.temps_distraction = 0

    def peut_voir_joueur(self, joueur_pos, jeu):
        if self.distrait:
            return False
        if self.ralenti:
            return False
            
        dx = joueur_pos[0] - self.x
        dy = joueur_pos[1] - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 8:
            return False
            
        return not a_mur_entre([self.x, self.y], joueur_pos, jeu)

    def mettre_a_jour(self, jeu, joueur_pos):
        if self.distrait:
            if self.temps_distraction > 0:
                self.temps_distraction -= 1
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

class BouteilleLancee:
    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle
        angle_rad = math.radians(angle)
        self.dx = math.cos(angle_rad) * 0.8
        self.dy = -math.sin(angle_rad) * 0.8
        self.brisee = False
        self.temps_brisure = 0
        self.position_brisure = None


def gerer_evenement(event, boutons):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    if event.type == pygame.MOUSEBUTTONDOWN and event.button < 4:
        for bouton in boutons:
            if len(bouton) == 3:
                bouton_rect, texte, _ = bouton
            else:
                bouton_rect, texte = bouton

            if bouton_rect.collidepoint(event.pos):
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

def dessiner_bouton(surface, rect, text, font, hover_color, default_color, text_color, border_radius=15, icon_text=None, icon_font=None):
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

def bords_arrondis(surface, color, rect, radius):
    x, y, width, height = rect

    pygame.draw.circle(surface, color, (x + radius, y + radius), radius)
    pygame.draw.circle(
        surface, color, (x + width - radius, y + radius), radius)
    pygame.draw.circle(surface, color, (x + radius,
                       y + height - radius), radius)
    pygame.draw.circle(surface, color, (x + width - radius,
                       y + height - radius), radius)

    pygame.draw.rect(surface, color, (x + radius, y, width - 2*radius, height))
    pygame.draw.rect(surface, color, (x, y + radius, width, height - 2*radius))


def afficher_menu():
    global cles_collectees, sprays_collectes, bouteilles_collectees, endurance_actuelle
    
    cles_collectees = 0
    sprays_collectes = 0
    bouteilles_collectees = 0
    endurance_actuelle = endurance_max
    
    pygame.mouse.set_visible(True)
    musique_menu()

    background_layers = [
        pygame.image.load("./texture/background_1.png"),
        pygame.image.load("./texture/background_2.png"),
        pygame.image.load("./texture/background_3.png"),
        pygame.image.load("./texture/background_4.png"),
        pygame.image.load("./texture/background_5.png")
    ]
    
    scale_factor = 1.3
    scaled_width = int(largeur * scale_factor)
    scaled_height = int(hauteur * scale_factor)
    background_layers = [pygame.transform.scale(layer, (scaled_width, scaled_height)) 
                        for layer in background_layers]
    
    parallax_factors = [0.02, 0.04, 0.08, 0.12, 0.16]
    initial_offset_x = -150

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        center_x = largeur / 2
        center_y = hauteur / 2
        rel_x = (mouse_x - center_x) / (center_x * 0.7)
        rel_y = (mouse_y - center_y) / (center_y * 0.7)

        for i, layer in enumerate(background_layers):
            offset_x = initial_offset_x - rel_x * parallax_factors[i] * (scaled_width - largeur)
            offset_y = -rel_y * parallax_factors[i] * (scaled_height - hauteur)
            
            fenetre.blit(layer, (offset_x, offset_y))

        logo_rect = logo.get_rect(center=(largeur // 2, hauteur // 4.5))
        fenetre.blit(logo, logo_rect)

        espace_boutton = 150
        y_depart = hauteur // 2.5
        boutons = [
            (pygame.Rect(largeur // 2 - 250, y_depart, 500, 90), "Nouvelle Partie"),
            (pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton, 500, 90), "Paramètres"),
            (pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 2, 500, 90), "Crédits"),
            (pygame.Rect(largeur // 2 - 250, y_depart + espace_boutton * 3, 500, 90), "Quitter"),
        ]

        font = pygame.font.Font("./HelpMe.ttf", 40)
        for bouton, texte in boutons:
            dessiner_bouton(fenetre, bouton, texte, font, violet_hover, violet, blanc)

        pygame.display.flip()
        for event in pygame.event.get():
            result = gerer_evenement(event, boutons)
            if result:
                return result


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
        "Personnalisé": controles
    }
    preset_selectionne = "Personnalisé"

    while True:
        fenetre.fill(pygame.Color(violet_fonce))
        center_x = largeur // 2

        bouton_retour = pygame.Rect(50, 50, 200, 60)
        dessiner_bouton(fenetre, bouton_retour, "Retour", pygame.font.Font(font_helpme, 30), violet_hover, violet, blanc, icon_text="B", icon_font=pygame.font.Font("./Arrows.ttf", 30))

        bouton_sauvegarde = pygame.Rect(center_x - 150, hauteur - 150, 300, 60)
        dessiner_bouton(fenetre, bouton_sauvegarde, "Sauvegarder", pygame.font.Font(font_helpme, 30), violet_hover, violet, blanc)

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
                    pygame.draw.rect(fenetre, violet, case_rect)
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
            preset_x = center_x - 130
            control_x = center_x + 130

            texte_presets = pygame.font.Font(None, 40).render("Presets:", True, blanc)
            texte_presets_rect = texte_presets.get_rect(center=(preset_x, preset_y - 50))
            fenetre.blit(texte_presets, texte_presets_rect)

            texte_controls = pygame.font.Font(None, 40).render("Controls:", True, blanc)
            texte_controls_rect = texte_controls.get_rect(center=(control_x, preset_y - 50))
            fenetre.blit(texte_controls, texte_controls_rect)

            for preset in presets:
                couleur = blanc if preset == preset_selectionne else gris2
                texte = pygame.font.Font(None, 40).render(preset, True, couleur)
                texte_rect = texte.get_rect(center=(preset_x, preset_y))
                fenetre.blit(texte, texte_rect)
                preset_y += 50

            control_y = 300
            for i, action in enumerate(texte_controles):
                key_name = pygame.key.name(controles[action]).upper()
                couleur = blanc if preset_selectionne == "Personnalisé" else gris2
                texte = pygame.font.Font(None, 40).render(f"{action}: {key_name}", True, couleur)
                texte_rect = texte.get_rect(center=(control_x, control_y + i * 50))
                fenetre.blit(texte, texte_rect)

                if preset_selectionne == "Personnalisé":
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
                elif controle_selectione and preset_selectionne == "Personnalisé":
                    controles[controle_selectione] = event.key
                    controle_selectione = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if bouton_retour.collidepoint(event.pos):
                    return
                if bouton_sauvegarde.collidepoint(event.pos):
                    sauvegarder_parametres()
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

                    if preset_selectionne == "Personnalisé":
                        for i, action in enumerate(texte_controles):
                            texte_rect = pygame.font.Font(None, 40).render(f"{action}: {pygame.key.name(controles[action]).upper()}", True, blanc).get_rect(center=(control_x, 300 + i * 50))
                            if texte_rect.collidepoint(event.pos):
                                controle_selectione = action

        pygame.display.flip()

def charger_parametres():
    global resolution_index, largeur, hauteur, plein_ecran, montrer_fps, volume, controles

    parametres_par_defaut = {
        "resolution_index": 4,
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
            parametres = json.load(file)

            resolution_index = parametres.get("resolution_index", parametres_par_defaut["resolution_index"])
            largeur, hauteur = resolutions[resolution_index]
            plein_ecran = parametres.get("plein_ecran", parametres_par_defaut["plein_ecran"])
            montrer_fps = parametres.get("montrer_fps", parametres_par_defaut["montrer_fps"])
            volume = parametres.get("volume", parametres_par_defaut["volume"])
            pygame.mixer.music.set_volume(volume)
            controles = parametres.get("controles", parametres_par_defaut["controles"])

            flags = pygame.FULLSCREEN if plein_ecran else pygame.RESIZABLE
            fenetre = pygame.display.set_mode((largeur, hauteur), flags)

    except FileNotFoundError:
        sauvegarder_parametres(parametres_par_defaut)

def sauvegarder_parametres(parametres=None):
    if parametres is None:
        parametres = {
            "resolution_index": resolution_index,
            "plein_ecran": plein_ecran,
            "montrer_fps": montrer_fps,
            "volume": volume,
            "controles": controles
        }
    with open(fichier_parametres, "w") as file:
        json.dump(parametres, file, indent=4)


def afficher_credits():
    SCROLL_SPEED = 5
    TITLE_SIZE = 100
    NAME_SIZE = 80
    ROLE_SIZE = 50
    SPACING = 120
    SPACING_2 = 30
    SPACING_3 = 200
    
    credits_data = [
        ("Développeurs :", TITLE_SIZE),
        ("", SPACING_3),
        ("Iaroslav Lushcheko", NAME_SIZE),
        ("", SPACING_2),
        ("Programmation, Game Design", ROLE_SIZE),
        ("", SPACING),
        ("Eliott Raulet", NAME_SIZE),
        ("", SPACING_2),
        ("Level Design, Game Mechanics", ROLE_SIZE),
        ("", SPACING),
        ("Mohamed El Mekkawy", NAME_SIZE),
        ("", SPACING_2),
        ("UI/UX, Game Systems", ROLE_SIZE),
        ("", SPACING),
        ("Ugo Guillemart", NAME_SIZE),
        ("", SPACING_2),
        ("Sound Design, Testing", ROLE_SIZE),
        ("", SPACING_3),
    ]
    
    total_height = sum([size if text == "" else 80 for text, size in credits_data])
    y_offset = float(hauteur)
    
    while True:
        fenetre.fill(violet_fonce)
        
        current_y = int(y_offset)
        
        for text, size in credits_data:
            if text:
                texte = pygame.font.Font("./HelpMe.ttf", size).render(text, True, blanc)
                texte_rect = texte.get_rect(center=(largeur // 2, current_y))
                
                if -50 <= current_y <= hauteur + 50:
                    if size == TITLE_SIZE:
                        glow = pygame.font.Font("./HelpMe.ttf", size).render(text, True, (100, 100, 100))
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

        y_offset -= SCROLL_SPEED
        
        if y_offset < -total_height:
            y_offset = float(hauteur)
        
        pygame.display.flip()
        horloge.tick(60)


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
        fenetre.fill(violet_fonce)
        texte_niveau.set_alpha(alpha)
        texte_sous_titre.set_alpha(alpha)
        fenetre.blit(texte_niveau, texte_niveau_rect)
        fenetre.blit(texte_sous_titre, texte_sous_titre_rect)
        pygame.display.flip()
        pygame.time.delay(10)

    pygame.time.delay(3000)

    for alpha in range(255, -1, -5):
        fenetre.fill(violet_fonce)
        texte_niveau.set_alpha(alpha)
        texte_sous_titre.set_alpha(alpha)
        fenetre.blit(texte_niveau, texte_niveau_rect)
        fenetre.blit(texte_sous_titre, texte_sous_titre_rect)
        pygame.display.flip()
        pygame.time.delay(10)


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
                        if 0 <= (y + ny) // 2 + i < nb_lignes and 0 <= (x + nx) // 2 + j < nb_colonnes:
                            jeu[(y + ny) // 2 + i][(x + nx) // 2 + j] = " "
                départ(nx, ny)

    départ(nb_colonnes // 2, nb_lignes // 2)

    bords = [
        (0, random.randint(1, nb_colonnes - 2)),
        (nb_lignes - 1, random.randint(1, nb_colonnes - 2)),
        (random.randint(1, nb_lignes - 2), 0),
        (random.randint(1, nb_lignes - 2), nb_colonnes - 1)
    ]
    random.shuffle(bords)
    for sortie_y, sortie_x in bords:
        if jeu[sortie_y][sortie_x] == " ":
            jeu[sortie_y][sortie_x] = "S"
            break

    return jeu

def redimensionner_jeu(nouvelle_largeur, nouvelle_hauteur):
    global largeur, hauteur, taille_case, nombre_lignes, nombre_colonnes
    
    largeur = nouvelle_largeur
    hauteur = nouvelle_hauteur
    
    taille_case = int(min(largeur, hauteur) / 20)
    
    nombre_lignes = (hauteur // taille_case) * 2
    nombre_colonnes = (largeur // taille_case) * 2
    
    nouveau_jeu = generer_jeu(nombre_lignes, nombre_colonnes)
    
    placer_cles(nouveau_jeu, nombre_cles)
    placer_sprays(nouveau_jeu, nombre_sprays)
    
    return nouveau_jeu

def dessiner_jeu(jeu, joueur_pos, camera_offset):
    virtual_surface = pygame.Surface((largeur, hauteur))
    virtual_surface.fill(noir)

    marge = 2
    debut_x = max(0, int(camera_offset[0] // taille_case) - marge)
    debut_y = max(0, int(camera_offset[1] // taille_case) - marge)
    fin_x = min(len(jeu[0]), int((camera_offset[0] + largeur) // taille_case) + marge)
    fin_y = min(len(jeu), int((camera_offset[1] + hauteur) // taille_case) + marge)

    cam_x = camera_offset[0]
    cam_y = camera_offset[1]

    temp_surface = pygame.Surface((largeur, hauteur))
    temp_surface.fill(noir)

    for i in range(debut_y, fin_y):
        y = i * taille_case - cam_y
        for j in range(debut_x, fin_x):
            x = j * taille_case - cam_x
            couleur = mur if jeu[i][j] == "#" else sol
            pygame.draw.rect(temp_surface, couleur,
                             (x, y, taille_case, taille_case))

    virtual_surface.blit(temp_surface, (0, 0))

    joueur_centre = (
        joueur_pos[0] * taille_case - cam_x + taille_case // 2,
        joueur_pos[1] * taille_case - cam_y + taille_case // 2
    )
    appliquer_masque_vision(virtual_surface, joueur_centre, angle_de_vue, cone_longueur)

    for i in range(debut_y, fin_y):
        y = i * taille_case - cam_y
        for j in range(debut_x, fin_x):
            x = j * taille_case - cam_x
            case = jeu[i][j]
            if case in ["S", "C", "P", "V"]:
                if est_visible(joueur_pos, (j, i), jeu):
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

    if joueur:
        joueur_x = joueur_pos[0] * taille_case - camera_offset[0] - (joueur.get_width() - taille_case) // 2
        joueur_y = joueur_pos[1] * taille_case - camera_offset[1] - (joueur.get_height() - taille_case) // 2
        
        rotation_angle = -(angle_de_vue + 90)
        joueur_rotated = pygame.transform.rotate(joueur, rotation_angle)
        
        joueur_x -= (joueur_rotated.get_width() - joueur.get_width()) // 2
        joueur_y -= (joueur_rotated.get_height() - joueur.get_height()) // 2
        
        virtual_surface.blit(joueur_rotated, (joueur_x, joueur_y))
    else:
        pygame.draw.rect(virtual_surface, joueur, (
            joueur_pos[0] * taille_case - camera_offset[0],
            joueur_pos[1] * taille_case - camera_offset[1],
            taille_case, taille_case
        ))

    for ennemi in liste_ennemis:
        x = ennemi.x * taille_case - camera_offset[0]
        y = ennemi.y * taille_case - camera_offset[1]
        
        dx = ennemi.x - joueur_pos[0]
        dy = ennemi.y - joueur_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance * taille_case <= rayon_vision_proche:
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), jeu):
                angle = math.degrees(math.atan2(dy, dx))
                zombie_rotated = pygame.transform.rotate(zombie_img, angle)
                rect_rotated = zombie_rotated.get_rect(center=(x, y))
                virtual_surface.blit(zombie_rotated, rect_rotated)
        elif est_dans_cone(joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, cone_longueur):
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), jeu):
                angle = math.degrees(math.atan2(dy, dx))
                zombie_rotated = pygame.transform.rotate(zombie_img, angle)
                rect_rotated = zombie_rotated.get_rect(center=(x, y))
                virtual_surface.blit(zombie_rotated, rect_rotated)

    scaled_surface = pygame.transform.scale(virtual_surface, (largeur, hauteur))
    fenetre.blit(scaled_surface, (0, 0))

def deplacement_valide(jeu, pos):
    positions_a_verifier = [
        (int(pos[0]), int(pos[1])),
        (int(pos[0] + 0.9), int(pos[1])),
        (int(pos[0]), int(pos[1] + 0.9)),
        (int(pos[0] + 0.9), int(pos[1] + 0.9))
    ]
    
    for x, y in positions_a_verifier:
        if not (0 <= y < len(jeu) and 0 <= x < len(jeu[0])):
            return False
        if jeu[y][x] == "#":
            return False
    return True

def mettre_a_jour_camera(joueur_pos):
    global camera_offset
    
    camera_x = joueur_pos[0] * taille_case - largeur // 2
    camera_y = joueur_pos[1] * taille_case - hauteur // 2
    
    limite_droite = len(jeu[0]) * taille_case - largeur
    limite_bas = len(jeu) * taille_case - hauteur
    
    camera_x = max(0, min(camera_x, limite_droite))
    camera_y = max(0, min(camera_y, limite_bas))
    
    vitesse_camera = 0.1
    camera_offset[0] += (camera_x - camera_offset[0]) * vitesse_camera
    camera_offset[1] += (camera_y - camera_offset[1]) * vitesse_camera
    
    camera_offset[0] = max(0, min(camera_offset[0], limite_droite))
    camera_offset[1] = max(0, min(camera_offset[1], limite_bas))

def appliquer_masque_vision(surface, position, angle, longueur):
    masque = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    masque.fill((0, 0, 0, 200))

    x, y = position
    start_angle = math.radians(angle - cone_angle / 2)
    end_angle = math.radians(angle + cone_angle / 2)

    points = [(x, y)]

    steps = 30
    ray_step = 5

    angle_step = (end_angle - start_angle) / steps
    cos_angles = [math.cos(start_angle + i * angle_step) for i in range(steps + 1)]
    sin_angles = [math.sin(start_angle + i * angle_step) for i in range(steps + 1)]

    for i in range(steps + 1):
        cos_theta = cos_angles[i]
        sin_theta = sin_angles[i]
        
        for dist in range(0, int(longueur), ray_step):
            ray_x = x + dist * cos_theta
            ray_y = y + dist * sin_theta

            grille_x = int((ray_x + camera_offset[0]) / taille_case)
            grille_y = int((ray_y + camera_offset[1]) / taille_case)

            if (0 <= grille_y < len(jeu) and 
                0 <= grille_x < len(jeu[0]) and 
                jeu[grille_y][grille_x] == "#"):
                points.append((ray_x, ray_y))
                break
            elif dist >= longueur - ray_step:
                points.append((ray_x, ray_y))

    if len(points) > 2:
        pygame.draw.polygon(masque, (0, 0, 0, 0), points)

    pygame.draw.circle(masque, (0, 0, 0, 0), (int(x), int(y)), rayon_vision_proche)

    surface.blit(masque, (0, 0))

def dessiner_inventaire(surface):
    global index_case_selectionnee

    inv_x = 20
    inv_y = hauteur - 70
    case_taille = 50
    espacement = 10

    for i in range(len(inventaire)):
        x = inv_x + (case_taille + espacement) * i
        pygame.draw.rect(surface, gris_fonce, (x, inv_y, case_taille, case_taille))
        if i == index_case_selectionnee:
            pygame.draw.rect(surface, gris_clair, (x, inv_y, case_taille, case_taille), 2)
        else:
            pygame.draw.rect(surface, gris, (x, inv_y, case_taille, case_taille), 1)

        if inventaire[i] == "spray":
            pygame.draw.rect(surface, spray, (x + 5, inv_y + 5, case_taille - 10, case_taille - 10))
            texte = pygame.font.Font(None, 20).render(str(sprays_collectes), True, blanc)
            surface.blit(texte, (x + case_taille - 15, inv_y + case_taille - 15))
        elif inventaire[i] == "bouteille":
            pygame.draw.rect(surface, bouteille_verre, (x + 5, inv_y + 5, case_taille - 10, case_taille - 10))
            texte = pygame.font.Font(None, 20).render(str(bouteilles_collectees), True, blanc)
            surface.blit(texte, (x + case_taille - 15, inv_y + case_taille - 15))

    pygame.display.flip()

def placer_cles(jeu, nombre_cles):
    cles = []
    cases_vides = [(i, j) for i, ligne in enumerate(jeu)
                   for j, case in enumerate(ligne) if case == " "]
    for _ in range(nombre_cles):
        x, y = random.choice(cases_vides)
        cles.append((x, y))
        jeu[x][y] = "C"
        cases_vides.remove((x, y))
    return cles

def ajouter_objet(type_objet):
    """Ajoute un objet dans la première case disponible"""
    case = trouver_case_disponible()
    if case != -1:
        inventaire[case] = type_objet
        return True
    return False

def placer_sprays(jeu, nombre_sprays):
    cases_vides = [(j, i) for i, ligne in enumerate(jeu)
                   for j, case in enumerate(ligne) if case == " "]
    for _ in range(nombre_sprays):
        if cases_vides:
            x, y = random.choice(cases_vides)
            jeu[y][x] = "P"
            cases_vides.remove((x, y))

def placer_bouteilles(jeu, nombre):
    cases_vides = []
    for y in range(len(jeu)):
        for x in range(len(jeu[0])):
            if jeu[y][x] == " ":
                cases_vides.append((y, x))
    
    for _ in range(nombre):
        if cases_vides:
            y, x = random.choice(cases_vides)
            jeu[y][x] = "V"
            cases_vides.remove((y, x))

def dessiner_barre_endurance(surface):
    x = largeur - 220
    y = hauteur - 40
    largeur_max = 200
    hauteur_barre = 20
    
    pygame.draw.rect(surface, (50, 50, 50), (x, y, largeur_max, hauteur_barre))
    
    largeur_endurance = (endurance_actuelle / endurance_max) * largeur_max
    pygame.draw.rect(surface, (0, 255, 0), (x, y, largeur_endurance, hauteur_barre))
    
    pygame.draw.rect(surface, blanc, (x, y, largeur_max, hauteur_barre), 2)

def afficher_fps(surface, horloge):
    font = pygame.font.Font(None, 36)
    fps = int(horloge.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, blanc)
    surface.blit(fps_text, (10, 10))

def dessiner_compteur_cles(surface, cles_collectees, nombre_cles_total):
    marge = 20
    taille_icone = 30
    espacement = 10

    fond_rect = pygame.Rect(
        largeur - (marge + taille_icone + 80),
        marge,
        taille_icone + 80,
        taille_icone + 10
    )
    pygame.draw.rect(surface, bordeaux, fond_rect)
    pygame.draw.rect(surface, blanc, fond_rect, 2)

    icone_cle = pygame.Rect(
        largeur - (marge + taille_icone),
        marge + 5,
        taille_icone,
        taille_icone
    )
    pygame.draw.rect(surface, cle, icone_cle)

    texte = f"{cles_collectees}/{nombre_cles_total}"
    police = pygame.font.Font(None, 36)
    surface_texte = police.render(texte, True, blanc)
    pos_texte = (
        largeur - (marge + taille_icone + espacement +
                   surface_texte.get_width()),
        marge + 8
    )
    surface.blit(surface_texte, pos_texte)


def initialiser_ennemis(jeu, nombre_ennemis):
    liste_ennemis = []
    cases_vides = [(j, i) for i, ligne in enumerate(jeu)
                   for j, case in enumerate(ligne) if case == " "]
    for _ in range(nombre_ennemis):
        if cases_vides:
            x, y = random.choice(cases_vides)
            liste_ennemis.append(Ennemi(x, y))
            cases_vides.remove((x, y))
    return liste_ennemis

def deplacer_ennemis(jeu, liste_ennemis, joueur_pos):
    global est_en_poursuite, temps_perdu_vue, musique_ambiance_position
    joueur_est_vu = False
    temps_actuel = pygame.time.get_ticks()
    
    for ennemi in liste_ennemis:
        voit_joueur = ennemi.peut_voir_joueur(joueur_pos, jeu)
        
        if voit_joueur and not ennemi.ralenti:
            joueur_est_vu = True
            temps_perdu_vue = 0
            ennemi.vitesse_actuelle = ennemi.vitesse_poursuite
            ennemi.derniere_pos_joueur = joueur_pos[:]
            ennemi.temps_memoire = ennemi.duree_memoire_max
            
            if not est_en_poursuite:
                est_en_poursuite = True
                if musique_poursuite:
                    musique_ambiance_position = pygame.mixer.music.get_pos()
                    pygame.mixer.music.pause()
                    musique_poursuite.play(-1)
        
        elif not ennemi.ralenti:
            ennemi.vitesse_actuelle = ennemi.vitesse_patrouille
            
            if not ennemi.derniere_pos_joueur:
                ennemi.pas_patrouille += 1
                if ennemi.pas_patrouille >= ennemi.max_pas_patrouille:
                    ennemi.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                    ennemi.pas_patrouille = 0
                    ennemi.max_pas_patrouille = random.randint(5, 10)
                
                nouvelle_x = ennemi.x + ennemi.direction[0] * ennemi.vitesse_patrouille
                nouvelle_y = ennemi.y + ennemi.direction[1] * ennemi.vitesse_patrouille
                
                if deplacement_valide(jeu, [nouvelle_x, ennemi.y]):
                    ennemi.x = nouvelle_x
                if deplacement_valide(jeu, [ennemi.x, nouvelle_y]):
                    ennemi.y = nouvelle_y
        
        if ennemi.derniere_pos_joueur:
            dx = ennemi.derniere_pos_joueur[0] - ennemi.x
            dy = ennemi.derniere_pos_joueur[1] - ennemi.y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0.1:
                dx = dx / distance * ennemi.vitesse_actuelle
                dy = dy / distance * ennemi.vitesse_actuelle
                
                nouvelle_pos_x = ennemi.x + dx
                if deplacement_valide(jeu, [nouvelle_pos_x, ennemi.y]):
                    ennemi.x = nouvelle_pos_x
                
                nouvelle_pos_y = ennemi.y + dy
                if deplacement_valide(jeu, [ennemi.x, nouvelle_pos_y]):
                    ennemi.y = nouvelle_pos_y
            else:
                ennemi.derniere_pos_joueur = None
                ennemi.temps_memoire = 0
        
        if ennemi.temps_memoire > 0:
            ennemi.temps_memoire -= 1
            if ennemi.temps_memoire <= 0:
                ennemi.derniere_pos_joueur = None
        
        if ennemi.ralenti:
            if pygame.time.get_ticks() - ennemi.temps_ralenti > 2000:
                ennemi.ralenti = False
                ennemi.vitesse_actuelle = ennemi.vitesse_patrouille

    if not joueur_est_vu and est_en_poursuite:
        temps_perdu_vue += 1
        if temps_perdu_vue >= delai_arret_musique:
            est_en_poursuite = False
            if musique_poursuite:
                musique_poursuite.stop()
                pygame.mixer.music.unpause()

    if verifier_collision_ennemis(joueur_pos, liste_ennemis):
        return "game_over"
    
    return None

def verifier_collision_ennemis(joueur_pos, liste_ennemis):
    pos_x_int = int(joueur_pos[0])
    pos_y_int = int(joueur_pos[1])
    
    for ennemi in liste_ennemis:
        ennemi_x = int(ennemi.x)
        ennemi_y = int(ennemi.y)
        
        if (abs(pos_x_int - ennemi_x) < 1 and 
            abs(pos_y_int - ennemi_y) < 1):
            return True
    return False


def est_dans_cone(pos_joueur, pos_cible, angle_vue, longueur_cone):
    dx = pos_cible[0] - pos_joueur[0]
    dy = pos_cible[1] - pos_joueur[1]
    
    distance = math.sqrt(dx*dx + dy*dy)
    if distance > longueur_cone:
        return False
        
    angle_cible = (math.degrees(math.atan2(dy, dx)) + 360) % 360
    
    diff_angle = (angle_cible - angle_vue + 180) % 360 - 180
    
    return abs(diff_angle) <= 30

def est_visible(joueur_pos, case_pos, jeu):
    """Vérifie si une case est visible (dans le cône ou le cercle proche, et pas de mur entre)"""
    joueur_x, joueur_y = joueur_pos
    case_x, case_y = case_pos

    dx = case_x - joueur_x
    dy = case_y - joueur_y
    distance = math.sqrt(dx*dx + dy*dy)

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

    hauteur = len(jeu)
    largeur = len(jeu[0]) if hauteur > 0 else 0
    
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
            
            if not (0 <= x < largeur and 0 <= y < hauteur):
                return True
            if jeu[y][x] == "#":
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
            
            if not (0 <= x < largeur and 0 <= y < hauteur):
                return True
            if jeu[y][x] == "#":
                return True

    return False


def afficher_menu_pause():
    pygame.mouse.set_visible(True)
    global resolution_index, largeur, hauteur, fenetre

    fond = pygame.image.load("./texture/background_1.png")
    fond = pygame.transform.scale(fond, (largeur, hauteur))

    while True:
        fenetre.blit(fond, (0, 0))

        titre = pygame.font.Font("November.ttf", 100).render("Echoes of the Hollow", True, blanc)
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
            dessiner_bouton(fenetre, bouton, texte, pygame.font.Font(font_helpme, taille_texte), '#6428a0', '#301934', blanc)

        pygame.display.flip()

        for event in pygame.event.get():
            result = gerer_evenement(event, boutons)
            if result in ["continuer", "recommencer", "menu"]:
                return result
            if result == "escape":
                return


def trouver_case_disponible():
    """Trouve la première case vide dans l'inventaire"""
    for i in range(len(inventaire)):
        if inventaire[i] is None:
            return i
    return -1

def utiliser_objet_selectionne():
    """Utilise l'objet dans la case sélectionnée"""
    global sprays_collectes, bouteilles_collectees
    
    if index_case_selectionnee < len(inventaire):
        objet = inventaire[index_case_selectionnee]
        if objet == "spray" and sprays_collectes > 0:
            utiliser_spray(joueur_pos, angle_de_vue, liste_ennemis, jeu)
            sprays_collectes -= 1
            if sprays_collectes == 0:
                inventaire[index_case_selectionnee] = None
        elif objet == "bouteille" and bouteilles_collectees > 0:
            utiliser_bouteille(joueur_pos, angle_de_vue)
            bouteilles_collectees -= 1
            if bouteilles_collectees == 0:
                inventaire[index_case_selectionnee] = None

def dessiner_cone_spray(surface, position, angle, longueur):
    masque = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
    
    x, y = position
    angle_spray = 30
    start_angle = math.radians(angle - angle_spray / 2)
    end_angle = math.radians(angle + angle_spray / 2)

    points = [(x, y)]

    steps = 180
    for i in range(steps + 1):
        theta = start_angle + i * (end_angle - start_angle) / steps
        ray_x = x + longueur * math.cos(theta)
        ray_y = y + longueur * math.sin(theta)
        points.append((ray_x, ray_y))

    if len(points) > 2:
        pygame.draw.polygon(masque, marron_spray, points)

    surface.blit(masque, (0, 0))

def utiliser_spray(joueur_pos, angle_de_vue, liste_ennemis, jeu):
    global sprays_collectes, spray_actif, temps_spray
    if sprays_collectes <= 0:
        return
    
    spray_actif = True
    temps_spray = pygame.time.get_ticks()
    
    portee_spray = 5 * taille_case
    
    for ennemi in liste_ennemis:
        if est_dans_cone(joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, portee_spray):
            if not a_mur_entre(joueur_pos, (ennemi.x, ennemi.y), jeu):
                ennemi.ralenti = True
                ennemi.temps_ralenti = pygame.time.get_ticks()
                ennemi.vitesse_actuelle = 0.1
    
    sprays_collectes -= 1

def dessiner_bouteilles(surface, camera_offset):
    for bouteille in bouteilles_lancees:
        pos_x = int(bouteille.x * taille_case - camera_offset[0])
        pos_y = int(bouteille.y * taille_case - camera_offset[1])
        
        if not bouteille.brisee:
            taille_bouteille = taille_case // 2
            
            surface_bouteille = pygame.Surface((taille_bouteille, taille_bouteille), pygame.SRCALPHA)
            
            couleur_bouteille = pygame.Color(bouteille_verre)
            
            pygame.draw.rect(surface_bouteille, couleur_bouteille, 
                           (taille_bouteille//4, 0, 
                            taille_bouteille//2, taille_bouteille))
            
            angle_rotation = -math.degrees(math.atan2(bouteille.dy, bouteille.dx))
            surface_bouteille_rotated = pygame.transform.rotate(surface_bouteille, angle_rotation)
            rect_rotated = surface_bouteille_rotated.get_rect(center=(pos_x, pos_y))
            
            surface.blit(surface_bouteille_rotated, rect_rotated)
            
            for i in range(3):
                alpha = 150 - i * 50
                pos_trainee_x = int(pos_x - bouteille.dx * taille_case * i)
                pos_trainee_y = int(pos_y - bouteille.dy * taille_case * i)
                surface_trainee = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(surface_trainee, (*couleur_bouteille[:3], alpha), (2, 2), 2)
                surface.blit(surface_trainee, (pos_trainee_x - 2, pos_trainee_y - 2))
        else:
            for i in range(8):
                angle = random.uniform(0, 360)
                distance = random.uniform(0, taille_case/2)
                eclat_x = pos_x + math.cos(math.radians(angle)) * distance
                eclat_y = pos_y + math.sin(math.radians(angle)) * distance
                taille_eclat = random.randint(1, 3)
                pygame.draw.circle(surface, (200, 200, 200, 150), 
                                 (int(eclat_x), int(eclat_y)), taille_eclat)

def utiliser_bouteille(pos_joueur, angle):
    global bouteilles_collectees, bouteilles_lancees
    if bouteilles_collectees > 0:
        pos_souris = pygame.mouse.get_pos()
        
        joueur_ecran_x = pos_joueur[0] * taille_case - camera_offset[0]
        joueur_ecran_y = pos_joueur[1] * taille_case - camera_offset[1]
        
        dx = pos_souris[0] - joueur_ecran_x
        dy = pos_souris[1] - joueur_ecran_y
        angle_reel = math.degrees(math.atan2(-dy, dx))
        
        bouteilles_collectees -= 1
        nouvelle_bouteille = BouteilleLancee(pos_joueur[0], pos_joueur[1], angle_reel)
        bouteilles_lancees.append(nouvelle_bouteille)

def mettre_a_jour_bouteilles(jeu, liste_ennemis):
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
                
                if (0 <= pos_grille_y < len(jeu) and 
                    0 <= pos_grille_x < len(jeu[0])):
                    if jeu[pos_grille_y][pos_grille_x] == "#":
                        bouteille.brisee = True
                        bouteille.position_brisure = [bouteille.x, bouteille.y]
                        bouteille.temps_brisure = vitesse_distraction
                        
                        for ennemi in liste_ennemis:
                            distance = distance_entre_points([ennemi.x, ennemi.y], bouteille.position_brisure)
                            if distance < 8:
                                ennemi.distrait = True
                                ennemi.derniere_pos_joueur = bouteille.position_brisure
                                ennemi.temps_distraction = vitesse_distraction
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


def distance_entre_points(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def verifier_victoire(joueur_pos, jeu, cles_collectees, nombre_cles):
    if cles_collectees >= nombre_cles:
        x, y = int(joueur_pos[0]), int(joueur_pos[1])
        if jeu[y][x] == "S":
            return True
    return False

def afficher_victoire():
    fenetre.fill(violet_fonce)
    font = pygame.font.Font(None, 74)
    
    texte = font.render("Félicitations ! Jeu terminé !", True, blanc)
    text_rect = texte.get_rect(center=(largeur//2, hauteur//2))
    fenetre.blit(texte, text_rect)
    pygame.display.flip()
    pygame.time.delay(3000)

def game_over():
    global running, cles_collectees, sprays_collectes, bouteilles_collectees, endurance_actuelle
    
    arreter_musiques()
    
    fenetre.fill(violet_fonce)
    font = pygame.font.Font(None, 74)
    texte = font.render("Game Over", True, (255, 0, 0))
    texte_rect = texte.get_rect(center=(largeur//2, hauteur//2))
    fenetre.blit(texte, texte_rect)
    pygame.display.flip()
    
    pygame.time.wait(2000)
    
    cles_collectees = 0
    sprays_collectes = 0
    bouteilles_collectees = 0
    endurance_actuelle = endurance_max
    
    jeu = generer_jeu(nombre_lignes, nombre_colonnes)
    cles = placer_cles(jeu, nombre_cles)
    placer_sprays(jeu, nombre_sprays)
    placer_bouteilles(jeu, nombre_bouteilles)
    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
    liste_ennemis = initialiser_ennemis(jeu, nombre_ennemis)
    
    pygame.mouse.set_visible(True)
    afficher_menu()
    pygame.mouse.set_visible(False)
    musique_fond()
    
    return "menu"


def musique_menu():
    pygame.mixer.music.load("./OST/menu_musique.mp3")
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)

def musique_fond():
    pygame.mixer.music.load("./OST/Amnesia_02.mp3")
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)

def demarrer_musique_ambiance():
    try:
        pygame.mixer.music.load("./OST/Amnesia_02.mp3")
        pygame.mixer.music.play(-1)
    except:
        print("Erreur lors du chargement de la musique d'ambiance")

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


jeu = generer_jeu(nombre_lignes, nombre_colonnes)
cles = placer_cles(jeu, nombre_cles)
placer_sprays(jeu, nombre_sprays)
placer_bouteilles(jeu, nombre_bouteilles)
liste_ennemis = initialiser_ennemis(jeu, nombre_ennemis)
charger_parametres()
pygame.mixer.music.set_volume(volume)
afficher_menu()
pygame.mouse.set_visible(False)
musique_fond()
demarrer_musique_ambiance()
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
                    placer_sprays(jeu, nombre_sprays)
                    placer_bouteilles(jeu, nombre_bouteilles)
                    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
                    liste_ennemis = initialiser_ennemis(jeu, nombre_ennemis)
                    cles_collectees = 0
                    sprays_collectes = 0
                    bouteilles_collectees = 0
                    endurance_actuelle = endurance_max
                    arreter_musiques()
                    musique_fond()
                elif choix == "menu":
                    jeu = generer_jeu(nombre_lignes, nombre_colonnes)
                    cles = placer_cles(jeu, nombre_cles)
                    placer_sprays(jeu, nombre_sprays)
                    placer_bouteilles(jeu, nombre_bouteilles)
                    joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
                    liste_ennemis = initialiser_ennemis(jeu, nombre_ennemis)
                    cles_collectees = 0
                    sprays_collectes = 0
                    bouteilles_collectees = 0
                    endurance_actuelle = endurance_max
                    afficher_menu()
                    arreter_musiques()
                    musique_fond()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                index_case_selectionnee = max(0, index_case_selectionnee - 1)
            elif event.button == 5:
                index_case_selectionnee = min(4, index_case_selectionnee + 1)
            elif event.button == 1:
                utiliser_objet_selectionne()
        if event.type == pygame.VIDEORESIZE and not plein_ecran:
            largeur, hauteur = event.size
            fenetre = pygame.display.set_mode((largeur, hauteur), pygame.RESIZABLE)
            jeu = redimensionner_jeu(largeur, hauteur)
            joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
            liste_ennemis = initialiser_ennemis(jeu, nombre_ennemis)

    souris_x, souris_y = pygame.mouse.get_pos()
    
    joueur_ecran_x = joueur_pos[0] * taille_case - camera_offset[0]
    joueur_ecran_y = joueur_pos[1] * taille_case - camera_offset[1]
    
    dx = souris_x - joueur_ecran_x
    dy = souris_y - joueur_ecran_y
    angle_de_vue = (math.degrees(math.atan2(dy, dx)) + 360) % 360

    for ennemi in liste_ennemis:
        if ennemi.peut_voir_joueur(joueur_pos, jeu):
            if not est_dans_cone(joueur_pos, (ennemi.x, ennemi.y), angle_de_vue, cone_longueur):
                ennemi.derniere_pos_joueur = joueur_pos[:]
                ennemi.temps_memoire = ennemi.duree_memoire_max

    touches = pygame.key.get_pressed()
    nouvelle_pos_x = joueur_pos[0]
    nouvelle_pos_y = joueur_pos[1]
    
    est_en_sprint = (touches[pygame.K_LSHIFT] or touches[pygame.K_RSHIFT]) and endurance_actuelle > 0
    
    if est_en_sprint and (touches[pygame.K_z] or touches[pygame.K_s] or touches[pygame.K_q] or touches[pygame.K_d] or 
                         touches[pygame.K_UP] or touches[pygame.K_DOWN] or touches[pygame.K_LEFT] or touches[pygame.K_RIGHT]):
        vitesse = vitesse_sprint
        endurance_actuelle = max(0, endurance_actuelle - taux_diminution)
    else:
        vitesse = vitesse_base
        if endurance_actuelle < endurance_max:
            endurance_actuelle = min(endurance_max, endurance_actuelle + taux_recuperation)
    
    dx = 0
    dy = 0
    
    if touches[controles["Haut"]]:
        dy -= vitesse
    if touches[controles["Bas"]]:
        dy += vitesse
    if touches[controles["Gauche"]]:
        dx -= vitesse
    if touches[controles["Droite"]]:
        dx += vitesse
        
    if dx != 0 and dy != 0:
        dx *= 0.707
        dy *= 0.707
    
    if deplacement_valide(jeu, [nouvelle_pos_x + dx, nouvelle_pos_y]):
        nouvelle_pos_x += dx
    
    if deplacement_valide(jeu, [nouvelle_pos_x, nouvelle_pos_y + dy]):
        nouvelle_pos_y += dy
    
    joueur_pos[0] = nouvelle_pos_x
    joueur_pos[1] = nouvelle_pos_y
    
    pos_x_int = int(joueur_pos[0])
    pos_y_int = int(joueur_pos[1])
    
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            check_x = pos_x_int + dx
            check_y = pos_y_int + dy
            
            if 0 <= check_y < len(jeu) and 0 <= check_x < len(jeu[0]):
                case = jeu[check_y][check_x]
                if case == "C":
                    cles_collectees += 1
                    jeu[check_y][check_x] = " "
                elif case == "P":
                    if ajouter_objet("spray"):
                        sprays_collectes += 1
                        jeu[check_y][check_x] = " "
                elif case == "V":
                    if ajouter_objet("bouteille"):
                        bouteilles_collectees += 1
                        jeu[check_y][check_x] = " "

    camera_cible_x = joueur_pos[0] * taille_case - largeur // 2
    camera_cible_y = joueur_pos[1] * taille_case - hauteur // 2
    
    facteur_lissage = 0.1
    camera_offset[0] += (camera_cible_x - camera_offset[0]) * facteur_lissage
    camera_offset[1] += (camera_cible_y - camera_offset[1]) * facteur_lissage

    camera_offset[0] = max(0, min(camera_offset[0], len(jeu[0]) * taille_case - largeur))
    camera_offset[1] = max(0, min(camera_offset[1], len(jeu) * taille_case - hauteur))

    dessiner_jeu(jeu, joueur_pos, camera_offset)

    dessiner_inventaire(fenetre)

    dessiner_barre_endurance(fenetre)

    afficher_fps(fenetre, horloge)

    resultat = deplacer_ennemis(jeu, liste_ennemis, joueur_pos)
    if resultat == "game_over":
        etat_jeu = game_over()
        if etat_jeu == "menu":
            jeu = generer_jeu(nombre_lignes, nombre_colonnes)
            joueur_pos = [nombre_colonnes // 2, nombre_lignes // 2]
            cles_collectees = 0
            liste_ennemis = initialiser_ennemis(jeu, nombre_ennemis)
            continue

    dessiner_compteur_cles(fenetre, cles_collectees, nombre_cles)

    if spray_actif:
        temps_actuel = pygame.time.get_ticks()
        if temps_actuel - temps_spray < duree_affichage_spray:
            joueur_ecran_x = joueur_pos[0] * taille_case - camera_offset[0] + taille_case // 2
            joueur_ecran_y = joueur_pos[1] * taille_case - camera_offset[1] + taille_case // 2
            dessiner_cone_spray(fenetre, (joueur_ecran_x, joueur_ecran_y), angle_de_vue, 5 * taille_case)
        else:
            spray_actif = False

    mettre_a_jour_bouteilles(jeu, liste_ennemis)
    dessiner_bouteilles(fenetre, camera_offset)

    if verifier_victoire(joueur_pos, jeu, cles_collectees, nombre_cles):
        afficher_victoire()
        running = False

    pygame.display.flip()
    horloge.tick(60)

pygame.quit()