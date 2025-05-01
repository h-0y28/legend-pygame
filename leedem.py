import pygame
import random
import sys

# 초기 설정
pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("리듬게임: 보스전 with 롱노트")
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
PLAYER_HP_COLOR = (0, 255, 255)  # 내 체력바 색상 (청록색)

# 게임 변수
lines = [90, 180, 270, 360]
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

# 시간 기반 속도 증가
start_time = pygame.time.get_ticks()
speed_increase_interval = 10000
max_speed = 10

# 노트 생성
note_interval = 700
NEW_NOTE = pygame.USEREVENT + 1

# 체력
player_hp = 100
boss_max_hp = 1500
boss_hp = boss_max_hp

# 보스 스킬 상태
boss_heal_used = False
boss_rage_used = False
rage_mode = False
rage_start_time = 0
rage_duration = 5000

key_mapping = {
    pygame.K_d: 0,
    pygame.K_f: 1,
    pygame.K_j: 2,
    pygame.K_k: 3,
}

# 음원 로드
C_note = pygame.mixer.Sound("C4.mp3")  # 도
D_note = pygame.mixer.Sound("D4.mp3")  # 레
E_note = pygame.mixer.Sound("E4.mp3")  # 미
F_note = pygame.mixer.Sound("F4.mp3")  # 파

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
    if 570 <= note_y <= 630:
        return "Perfect", 300
    elif 540 <= note_y <= 660:
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

def draw_boss_hp_bar():
    bar_width = 300
    bar_height = 20
    bar_x = 90
    bar_y = 50
    fill = (boss_hp / boss_max_hp) * bar_width
    pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill, bar_height))
    
    # 보스 체력 텍스트
    draw_text("보스 체력", bar_x + bar_width // 2 - 40, bar_y - 20, WHITE, FONT)

def draw_player_hp_bar():
    bar_width = 300
    bar_height = 20
    bar_x = 90
    bar_y = 100
    fill = (player_hp / 100) * bar_width
    pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, PLAYER_HP_COLOR, (bar_x, bar_y, fill, bar_height))  # 내 체력바 색상 변경
    
    # 내 체력 텍스트
    draw_text("내 체력", bar_x + bar_width // 2 - 40, bar_y - 20, WHITE, FONT)

def reset_game():
    global notes, score, combo, miss_count, judgement_text
    global skill_ready, skill_active, skill_type, note_speed, score_multiplier
    global player_hp, boss_hp, boss_heal_used, boss_rage_used, rage_mode, note_interval

    notes.clear()
    score = 0
    combo = 0
    miss_count = 0
    judgement_text = ""
    skill_ready = False
    skill_active = False
    skill_type = None
    score_multiplier = 1
    player_hp = 100
    boss_hp = boss_max_hp
    boss_heal_used = False
    boss_rage_used = False
    rage_mode = False

    if current_mode == "하드코어":
        note_speed = 10
        note_interval = 150
    elif current_mode == "어려움":
        note_speed = 6
        note_interval = 400
    else:
        note_speed = 4
        note_interval = 700

    pygame.time.set_timer(NEW_NOTE, note_interval)

def mode_select_screen():
    global current_mode
    modes = ["노말", "어려움", "하드코어", "무한 콤보"]
    while True:
        screen.fill(BLACK)
        draw_text("🎮 모드 선택 🎮", 120, 100, BLUE, BIG_FONT)
        for i, mode in enumerate(modes):
            button_y = 180 + i * 90
            draw_button(mode, 150, button_y, 180, 50)
            draw_text(get_mode_description(mode), 150, button_y + 50, GRAY)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, mode in enumerate(modes):
                    if 150 <= event.pos[0] <= 330 and 180 + i * 90 <= event.pos[1] <= 230 + i * 90:
                        current_mode = mode
                        return

def get_mode_description(mode):
    if mode == "노말": return "기본 모드"
    if mode == "어려움": return "속도 증가, 더 자주 생성"
    if mode == "하드코어": return "매우 빠른 노트, 매우 빠른 생성"
    if mode == "무한 콤보": return "콤보가 끊기지 않음"

def game_over_screen():
    while True:
        screen.fill(BLACK)
        draw_text("게임 오버!", 170, 200, RED, BIG_FONT)
        draw_text(f"최종 점수: {score}", 160, 260)
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
start_time = pygame.time.get_ticks()
game_active = True

# 키 누름 상태 추적
keys_held = {k: False for k in key_mapping.keys()}

while game_active:
    screen.fill(BLACK)
    draw_judgeline()
    draw_boss_hp_bar()
    draw_player_hp_bar()  # 체력바를 화면에 추가

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_active = False
        if event.type == NEW_NOTE:
            line = random.randint(0, 3)
            notes.append(Note(line))

        if event.type == pygame.KEYDOWN:
            if event.key in key_mapping:
                keys_held[event.key] = True
                line = key_mapping[event.key]
                hit = False
                for note in notes:
                    if note.line == line and abs(note.y - 600) < 50:
                        judgement, pts = get_judgement(note.y)
                        if judgement == "Perfect":
                            player_hp = min(100, player_hp + 5)  # Perfect일 때 체력 회복
                        elif judgement == "Good":
                            player_hp = min(100, player_hp + 2)  # Good일 때 체력 회복

                        if judgement != "Miss":
                            score += pts * score_multiplier
                            combo += 1
                            judgement_text = judgement
                            notes.remove(note)
                            hit = True
                            boss_hp -= 30 if judgement == "Perfect" else 10

                            # 음 출력
                            if line == 0:
                                C_note.play()  # 도
                            elif line == 1:
                                D_note.play()  # 레
                            elif line == 2:
                                E_note.play()  # 미
                            elif line == 3:
                                F_note.play()  # 파
                            break
                if not hit and current_mode != "무한 콤보":
                    combo = 0
                    miss_count += 1
                    judgement_text = "Miss"
                    player_hp -= 10
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
                player_hp = min(100, player_hp + 20)
        if event.type == pygame.KEYUP:
            if event.key in keys_held:
                keys_held[event.key] = False

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
                player_hp -= 10

    if boss_hp <= 0:
        screen.fill(BLACK)
        draw_text("보스를 이겼다!", 100, 300, GREEN, BIG_FONT)
        pygame.display.flip()
        pygame.time.delay(3000)
        game_active = game_over_screen()
        reset_game()
        start_time = pygame.time.get_ticks()

    if player_hp <= 0:
        game_active = game_over_screen()
        reset_game()
        start_time = pygame.time.get_ticks()

    draw_text(f"점수: {score}", 10, 10)
    draw_text(f"콤보: {combo}", 10, 40)
    draw_text(f"실수: {miss_count}", 10, 70)
    draw_text(f"{judgement_text}", 200, 550)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
