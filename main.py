import invaders
import pygame
from sys import exit

def main() -> None:

    folder = "assets"
    pygame.init()
    surface = pygame.display.set_mode((900, 700))
    pygame.display.set_caption("Covid invaders")
    pygame.display.set_icon(pygame.image.load(f"{folder}/icon.png"))

    fonts = {
        "small": invaders.font(f"{folder}/little_comet.otf", 2),
        "large": invaders.font(f"{folder}/little_comet.otf", 3),
        "unicode": invaders.font(f"{folder}/seguisym.ttf", 2)
    }

    # game reset
    invaders.Sprite.clear()

    # sprites
    invaders.Enemy.instantiate(folder)
    vaccine = invaders.Player(folder)
    vacc_hit_color = (250,204,13)
    vacc_hit = invaders.Projectile(vaccine.width, (vaccine.x, vaccine.y), vacc_hit_color)
    virus_hit_color = (255, 154, 0)
    virus_hit, attacker_x, attacker_y = invaders.Enemy.attack(virus_hit_color)

    score = 0
    variant_surfs = invaders.Enemy.types_surfs(["Omicron", "Delta", "Gamma", "Beta", "Alpha"], fonts["small"])
    total_score = sum(instance.pts for instance in invaders.Enemy.all)
    game = {"running": True, "start": False, "stop": False}

    # game loop
    while game["running"]:

        ground = invaders.enviornment((188,228,247), (140,196,59))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game["running"] = False

            change = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: change = -vaccine.dx
                if event.key == pygame.K_RIGHT: change = vaccine.dx
                if event.key == pygame.K_SPACE:
                    if game["start"]: vacc_hit.fire = True
                    if not game["start"]: game["start"] = True
                    if game["stop"]: main()
                if event.key == pygame.K_q and game["start"]:
                    if game["stop"]: game["running"] = False
                    if not game["stop"]: game["stop"] = True

            if event.type == pygame.KEYUP and (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT): change = 0

        # game stop
        if (all(not virus.visible for virus in invaders.Enemy.all)
        or virus_hit.collide(vaccine.img.get_rect(topleft = (vaccine.x, vaccine.y)))
        or vaccine.y - invaders.Enemy.all[-1].y <= invaders.Enemy.all[-1].height * 2 and invaders.Enemy.all[0].x == abs(invaders.Enemy.dx) * 4):
            game["stop"] = True

        vacc_hit.draw()
        vaccine.draw()

        if game["start"] and not game["stop"]:
            invaders.Enemy.move()
            vaccine.move(vaccine.x + change)
            vacc_hit.move(vaccine.x)
            if vacc_hit.y < -vacc_hit.length: vacc_hit.reset(vaccine.y)

            # continuous enemy projectile
            virus_hit.move(attacker_x)
            if virus_hit.collide(ground):
                virus_hit, attacker_x, attacker_y = invaders.Enemy.attack(virus_hit_color)
                virus_hit.reset(attacker_y, True)
                virus_hit.move(attacker_x)
            virus_hit.draw()

        for virus in invaders.Enemy.all:
            
            # virus collision with vacc_hit
            if virus.visible and vacc_hit.collide(virus.img.get_rect(topleft = (virus.x, virus.y)), True):
                virus.visible = False
                vacc_hit.reset(vaccine.y)
                score += virus.pts

            virus.draw()

        score_text = invaders.text(fonts["small"], f"Score: {score}")
        quit_text = invaders.text(fonts["small"], "Press Q to quit")
        
        if game["start"] and not game["stop"]:
            surface.blit(score_text, (invaders.em, invaders.em))
            surface.blit(quit_text, quit_text.get_rect(topright = (surface.get_width() - invaders.em, invaders.em)))
        
        elif game["stop"]:
            
            # game stop screen
            texts = [
                invaders.text(fonts["large"], "Game Over!"),
                score_text,
                invaders.text(fonts["small"], f"Maximum Score: {total_score}")
            ]

            # win or lose
            if score == total_score:
                texts.append(invaders.text(fonts["large"], "You have ended Covid!"))
                texts.append(invaders.emoji_text(invaders.text(fonts["small"], "Let's celebrate!"), invaders.text(fonts["unicode"], "🎉")))
            else:
                texts.append(invaders.text(fonts["large"], "Covid is still rampant!"))
                texts.append(invaders.emoji_text(invaders.text(fonts["small"], "Continue the fight, you can do it!"), invaders.text(fonts["unicode"], "👍")))

            texts.append(invaders.text(fonts["small"], "Press SPACE to replay"))
            texts.append(quit_text)

            invaders.text_screen(texts)
        
        else:

            # game start screen
            texts = [
                invaders.text(fonts["large"], "Welcome to Covid invaders!"),
                invaders.text(fonts["small"], "AIM: Eradicate all variants")
            ] + variant_surfs
            texts.append(invaders.text(fonts["small"], "Press SPACE to play"))

            invaders.text_screen(texts)
        
        pygame.display.update()
    
    pygame.quit()
    exit(0)


if __name__ == "__main__":
    main()
