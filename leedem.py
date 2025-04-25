import pygame
import random
import sys

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("리듬게임")
clock = pygame.time.Clock()
FONT = pygame.font.Font(pygame.font.match_font('NanumGothic'), 24)
BIG_FONT = pygame.font.Font(pygame.font.match_font('NanumGothic'), 36)

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
BLUE = (100, 200, 255)
TRANSPARENT_WHITE = (255, 255, 255, 100)

# 게임 변수
lines = [100, 200, 300, 400]
note_speed = 4
score = 0
combo = 0
miss_count = 0
judgement_text = ""
notes = []
game_active = False
current_mode = "노말"

# 스킬 변수
skill_ready = False
skill_active = False
skill_type = None
skill_timer = 0
score_multiplier = 1

# 시간 기반 속도 증가 변수
start_time = pygame.time.get_ticks()
speed_increase_interval = 10000
max_speed = 10

# 노트 생성 변수
note_interval = 700
NEW_NOTE = pygame.USEREVENT + 1

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
        self.transparent = skill_type == "투명화"

    def update(self):
        self.y += note_speed

    def draw(self):
        color = WHITE if not self.transparent else (255, 255, 255, 128)
        pygame.draw.rect(screen, color, (self.x, self.y, 50, 20))

# 판정 함수
def get_judgement(note_y):
    if 590 <= note_y <= 610:
        return "Perfect", 300
    elif 570 <= note_y <= 630:
        return "Good", 100
    else:
        return "Miss", 0

# 텍스트 출력 함수
def draw_text(text, x, y, color=WHITE, font=FONT):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def draw_button(text, x, y, w, h):
    pygame.draw.rect(screen, GRAY, (x, y, w, h), border_radius=10)
    draw_text(text, x + 20, y + 10)

# 판정선
def draw_judgeline():
    for x in lines:
        pygame.draw.rect(screen, GRAY, (x, 600, 50, 10))

def reset_game():
    global notes, score, combo, miss_count, judgement_text
    global skill_ready, skill_active, skill_type, note_speed, score_multiplier
    notes.clear()
    score = 0
    combo = 0
    miss_count = 0
    judgement_text = ""
    skill_ready = False
    skill_active = False
    skill_type = None
    score_multiplier = 1
    if current_mode == "하드코어":
        note_speed = 6
    else:
        note_speed = 4
    pygame.time.set_timer(NEW_NOTE, note_interval)

def mode_select_screen():
    global current_mode
    modes = ["노말", "하드코어", "무한 콤보"]
    while True:
        screen.fill(BLACK)
        draw_text("🎮 모드 선택 🎮", 150, 100, BLUE, BIG_FONT)
        for i, mode in enumerate(modes):
            draw_button(mode, 150, 180 + i * 70, 180, 50)
            draw_text(get_mode_description(mode), 100, 180 + i * 70 + 60, GRAY, FONT)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, mode in enumerate(modes):
                    if 150 <= event.pos[0] <= 330 and (180 + i * 70) <= event.pos[1] <= (230 + i * 70):
                        current_mode = mode
                        return

def get_mode_description(mode):
    if mode == "노말": return "기본 모드"
    if mode == "하드코어": return "빠른 노트, 높은 점수"
    if mode == "무한 콤보": return "콤보가 절대 끊기지 않음"

def game_over_screen():
    while True:
        screen.fill(BLACK)
        draw_text("게임 오버!", 170, 200, RED, BIG_FONT)
        draw_text(f"최종 점수: {score}", 160, 260, WHITE)
        draw_button("다시 시작", 100, 320, 120, 50)
        draw_button("종료", 260, 320, 120, 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 100 <= x <= 220 and 320 <= y <= 370:
                    return True
                elif 260 <= x <= 380 and 320 <= y <= 370:
                    pygame.quit(); sys.exit()

# 시작 화면
mode_select_screen()
reset_game()
pygame.time.set_timer(NEW_NOTE, note_interval)
start_time = pygame.time.get_ticks()
game_active = True

# 게임 루프
while game_active:
    screen.fill(BLACK)
    draw_judgeline()
    draw_text(f"모드: {current_mode}", 360, 10, BLUE)

    # 시간에 따른 노트 속도 증가
    elapsed_time = pygame.time.get_ticks() - start_time
    if elapsed_time // speed_increase_interval > (note_speed - 4) and note_speed < max_speed and not skill_active:
        note_speed += 0.5

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_active = False

        if event.type == NEW_NOTE and not skill_active:
            line = random.randint(0, 3)
            if current_mode == "한 줄 전용":
                line = 2
            notes.append(Note(line))

        if event.type == pygame.KEYDOWN:
            if event.key in key_mapping:
                line = key_mapping[event.key]
                hit = False
                for note in notes:
                    if note.line == line:
                        judgement, pts = get_judgement(note.y)
                        if judgement != "Miss":
                            score += pts * score_multiplier
                            combo += 1
                            judgement_text = judgement
                            notes.remove(note)
                            hit = True
                            if combo % 10 == 0:
                                skill_ready = True
                            break
                if not hit and current_mode != "무한 콤보":
                    combo = 0
                    miss_count += 1
                    judgement_text = "Miss"
            elif event.key == pygame.K_1 and skill_ready:
                skill_active = True
                skill_type = "하드모드"
                skill_ready = False
                skill_timer = pygame.time.get_ticks()
                note_speed *= 2
            elif event.key == pygame.K_2 and skill_ready:
                skill_active = True
                skill_type = "투명화"
                skill_ready = False
                skill_timer = pygame.time.get_ticks()
                score_multiplier = 2
            elif event.key == pygame.K_3 and skill_ready and miss_count >= 5:
                skill_active = True
                skill_type = "리커버리"
                skill_ready = False
                skill_timer = pygame.time.get_ticks()
                miss_count = max(0, miss_count - 3)

    # 블럭 업데이트 및 화면 출력
    for note in notes[:]:
        note.update()
        note.draw()
        if note.y > HEIGHT:
            notes.remove(note)
            if current_mode != "무한 콤보":
                combo = 0
                miss_count += 1
                judgement_text = "Miss"

    # 스킬 종료 타이머
    if skill_active and pygame.time.get_ticks() - skill_timer > 5000:
        skill_active = False
        score_multiplier = 1
        if skill_type == "하드모드":
            note_speed /= 2
        skill_type = None

    # 게임 오버 조건
    if miss_count >= 10:
        game_active = game_over_screen()
        reset_game()
        start_time = pygame.time.get_ticks()

    draw_text(f"점수: {score}", 10, 10)
    draw_text(f"콤보: {combo}", 10, 40)
    draw_text(f"실수: {miss_count}/10", 10, 70)
    draw_text(f"{judgement_text}", 200, 550)
    if skill_ready:
        draw_text("스킬 사용 가능 (1:하드 2:투명 3:회복)", 80, 100)
    elif skill_active:
        draw_text(f"{skill_type} 스킬 발동 중!", 120, 100)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()