import pygame
import random
import sys

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("리듬게임")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 24)

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 게임 변수
lines = [100, 200, 300, 400]
note_speed = 4
score = 0
combo = 0
miss_count = 0
judgement_text = ""
notes = []

# 스킬 카드 변수
skill_ready = False
skill_active = False
skill_timer = 0

# 시간 기반 속도 증가 변수
start_time = pygame.time.get_ticks()
speed_increase_interval = 10000  # 10초마다
max_speed = 10

key_mapping = {
    pygame.K_d: 0,
    pygame.K_f: 1,
    pygame.K_j: 2,
    pygame.K_k: 3,
}

# 블럭 클래스
class Note:
    def __init__(self, line):
        self.line = line
        self.x = lines[line]
        self.y = -50

    def update(self):
        self.y += note_speed

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 50, 20))

# 블럭 생성 이벤트
NEW_NOTE = pygame.USEREVENT + 1
pygame.time.set_timer(NEW_NOTE, 700)

# 판정 함수
def get_judgement(note_y):
    if 590 <= note_y <= 610:
        return "Perfect", 300
    elif 570 <= note_y <= 630:
        return "Good", 100
    else:
        return "Miss", 0

# 텍스트 출력 함수
def draw_text(text, x, y):
    img = FONT.render(text, True, WHITE)
    screen.blit(img, (x, y))

# 판정선
def draw_judgeline():
    for x in lines:
        pygame.draw.rect(screen, (100, 100, 100), (x, 600, 50, 10))

# 게임 루프
running = True
while running:
    screen.fill(BLACK)
    draw_judgeline()

    # 시간에 따른 블럭 속도 증가
    elapsed_time = pygame.time.get_ticks() - start_time
    if elapsed_time // speed_increase_interval > (note_speed - 4) and note_speed < max_speed and not skill_active:
        note_speed += 0.5

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == NEW_NOTE:
            new_note = Note(random.randint(0, 3))
            notes.append(new_note)

        if event.type == pygame.KEYDOWN:
            if event.key in key_mapping:
                line = key_mapping[event.key]
                hit = False
                for note in notes:
                    if note.line == line:
                        judgement, pts = get_judgement(note.y)
                        if judgement != "Miss":
                            score += pts
                            combo += 1
                            judgement_text = judgement
                            notes.remove(note)
                            hit = True
                            if combo % 10 == 0 and not skill_active:
                                skill_ready = True
                            break
                if not hit:
                    combo = 0
                    miss_count += 1
                    judgement_text = "Miss"
            elif event.key == pygame.K_SPACE and skill_ready:
                skill_active = True
                skill_ready = False
                skill_timer = pygame.time.get_ticks()
                note_speed /= 2  # 슬로우 모션

    # 블럭 업데이트 및 화면 출력
    for note in notes[:]:
        note.update()
        note.draw()
        if note.y > HEIGHT:
            notes.remove(note)
            combo = 0
            miss_count += 1
            judgement_text = "Miss"

    # 스킬 종료 타이머
    if skill_active and pygame.time.get_ticks() - skill_timer > 5000:
        skill_active = False
        note_speed *= 2  # 원래 속도로 복귀

    # 게임 오버 조건
    if miss_count >= 10:
        screen.fill(BLACK)
        draw_text("Game Over!", 180, 280)
        draw_text(f"Final Score: {score}", 170, 320)
        pygame.display.flip()
        pygame.time.delay(3000)
        running = False

    # UI 출력
    draw_text(f"Score: {score}", 10, 10)
    draw_text(f"Combo: {combo}", 10, 40)
    draw_text(f"Miss: {miss_count}/10", 10, 70)
    draw_text(f"{judgement_text}", 200, 550)
    if skill_ready:
        draw_text("Skill Ready! (Press SPACE)", 120, 100)
    elif skill_active:
        draw_text("Skill Active!", 160, 100)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
