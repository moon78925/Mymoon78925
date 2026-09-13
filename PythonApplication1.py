import pygame
import random

# 1. 初始化 Pygame
pygame.init()

# 2. 设置屏幕尺寸 (1280x720 高清大屏)
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
pygame.display.set_caption("Python 跑酷 - 终极 Boss 决战版")

# 3. 定义颜色
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
RED = (255, 60, 60)
GOLD = (255, 215, 0)
BLUE = (0, 191, 255)
PURPLE = (148, 0, 211) # Boss 颜色
GREEN = (0, 255, 0)     # 技能颜色
GRAY = (100, 100, 100)
GROUND_HEIGHT = 40

# 4. 游戏状态
START = 0
PLAYING = 1
GAME_OVER = 2
WIN = 3  # 新增：胜利状态
game_state = START

# 5. 游戏基础变量
player_size = 60
player = pygame.Rect(150, SCREEN_HEIGHT - player_size - GROUND_HEIGHT, player_size, player_size)
gravity = 0.9
player_velocity = 0
jump_power = -18
jumps_left = 2
max_jumps = 2

# 技能相关变量
dash_cooldown = 0
dash_timer = 0
is_dashing = False
shockwave_cooldown = 0
shockwaves = [] # 玩家发射的冲击波

# 拖尾特效
trail = []
trail_length = 10

# 障碍物与道具
obstacles = []
coins = []
shields = []
has_shield = False

# Boss 相关变量
boss = None
boss_width, boss_height = 100, 120
boss_active = False
boss_hp = 100
boss_projectiles = [] # Boss 发射的子弹
boss_attack_timer = 0

spawn_timer = 0
score = 0
high_score = 0

# 字体
try:
    font_huge = pygame.font.SysFont("arial", 100)
    font_large = pygame.font.SysFont("arial", 60)
    font_medium = pygame.font.SysFont("arial", 40)
    font_small = pygame.font.SysFont("arial", 30)
except:
    font_huge = pygame.font.Font(None, 100)
    font_large = pygame.font.Font(None, 60)
    font_medium = pygame.font.Font(None, 40)
    font_small = pygame.font.Font(None, 30)

clock = pygame.time.Clock()
running = True

def reset_game():
    global player, player_velocity, jumps_left, obstacles, coins, shields
    global has_shield, score, spawn_timer, trail, boss, boss_active, boss_hp
    global boss_projectiles, shockwaves, dash_cooldown, shockwave_cooldown, is_dashing
    
    player = pygame.Rect(150, SCREEN_HEIGHT - player_size - GROUND_HEIGHT, player_size, player_size)
    player_velocity = 0
    jumps_left = max_jumps
    obstacles = []
    coins = []
    shields = []
    has_shield = False
    score = 0
    spawn_timer = 0
    trail = []
    
    # 重置 Boss
    boss = pygame.Rect(SCREEN_WIDTH + 100, SCREEN_HEIGHT - boss_height - GROUND_HEIGHT, boss_width, boss_height)
    boss_active = False
    boss_hp = 100
    boss_projectiles = []
    
    # 重置技能
    shockwaves = []
    dash_cooldown = 0
    shockwave_cooldown = 0
    is_dashing = False

def spawn_boss():
    global boss_active, boss
    boss_active = True
    boss.x = SCREEN_WIDTH - 200 # Boss 从右侧入场并固定

# 6. 游戏主循环
while running:
    clock.tick(60)
    
    # --- 事件处理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == START or game_state == GAME_OVER or game_state == WIN:
                    game_state = PLAYING
                    reset_game()
                elif game_state == PLAYING:
                    if jumps_left > 0:
                        player_velocity = jump_power
                        jumps_left -= 1
            
            # 技能按键 (仅在游戏进行中生效)
            if game_state == PLAYING:
                # Z键 - 冲刺
                if event.key == pygame.K_z and dash_cooldown == 0:
                    is_dashing = True
                    dash_timer = 15 # 冲刺持续15帧
                    dash_cooldown = 60 # 冷却60帧
                
                # X键 - 冲击波
                if event.key == pygame.K_x and shockwave_cooldown == 0:
                    shockwave = pygame.Rect(player.right, player.y + player.height//2 - 10, 60, 20)
                    shockwaves.append(shockwave)
                    shockwave_cooldown = 40 # 冷却40帧

    # --- 游戏逻辑更新 ---
    if game_state == PLAYING:
        # 技能冷却更新
        if dash_cooldown > 0: dash_cooldown -= 1
        if shockwave_cooldown > 0: shockwave_cooldown -= 1
        
        # 冲刺逻辑
        if is_dashing:
            dash_timer -= 1
            if dash_timer <= 0:
                is_dashing = False
        
        # 玩家物理
        if not is_dashing: # 冲刺时不受重力影响
            player_velocity += gravity
            player.y += player_velocity
            
        if player.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            player.bottom = SCREEN_HEIGHT - GROUND_HEIGHT
            player_velocity = 0
            jumps_left = max_jumps

        # 更新拖尾
        trail.append(player.copy())
        if len(trail) > trail_length:
            trail.pop(0)

        # 检查是否激活 Boss (分数达到500)
        if score >= 500 and not boss_active:
            spawn_boss()

        # --- Boss 逻辑 (已修复：不再主动向左移动) ---
        if boss_active:
            # Boss 攻击逻辑
            boss_attack_timer += 1
            if boss_attack_timer > 100: # 每100帧攻击一次
                attack_type = random.choice(['dash', 'shoot'])
                if attack_type == 'shoot':
                    # 发射子弹
                    proj = pygame.Rect(boss.x, boss.y + boss.height//2, 40, 40)
                    boss_projectiles.append(proj)
                boss_attack_timer = 0
            
            # 移动 Boss 子弹
            for proj in boss_projectiles:
                proj.x -= 10 # 子弹速度
            
            boss_projectiles = [p for p in boss_projectiles if p.right > 0]

        # --- 普通障碍物生成 (Boss 出现后减少普通障碍物) ---
        if not boss_active or (boss_active and random.random() < 0.3):
            spawn_timer += 1
            spawn_rate = max(40, 100 - score // 50)
            if spawn_timer > random.randint(spawn_rate, spawn_rate + 60):
                obstacle = pygame.Rect(SCREEN_WIDTH, SCREEN_HEIGHT - 70 - GROUND_HEIGHT, 50, 70)
                obstacles.append(obstacle)
                if random.random() < 0.3:
                    item_type = random.choice(['coin', 'shield'])
                    item_y = SCREEN_HEIGHT - 180 if item_type == 'coin' else SCREEN_HEIGHT - 260
                    item = pygame.Rect(SCREEN_WIDTH, item_y, 40, 40)
                    if item_type == 'coin':
                        coins.append(item)
                    else:
                        shields.append(item)
                spawn_timer = 0

        # 移动物体
        for obstacle in obstacles: obstacle.x -= 8
        for coin in coins: coin.x -= 8
        for shield in shields: shield.x -= 8
        for shockwave in shockwaves: shockwave.x += 15 # 冲击波向右飞

        obstacles = [obs for obs in obstacles if obs.right > 0]
        coins = [c for c in coins if c.right > 0]
        shields = [s for s in shields if s.right > 0]
        shockwaves = [s for s in shockwaves if s.left < SCREEN_WIDTH]

        # --- 碰撞检测 ---
        # 1. 玩家 vs 普通障碍物
        hit_obstacle = None
        for obstacle in obstacles:
            if player.colliderect(obstacle):
                hit_obstacle = obstacle
                break
        if hit_obstacle and not is_dashing: # 冲刺时无敌
            if has_shield:
                has_shield = False
                obstacles.remove(hit_obstacle)
            else:
                game_state = GAME_OVER
                if score > high_score: high_score = score

        # 2. 玩家 vs Boss 子弹
        hit_proj = None
        for proj in boss_projectiles:
            if player.colliderect(proj):
                hit_proj = proj
                break
        if hit_proj and not is_dashing:
            if has_shield:
                has_shield = False
                boss_projectiles.remove(hit_proj)
            else:
                game_state = GAME_OVER
                if score > high_score: high_score = score

        # 3. 玩家 vs Boss 本体
        if boss_active and player.colliderect(boss) and not is_dashing:
            if has_shield:
                has_shield = False
                boss.x += 50 # 撞飞 Boss
            else:
                game_state = GAME_OVER
                if score > high_score: high_score = score

        # 4. 冲击波 vs Boss 子弹 (抵消)
        for shockwave in shockwaves:
            for proj in boss_projectiles[:]:
                if shockwave.colliderect(proj):
                    if proj in boss_projectiles:
                        boss_projectiles.remove(proj)
                    if shockwave in shockwaves:
                        shockwaves.remove(shockwave)
                    break

        # 5. 冲击波 vs Boss (扣血)
        if boss_active:
            for shockwave in shockwaves:
                if shockwave.colliderect(boss):
                    boss_hp -= 2
                    if shockwave in shockwaves:
                        shockwaves.remove(shockwave)
                    if boss_hp <= 0:
                        game_state = WIN # 胜利！
                        score += 1000

        # 6. 吃道具
        for coin in coins[:]:
            if player.colliderect(coin):
                score += 50
                coins.remove(coin)
        for shield in shields[:]:
            if player.colliderect(shield):
                has_shield = True
                shields.remove(shield)

        if not boss_active:
            score += 1

    # --- 画面绘制 ---
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))

    if game_state == START:
        title_text = font_huge.render("Boss Battle", True, PURPLE)
        start_text = font_large.render("Press SPACE to Start", True, GRAY)
        skill_text = font_medium.render("Z: Dash | X: Shockwave", True, BLUE)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(skill_text, (SCREEN_WIDTH//2 - skill_text.get_width()//2, SCREEN_HEIGHT//2 + 60))

    elif game_state == PLAYING:
        # 绘制拖尾
        for i, pos in enumerate(trail):
            alpha = int((i / len(trail)) * 150)
            trail_surface = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
            trail_surface.fill((255, 60, 60, alpha))
            screen.blit(trail_surface, pos.topleft)

        # 绘制玩家
        player_color = BLUE if is_dashing else RED # 冲刺时变蓝
        pygame.draw.rect(screen, player_color, player)
        
        # 绘制护盾
        if has_shield:
            pygame.draw.rect(screen, GOLD, (player.x - 8, player.y - 8, player.width + 16, player.height + 16), 4)

        # 绘制普通障碍物
        for obstacle in obstacles: pygame.draw.rect(screen, BLACK, obstacle)
        
        # 绘制道具
        for coin in coins: pygame.draw.circle(screen, GOLD, coin.center, coin.width // 2)
        for shield in shields: pygame.draw.rect(screen, GOLD, shield)
        
        # 绘制技能特效
        for shockwave in shockwaves:
            pygame.draw.rect(screen, GREEN, shockwave)
        
        # 绘制 Boss
        if boss_active:
            pygame.draw.rect(screen, PURPLE, boss)
            # Boss 血条
            pygame.draw.rect(screen, RED, (boss.x, boss.y - 20, boss_width, 10))
            pygame.draw.rect(screen, GREEN, (boss.x, boss.y - 20, boss_width * (boss_hp / 100), 10))
            # Boss 子弹
            for proj in boss_projectiles:
                pygame.draw.circle(screen, RED, proj.center, proj.width // 2)

        # UI 信息
        score_text = font_medium.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))
        
        # 技能冷却显示
        dash_status = "READY" if dash_cooldown == 0 else "COOLDOWN"
        shockwave_status = "READY" if shockwave_cooldown == 0 else "COOLDOWN"
        skill_text = font_small.render(f"Dash(Z): {dash_status} | Shockwave(X): {shockwave_status}", True, GRAY)
        screen.blit(skill_text, (20, 60))

    elif game_state == GAME_OVER:
        game_over_text = font_huge.render("Game Over", True, RED)
        score_text = font_large.render(f"Final Score: {score}", True, BLACK)
        restart_text = font_medium.render("Press SPACE to Restart", True, GRAY)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 60))

    elif game_state == WIN:
        win_text = font_huge.render("YOU WIN!", True, GREEN)
        score_text = font_large.render(f"Final Score: {score}", True, BLACK)
        restart_text = font_medium.render("Press SPACE to Restart", True, GRAY)
        screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//3))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
    
    pygame.display.flip()

pygame.quit()