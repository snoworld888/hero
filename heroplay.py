import pygame
import sys
import random

# --- 常量定义 ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 40
MAP_WIDTH = 18
MAP_HEIGHT = 14
GRID_COLOR = (50, 50, 50)

# 颜色定义
COLORS = {
    'grass': (34, 139, 34),
    'forest': (0, 100, 0),
    'mountain': (139, 137, 137),
    'water': (30, 144, 255),
    'desert': (238, 203, 173),
    'snow': (240, 248, 255),
    'swamp': (115, 100, 0),
    'lava': (255, 69, 0),
    'background': (0, 0, 0),
    'text': (255, 255, 255),
    'highlight_passable': (0, 255, 0, 100),   # 绿色半透明，可移动
    'highlight_impassable': (255, 0, 0, 100), # 红色半透明，不可移动
    'highlight_hover': (255, 255, 0, 100),    # 黄色半透明，悬停
    'hero_color': (255, 215, 0),              # 金色
    'monster_color': (200, 0, 0),             # 红色
    'resource_color': (255, 215, 0),          # 金色
    'building_color': (139, 69, 19),          # 棕色
}

# --- 游戏对象类 ---
class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.level = 1
        self.experience = 0
        self.primary_skills = {'attack': 1, 'defense': 1, 'spell_power': 1, 'knowledge': 1}
        self.secondary_skills = {'侦察': 1}
        self.spells = ['祈祷']
        self.artifacts = ["生命之书"]
        self.resources = {
            'Gold': 2450, 'Wood': 12, 'Ore': 8, 
            'Mercury': 3, 'Sulfur': 2, 'Crystal': 4, 'Gems': 1
        }
        self.log = ["英雄已就位，开始探索！"]
        self.army = {'剑士': 15, '弓箭手': 8} # 示例军队

    def move_to(self, new_x, new_y, game_map):
        """尝试移动到指定坐标"""
        if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
            tile = game_map[new_y][new_x]
            # 检查地形是否可通行
            if tile in impassable_tiles:
                self.log.append(f"无法移动到 ({new_x}, {new_y}) - 地形不可通行！")
                return False
            
            self.x = new_x
            self.y = new_y
            self.log.append(f"移动到 ({self.x}, {self.y})")
            self._trigger_tile_event(game_map)
            return True
        return False

    def move_by_direction(self, dx, dy, game_map):
        """按方向移动一步"""
        new_x = self.x + dx
        new_y = self.y + dy
        self.move_to(new_x, new_y, game_map)

    def _trigger_tile_event(self, game_map):
        """触发当前格子的事件"""
        tile = game_map[self.y][self.x]
        
        if tile == 'T':  # 城镇
            self._visit_town()
        elif tile == 'X':  # 宝箱
            self._collect_treasure(game_map)
        elif tile == 'R':  # 资源点
            self._collect_resource(game_map)
        elif tile == 'C':  # 怪物营地
            self._fight_monster(game_map)
        elif tile == 'L':  # 图书馆
            self._visit_library()
        elif tile == 'A':  # 竞技场
            self._visit_arena()
        elif tile == 'P':  # 港口
            self._visit_port()
        elif tile == 'I':  # 遗迹
            self._visit_ruins()
        else:
            terrain_name = terrain_names.get(tile, '未知')
            self.log.append(f"在{terrain_name}地形上。")

    def _visit_town(self):
        self.resources['Gold'] += 800
        self.add_skill('后勤')
        self.log.append("访问了城镇！金币+800, 学会【后勤】技能！")

    def _collect_treasure(self, game_map):
        artifact_found = random.choice(["龙鳞甲", "贤者之石", "天使联盟"])
        self.artifacts.append(artifact_found)
        gold_found = random.randint(500, 1500)
        self.resources['Gold'] += gold_found
        game_map[self.y][self.x] = 'G' # 宝箱被拾取后变回草地
        self.log.append(f"拾取了宝箱！获得 {artifact_found} 和 {gold_found} 金币！")

    def _collect_resource(self, game_map):
        resource_type = random.choice(['Wood', 'Ore', 'Mercury', 'Sulfur', 'Crystal', 'Gems'])
        amount = random.randint(1, 3)
        self.resources[resource_type] += amount
        game_map[self.y][self.x] = 'G' # 资源点被采集后变回草地
        self.log.append(f"采集了资源！获得 {amount} 个 {resource_type}！")

    def _fight_monster(self, game_map):
        monster_data = monster_camps.get((self.x, self.y), {'creature': '哥布林', 'count': 10, 'reward_gold': 300})
        creature = monster_data['creature']
        count = monster_data['count']
        reward_gold = monster_data['reward_gold']
        
        print(f"\n遭遇 {count} 只 {creature}！\n")
        # 简化战斗逻辑，总是获胜
        exp_gained = reward_gold // 10
        self.gain_experience(exp_gained)
        self.resources['Gold'] += reward_gold
        self.log.append(f"击败了 {creature} 军队！获得 {reward_gold} 金币和 {exp_gained} 经验！")
        
        # 检查是否有宝物掉落
        if random.random() < 0.3:  # 30% 概率掉落
            artifact_dropped = random.choice(["泰坦之锤", "龙眼"])
            self.artifacts.append(artifact_dropped)
            self.log.append(f"缴获了战利品！获得 {artifact_dropped}！")
        
        # 清除怪物营地
        game_map[self.y][self.x] = 'G'
        del monster_camps[(self.x, self.y)]

    def _visit_library(self):
        new_spell = random.choice(["失忆", "火球术", "治疗", "魔力井"])
        self.spells.append(new_spell)
        self.log.append(f"在图书馆学习了 {new_spell} 法术！")

    def _visit_arena(self):
        for skill in self.primary_skills:
            self.primary_skills[skill] += 1
        self.gain_experience(500)
        self.log.append("在竞技场挑战成功！全属性+1, 获得 500 经验！")

    def _visit_port(self):
        self.log.append("到达了港口，可以在此乘船航行。")

    def _visit_ruins(self):
        artifact_found = random.choice(["魔力源泉", "时光之帽"])
        self.artifacts.append(artifact_found)
        self.log.append(f"在遗迹中发掘出 {artifact_found}！")

    def gain_experience(self, exp):
        old_level = self.level
        self.experience += exp
        self.level = (self.experience // 1000) + 1
        if self.level > old_level:
            self.log.append(f"*** {self.level} 级！ ***")

    def add_skill(self, skill_name):
        if skill_name in self.secondary_skills:
            self.secondary_skills[skill_name] += 1
        else:
            self.secondary_skills[skill_name] = 1
        self.log.append(f"学会了 {skill_name} 技能！")

    def get_stats_text(self):
        stats = [
            f"英雄: {self.name}",
            f"等级: {self.level} (经验: {self.experience})",
            f"金币: {self.resources['Gold']}",
            f"木材: {self.resources['Wood']}, 矿石: {self.resources['Ore']}",
            f"水银: {self.resources['Mercury']}, 硫磺: {self.resources['Sulfur']}",
            f"水晶: {self.resources['Crystal']}, 宝石: {self.resources['Gems']}",
            f"主属性: 攻防法知 {self.primary_skills['attack']}/{self.primary_skills['defense']}/{self.primary_skills['spell_power']}/{self.primary_skills['knowledge']}",
            f"技能: {', '.join([f'{k}:{v}' for k, v in self.secondary_skills.items()])}",
            f"法术: {', '.join(self.spells)}",
            f"宝物: {', '.join(self.artifacts[:3])}",
            f"军队: {dict(self.army)}"
        ]
        return stats

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("英雄无敌3 - 高级地图探索器")
        self.clock = pygame.time.Clock()
        # 使用系统默认字体，解决中文乱码问题
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # 地图生成
        self.game_map = self.generate_map()
        self.hero = Hero(8, 6) # 初始位置
        self.hovered_tile = None
        self.hero.name = "艾尔拉思" # 设置英雄名

    def generate_map(self):
        # 初始化地图为草地
        game_map = [['G' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
        
        # 添加地形
        # 水域
        for x in range(14, 17):
            game_map[2][x] = 'W'
            game_map[3][x] = 'W'
            game_map[4][x] = 'W'
        # 山脉
        for x in range(3, 6):
            game_map[10][x] = 'M'
            game_map[11][x] = 'M'
        for y in range(5, 8):
            game_map[y][12] = 'M'
        # 森林
        for x in range(10, 13):
            for y in range(9, 12):
                game_map[y][x] = 'F'
        # 沙漠
        for x in range(0, 4):
            for y in range(0, 4):
                game_map[y][x] = 'D'
        # 雪地
        for x in range(14, 18):
            for y in range(10, 14):
                game_map[y][x] = 'S'
        # 沼泽
        for x in range(5, 8):
            for y in range(2, 5):
                game_map[y][x] = 'B'
        
        # 放置特殊地点
        game_map[1][1] = 'T'  # 城镇
        game_map[1][13] = 'X' # 宝箱
        game_map[2][7] = 'R'  # 资源点
        game_map[4][5] = 'C'  # 怪物营地
        game_map[6][10] = 'L' # 图书馆
        game_map[12][1] = 'A' # 竞技场
        game_map[0][15] = 'P' # 港口
        game_map[11][15] = 'I' # 遗迹
        game_map[8][3] = 'R'  # 另一个资源点
        game_map[5][15] = 'C' # 另一个怪物营地
        
        return game_map

    def handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        x, y = pos
        # 检查点击是否在地图区域内
        if 0 <= x < MAP_WIDTH * TILE_SIZE and 0 <= y < MAP_HEIGHT * TILE_SIZE:
            grid_x = x // TILE_SIZE
            grid_y = y // TILE_SIZE
            # 尝试移动到点击的格子
            self.hero.move_to(grid_x, grid_y, self.game_map)

    def update_hovered_tile(self, pos):
        """更新悬停的格子坐标"""
        x, y = pos
        if 0 <= x < MAP_WIDTH * TILE_SIZE and 0 <= y < MAP_HEIGHT * TILE_SIZE:
            self.hovered_tile = (x // TILE_SIZE, y // TILE_SIZE)
        else:
            self.hovered_tile = None

    def is_tile_passable(self, x, y):
        """检查指定格子是否可通行"""
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            return self.game_map[y][x] not in impassable_tiles
        return False

    def draw_map(self):
        self.screen.fill(COLORS['background'])
        
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # 绘制地形
                terrain = self.game_map[y][x]
                color = COLORS.get(terrain_colors.get(terrain, 'grass'), COLORS['grass'])
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1) # 边框
                
                # 绘制地形符号
                symbol = terrain_symbols.get(terrain, '')
                if symbol:
                    text_surface = self.small_font.render(symbol, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)
        
        # 高亮悬停的格子
        if self.hovered_tile:
            hx, hy = self.hovered_tile
            hover_rect = pygame.Rect(hx * TILE_SIZE, hy * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            
            # 根据地形决定高亮颜色
            if self.is_tile_passable(hx, hy):
                highlight_color = COLORS['highlight_passable']
            else:
                highlight_color = COLORS['highlight_impassable']
                
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)  # 创建半透明表面
            s.fill(highlight_color)
            self.screen.blit(s, hover_rect)

        # 绘制怪物营地
        for (mx, my), data in monster_camps.items():
            monster_rect = pygame.Rect(mx * TILE_SIZE, my * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, COLORS['monster_color'], monster_rect)
            # 绘制怪物符号
            symbol = '!'
            text_surface = self.small_font.render(symbol, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=monster_rect.center)
            self.screen.blit(text_surface, text_rect)

        # 绘制资源点
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.game_map[y][x] == 'R':
                    resource_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(self.screen, COLORS['resource_color'], resource_rect)
                    # 绘制资源符号
                    symbol = '$'
                    text_surface = self.small_font.render(symbol, True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=resource_rect.center)
                    self.screen.blit(text_surface, text_rect)

        # 绘制英雄
        hero_rect = pygame.Rect(self.hero.x * TILE_SIZE, self.hero.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.screen, COLORS['hero_color'], hero_rect) # 金色代表英雄
        hero_symbol = '@'
        text_surface = self.small_font.render(hero_symbol, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=hero_rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_ui(self):
        # 绘制侧边栏
        sidebar_rect = pygame.Rect(SCREEN_WIDTH - 250, 0, 250, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, (30, 30, 50), sidebar_rect)
        pygame.draw.line(self.screen, GRID_COLOR, (SCREEN_WIDTH - 250, 0), (SCREEN_WIDTH - 250, SCREEN_HEIGHT), 2)

        # 绘制英雄状态
        stats = self.hero.get_stats_text()
        for i, stat in enumerate(stats):
            text_surface = self.small_font.render(stat, True, COLORS['text'])
            self.screen.blit(text_surface, (SCREEN_WIDTH - 240, 20 + i * 22))

        # 绘制日志
        log_title = self.font.render("事件日志:", True, COLORS['text'])
        self.screen.blit(log_title, (SCREEN_WIDTH - 240, 300))
        for i, log_entry in enumerate(self.hero.log[-10:]): # 显示最近10条
            text_surface = self.small_font.render(log_entry, True, COLORS['text'])
            self.screen.blit(text_surface, (SCREEN_WIDTH - 240, 330 + i * 20))

        # 绘制操作提示
        hint_text = [
            "操作:",
            "WASD: 移动",
            "鼠标: 点击移动",
            "ESC: 退出"
        ]
        for i, hint in enumerate(hint_text):
            text_surface = self.small_font.render(hint, True, COLORS['text'])
            self.screen.blit(text_surface, (SCREEN_WIDTH - 240, SCREEN_HEIGHT - 120 + i * 25))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.hero.move_by_direction(0, -1, self.game_map)
                    elif event.key == pygame.K_s:
                        self.hero.move_by_direction(0, 1, self.game_map)
                    elif event.key == pygame.K_a:
                        self.hero.move_by_direction(-1, 0, self.game_map)
                    elif event.key == pygame.K_d:
                        self.hero.move_by_direction(1, 0, self.game_map)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左键点击
                        self.handle_mouse_click(event.pos)
                if event.type == pygame.MOUSEMOTION:
                    self.update_hovered_tile(event.pos)

            self.draw_map()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

# --- 地图元素映射 ---
impassable_tiles = {'W'} # 不可通行的地形
terrain_colors = {
    'G': 'grass', 'F': 'forest', 'M': 'mountain', 
    'W': 'water', 'D': 'desert', 'S': 'snow', 
    'B': 'swamp', 'L': 'lava', 'T': 'building', # 建筑放在对应地形上
    'X': 'grass', 'R': 'grass', 'C': 'grass', 'L': 'building', 'A': 'building',
    'P': 'building', 'I': 'building'
}
terrain_symbols = {
    'G': '.', 'F': '#', 'M': '^', 'W': '~', 'D': ':', 'S': '*',
    'B': '%', 'T': 'T', 'X': 'X', 'R': '$', 'C': '!', 'L': 'L', 'A': 'A',
    'P': 'P', 'I': 'I'
}
terrain_names = {
    'G': '草地', 'F': '森林', 'M': '山脉', 'W': '水域',
    'D': '沙漠', 'S': '雪地', 'B': '沼泽', 'T': '城镇',
    'X': '宝箱', 'R': '资源点', 'C': '怪物营地', 'L': '图书馆',
    'A': '竞技场', 'P': '港口', 'I': '遗迹'
}

# 怪物营地数据
monster_camps = {
    (4, 5): {'creature': '哥布林', 'count': 15, 'reward_gold': 300},
    (5, 15): {'creature': '独眼巨人', 'count': 5, 'reward_gold': 800, 'artifact_drop': True},
    (10, 1): {'creature': '金人', 'count': 1, 'reward_gold': 2000, 'artifact_drop': True},
}

if __name__ == "__main__":
    game = Game()
    game.run()

