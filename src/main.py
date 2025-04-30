import pygame
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("2D Platformer")

    game = Game()  # Убрали передачу screen, так как Game создает свой собственный

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.run()

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()