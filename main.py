import copy
import pygame
from pygame import Cursor, mixer
import math
import config
import mapparser 
import os

pygame.init()
pygame.font.init()
pygame.mixer.init()

size = (1200, 900)
screen = pygame.display.set_mode(size)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

couriernewBig = pygame.font.SysFont('couriernew', 38)
couriernewBigBold = pygame.font.SysFont('couriernew', 38, bold=True)
couriernewSmall = pygame.font.SysFont('couriernew', 25)
couriernewScore = pygame.font.SysFont('couriernew', 60)

pygame.display.set_caption("JATVSRG")
 
# padding for score
def padding(score, max):
    ret = str(math.floor(score))
    ret = "0" * (max - len(ret)) + ret
    return ret

# main loop
def main():
    maps = []
    loadedMap = []
    loadedObjects = []
    selectedMapIndex = 0
    volume = 0.3
    keysDown = [False, False, False, False]
    keysPressed = [False, False, False, False]
    keysReleased = [False, False, False, False]
    isPlaying = False
    playingFrame = 0
    curScore = 0.0
    scoreMultiiplier = 0.0
    pygame.mixer.music.set_volume(volume)
    results = False

    # per play
    hitCount = {
        'perfect': 0,
        'good': 0,
        'bad': 0,
        'miss': 0
    }
    
    # variable to represent the most recent hit, and when it occured
    hit = ""
    hitMarker = 0

    # list of all maps
    for dir in os.listdir('maps/'):
        if os.path.isdir(os.path.join('maps/', dir)):
            maps.append(dir)
    
    pygame.mixer.music.load(f"maps/{maps[selectedMapIndex]}/audio.mp3")
    pygame.mixer.music.play()
    while True:
        screen.fill(BLACK)
        
        # reset keyspressed
        for i in range(len(keysPressed)):
            keysPressed[i] = False
            keysReleased[i] = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN and not isPlaying:
                    selectedMapIndex += 1

                    if selectedMapIndex == -1:
                        selectedMapIndex = len(maps) - 1
                    elif selectedMapIndex == len(maps):
                        selectedMapIndex = 0
                    pygame.mixer.music.load(f"maps/{maps[selectedMapIndex]}/audio.mp3")
                    pygame.mixer.music.play()
                elif event.key == pygame.K_UP and not isPlaying:
                    selectedMapIndex -= 1
                    
                    if selectedMapIndex == -1:
                        selectedMapIndex = len(maps) - 1
                    elif selectedMapIndex == len(maps):
                        selectedMapIndex = 0
                    pygame.mixer.music.load(f"maps/{maps[selectedMapIndex]}/audio.mp3")
                    pygame.mixer.music.play()
                elif event.key == pygame.K_RETURN and not isPlaying:
                    pygame.mixer.music.load(f"maps/{maps[selectedMapIndex]}/audio.mp3")
                    pygame.mixer.music.play()
                    pygame.mixer.music.pause()
                    
                    loadedMap = mapparser.parseMap(maps[selectedMapIndex])
                    curScore = 0.0
                    results = False
                    hitCount = dict.fromkeys(hitCount, 0)
                    for i in range(20):
                        loadedObjects.append(loadedMap.pop(0))
                    isPlaying = True
                    playingFrame = pygame.time.get_ticks()
                    scoreMultiiplier = 1000000 / (len(loadedMap) + 20)
                else:
                    for i in config.keybinds:
                        if event.key == eval(f"pygame.K_{config.keybinds[i]}"):
                            keysDown[i] = True
                            keysPressed[i] = True
                
            elif event.type == pygame.KEYUP:
                for i in config.keybinds:
                    if event.key == eval(f"pygame.K_{config.keybinds[i]}"):
                        keysDown[i] = False
                        keysReleased[i] = True
        for i in range(len(maps)):
            if i == selectedMapIndex:
                map = maps[i]
                pygame.draw.rect(screen, WHITE, pygame.Rect(27, 63 + i * 25, 256, 29))
                screen.blit(couriernewSmall.render(map, False, BLACK), (30, 65 + i * 25))
                continue
            map = maps[i]
            screen.blit(couriernewSmall.render(map, False, WHITE), (30, 65 + i * 25))

        for i in range(len(keysDown)):
            if keysDown[i]:
                pygame.draw.circle(screen, config.colors[i], (390 + i * 140, 800), 60) 

        if isPlaying and playingFrame + 1000 < pygame.time.get_ticks():
            # map complete
            if len(loadedObjects) == 0:
                print(hitCount)
                results = True
                isPlaying = False
            
            # deep copy the array of loaded objects
            unloadedObjects = copy.deepcopy(loadedObjects)

            # to store all loaded objects per lane
            loadedLaneObjects = [[], [], [], []]
            for obj in loadedObjects:
                for i in range(len(keysPressed)):
                    if keysPressed[i] or keysReleased[i]:
                        if obj[1] == i:
                            if obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame) < 500:
                                loadedLaneObjects[i].append(obj)
                                break;

                if len(obj) == 5:
                    if not obj[3]:
                        pygame.draw.circle(screen, config.colors[obj[1]], (390 + obj[1] * 140, 800 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config.ar), 60 )
                    pygame.draw.circle(screen, config.colors[obj[1]], (390 + obj[1] * 140, 800 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config.ar), 60 )
                    rect1 = 330 + obj[1] * 140
                    rect2 = 800 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config.ar
                    rect3 = 120
                    if not obj[3]:
                        rect4 = (800 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config.ar) - rect2
                    else:
                        rect4 = (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config.ar
                    pygame.draw.rect(screen, config.colors[obj[1]], pygame.Rect(rect1, rect2, rect3, rect4))
                    
                    if 800 - (obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config.ar > 960:
                        hit = "miss"
                        hitMarker = pygame.time.get_ticks()
                        hitCount[hit] += 1
                        # alter the copied array so index doesn't get mixed up
                        unloadedObjects.remove(obj)
                        if len(loadedMap) != 0:
                            unloadedObjects.append(loadedMap.pop(0))
                else:
                    pygame.draw.circle(screen, config.colors[obj[1]], (390 + obj[1] * 140, 800 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config.ar), 60 )

                    # if the circle passes the visible point
                    if 800 - (obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame)) * config.ar > 960:
                        hit = "miss"
                        hitMarker = pygame.time.get_ticks()
                        hitCount[hit] += 1
                        # alter the copied array so index doesn't get mixed up
                        unloadedObjects.remove(obj)
                        if len(loadedMap) != 0:
                            unloadedObjects.append(loadedMap.pop(0))

            # click handling
            print(loadedLaneObjects)
            for i in range(len(keysPressed)):
                if keysPressed[i]:
                    if len(loadedLaneObjects[i]) != 0:
                        obj = loadedLaneObjects[i][0]
                        
                        if len(obj) == 5:
                            unObj = unloadedObjects[unloadedObjects.index(loadedLaneObjects[i][0])]
                            unObj[3] = True
                            # evaluate score for hit
                            unObj[4] = abs(obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame))
                        else:
                            # evaluate score for hit
                            hitMarker = pygame.time.get_ticks()
                            hitDifference = abs(obj[0] - (pygame.time.get_ticks() - 2000 - playingFrame))
                            if hitDifference > config.hitwindow[0]:
                                hit = "miss"
                            elif hitDifference > config.hitwindow[1]:
                                curScore += scoreMultiiplier * 0.3
                                hit = "bad"
                            elif hitDifference > config.hitwindow[2]:
                                curScore += scoreMultiiplier * 0.5
                                hit = "good"
                            else:
                                curScore += scoreMultiiplier * 1
                                hit = "perfect"
                            hitCount[hit] += 1

                            if obj in unloadedObjects:
                                unloadedObjects.remove(obj)
                                if len(loadedMap) != 0:
                                    unloadedObjects.append(loadedMap.pop(0))
            
            # release handling
            for i in range(len(keysReleased)):
                if keysReleased[i]:
                    print(loadedLaneObjects)
                    if len(loadedLaneObjects[i]) != 0:
                        obj = loadedLaneObjects[i][0]

                        if len(obj) == 5 and obj[3]:
                            # evaluate score for hit
                            hitMarker = pygame.time.get_ticks()
                            # actual hitscore is based on the worst of the 2 values
                            print(obj[4])
                            print(abs(obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)))
                            hitDifference = max(obj[4], abs(obj[2] - (pygame.time.get_ticks() - 2000 - playingFrame)))
                            print(hitDifference)
                            if hitDifference > config.hitwindow[0]:
                                hit = "miss"
                            elif hitDifference > config.hitwindow[1]:
                                curScore += scoreMultiiplier * 0.3
                                hit = "bad"
                            elif hitDifference > config.hitwindow[2]:
                                curScore += scoreMultiiplier * 0.5
                                hit = "good"
                            else:
                                curScore += scoreMultiiplier * 1
                                hit = "perfect"
                            hitCount[hit] += 1

                            if obj in unloadedObjects:
                                unloadedObjects.remove(obj)
                                if len(loadedMap) != 0:
                                    unloadedObjects.append(loadedMap.pop(0))

            
            # display most recent hit score
            if hit != "":
                # center the text
                hitWidth = 0.39*35*len(hit)
                # fading effect
                hitColor = copy.deepcopy(config.hitColors[hit])
                for i in range(len(hitColor)):
                    hitColor[i] = max(min(hitColor[i] * (1 - ((pygame.time.get_ticks() - hitMarker) / config.hitFadeTime)), 255), 0)
                screen.blit(couriernewBigBold.render(hit, True, hitColor), (580 - hitWidth / 2, 640))

            # set the old array to the altered array
            loadedObjects = unloadedObjects

        if isPlaying and playingFrame + 2000 < pygame.time.get_ticks():
            pygame.mixer.music.unpause()

        # results screen
        if results:
            screen.blit(couriernewBigBold.render("Perfect: ", True, config.hitColors['perfect']), (425, 200))
            screen.blit(couriernewBigBold.render("Good: ", True, config.hitColors['good']), (425, 300))
            screen.blit(couriernewBigBold.render("Bad: ", True, config.hitColors['bad']), (425, 400))
            screen.blit(couriernewBigBold.render("Miss: ", True, config.hitColors['miss']), (425, 500))
            screen.blit(couriernewBig.render(f"{padding(hitCount['perfect'], 4)}", True, (255, 255, 255)), (650, 200))
            screen.blit(couriernewBig.render(f"{padding(hitCount['good'], 4)}", True, (255, 255, 255)), (650, 300))
            screen.blit(couriernewBig.render(f"{padding(hitCount['bad'], 4)}", True, (255, 255, 255)), (650, 400))
            screen.blit(couriernewBig.render(f"{padding(hitCount['miss'], 4)}", True, (255, 255, 255)), (650, 500))

        # maps list
        pygame.draw.rect(screen, WHITE, pygame.Rect(20, 20, 270, 860),  5)
        screen.blit(couriernewBig.render('Maps', True, WHITE),(30, 25))

        # leaderboard
        pygame.draw.rect(screen, WHITE, pygame.Rect(910, 20, 270, 710), 5)
        screen.blit(couriernewBig.render('Leaderboard', True, WHITE),(920, 25))

        # score
        pygame.draw.rect(screen, WHITE, pygame.Rect(910, 750, 270, 130), 5)
        screen.blit(couriernewBig.render('Score', True, WHITE), (920, 755))
        screen.blit(couriernewScore.render(padding(curScore, 7), True, WHITE), (920, 800))

        # main play area
        pygame.draw.rect(screen, WHITE, pygame.Rect(310, -200, 580, 1500), 5)
        for i in range(4):    
            pygame.draw.circle(screen, WHITE, (390 + i * 140, 800), 60, 5) 

        # --- Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
    
        # --- Limit to 60 frames per second
        pygame.time.Clock().tick(144)

if __name__ == "__main__":
    main()