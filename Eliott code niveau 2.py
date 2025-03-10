import pygame
import random

# Constantes
LARGEUR = 1500 * 3+1
HAUTEUR = 900 * 3+1
TAILLE_CASE = 50

# Paramètres
DENSITE_BUISSONS = 0.03
REDUCTION_VISION_BUISSON = 1
VITESSE_NORMALE = 1
VITESSE_BUISSON = 2

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
JOUEUR = (41, 27, 14)
SORTIE = (0, 255, 0)
HERBE = (34, 139, 34)
BUISSON = (0, 100, 0)
CLE = (255, 223, 0)
ENNEMIES = (255, 0, 0)
ARBRE = (255, 105, 180)
BARRIERE = (139, 69, 19)

COULEURS = {
    "X": BARRIERE,
    "B": BUISSON,
    "A": ARBRE,
    "S": SORTIE,
    "J": JOUEUR,
    " ": HERBE,
}

class Jardin:
    def __init__(self):
        self.nb_lignes = HAUTEUR // TAILLE_CASE
        self.nb_colonnes = LARGEUR // TAILLE_CASE
        self.joueur_pos = self.placer_joueur_bord()
        self.grille = self.generer_jardin()
        self.camera_offset = [0, 0]
        self.preparer_textures()

    def generer_jardin(self):
        grille = [[" " for _ in range(self.nb_colonnes)] for _ in range(self.nb_lignes)]

        for i in range(self.nb_lignes):
            grille[i][0] = grille[i][-1] = "X"
        for j in range(self.nb_colonnes):
            grille[0][j] = grille[-1][j] = "X"

        for _ in range(int(self.nb_lignes * self.nb_colonnes * DENSITE_BUISSONS)):
            x, y = random.randint(1, self.nb_colonnes - 3), random.randint(1, self.nb_lignes - 3)
            if grille[y][x] == " ":
                for dy in range(2):
                    for dx in range(2):
                        grille[y + dy][x + dx] = "B"

        for _ in range(random.randint(20, 60)):
            x, y = random.randint(1, self.nb_colonnes - 2), random.randint(1, self.nb_lignes - 2)
            if grille[y][x] == " ":
                grille[y][x] = "A"
                if random.random() < 0.5 and y + 1 < self.nb_lignes - 1 and x + 1 < self.nb_colonnes - 1:
                    grille[y + 1][x] = "A"
                    grille[y][x + 1] = "A"
                    grille[y + 1][x + 1] = "A"

        self.placer_sortie(grille)
        return grille

    def placer_joueur_bord(self):
        bord = random.randint(0, 3)
        return [
            random.randint(1, self.nb_colonnes - 2) if bord % 2 == 0 else (self.nb_colonnes - 2 if bord == 1 else 1),
            random.randint(1, self.nb_lignes - 2) if bord % 2 == 1 else (self.nb_lignes - 2 if bord == 2 else 1),
        ]

    def placer_sortie(self, grille):
        bord = random.choice(["haut", "bas", "gauche", "droite"])
        x, y = (random.randint(1, self.nb_colonnes - 2), 0 if bord == "haut" else self.nb_lignes - 1) if bord in ["haut", "bas"] else (0 if bord == "gauche" else self.nb_colonnes - 1, random.randint(1, self.nb_lignes - 2))
        grille[y][x] = "S"
        if bord in ["haut", "bas"]:
            grille[y][x - 1] = grille[y][x + 1] = "X"
        else:
            grille[y - 1][x] = grille[y + 1][x] = "X"

    def est_dans_buisson(self):
        x, y = self.joueur_pos
        return self.grille[y][x] == "B"

    def preparer_textures(self):
        self.textures = {cle: pygame.Surface((TAILLE_CASE, TAILLE_CASE)) for cle in COULEURS}
        for cle, couleur in COULEURS.items():
            self.textures[cle].fill(couleur)

    def dessiner(self, fenetre):
        fenetre.fill(NOIR)

        debut_x, debut_y = self.camera_offset[0] // TAILLE_CASE, self.camera_offset[1] // TAILLE_CASE
        fin_x, fin_y = debut_x + 30, debut_y + 18

        for i in range(debut_y, min(fin_y, self.nb_lignes)):
            for j in range(debut_x, min(fin_x, self.nb_colonnes)):
                x, y = j * TAILLE_CASE - self.camera_offset[0], i * TAILLE_CASE - self.camera_offset[1]
                fenetre.blit(self.textures[self.grille[i][j]], (x, y))

        if self.est_dans_buisson():
            masque = pygame.Surface((1500, 900), pygame.SRCALPHA)
            masque.fill((0, 0, 0, int(255 * REDUCTION_VISION_BUISSON)))
            fenetre.blit(masque, (0, 0))

        joueur_x, joueur_y = self.joueur_pos[0] * TAILLE_CASE - self.camera_offset[0], self.joueur_pos[1] * TAILLE_CASE - self.camera_offset[1]
        pygame.draw.rect(fenetre, COULEURS["J"], (joueur_x, joueur_y, TAILLE_CASE, TAILLE_CASE))

def afficher_victoire():
    debut = pygame.time.get_ticks()
    while pygame.time.get_ticks() - debut < 30000:  # 30 secondes
        fenetre.fill(NOIR)
        texte = pygame.font.Font(None, 60).render("Victoire !", True, BLANC)
        texte_rect = texte.get_rect(center=(1500 // 2, 900 // 2))
        fenetre.blit(texte, texte_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

if __name__ == "__main__":
    pygame.init()
    fenetre = pygame.display.set_mode((1500, 900))
    pygame.display.set_caption("Jardin")
    horloge = pygame.time.Clock()

    jardin = Jardin()
    vitesse = VITESSE_NORMALE

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        vitesse = VITESSE_BUISSON if jardin.est_dans_buisson() else VITESSE_NORMALE
        touches = pygame.key.get_pressed()
        dx, dy = 0, 0

        if touches[pygame.K_z] or touches[pygame.K_UP]:
            dy = -1
        if touches[pygame.K_s] or touches[pygame.K_DOWN]:
            dy = 1
        if touches[pygame.K_q] or touches[pygame.K_LEFT]:
            dx = -1
        if touches[pygame.K_d] or touches[pygame.K_RIGHT]:
            dx = 1

        nouvelle_pos = [jardin.joueur_pos[0] + dx, jardin.joueur_pos[1] + dy]
        if jardin.grille[nouvelle_pos[1]][nouvelle_pos[0]] not in ["X", "A"]:
            jardin.joueur_pos = nouvelle_pos

        jardin.camera_offset = [
            max(0, min(jardin.joueur_pos[0] * TAILLE_CASE - 750, LARGEUR - 1500)),
            max(0, min(jardin.joueur_pos[1] * TAILLE_CASE - 450, HAUTEUR - 900)),
        ]

        if jardin.grille[nouvelle_pos[1]][nouvelle_pos[0]] == "S":
            afficher_victoire()
            pygame.time.delay(30000)  # Attendre 30 secondes
            running = False  # Quitter le jeu après la victoire

        
        jardin.dessiner(fenetre)
        pygame.display.flip()
        horloge.tick(60)

    pygame.quit()
