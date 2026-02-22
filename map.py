import pygame
import sys
import random
from enum import Enum

class TerrainType(Enum):
    GRASS = 0
    WATER = 1
    MOUNTAIN = 2
    FOREST = 3
    DESERT = 4
    SWAMP = 5

class ObjectType(Enum):
    EMPTY = 0
    HERO = 1
    TOWN = 2
    RESOURCE = 3
    MONSTER = 4
    ARTIFACT = 5

class Tile:
    def __init__(self, terrain_type, object_type=ObjectType.EMPTY):
        self.terrain_type = terrain_type
        self.object_type = object_type
        self.explored = True  # 在这个版本中所有地图都是可见的

class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.name = "玩家英雄"
        self.color = (0, 100, 255)  # 蓝色代表玩家

class MapRenderer:
    def __init__(self, width=48, height=48):
        self.width = width
        self.height = height
        self.tiles = [[None for _ in range(width)] for _ in range(height)]
        self.heroes = []
        self.towns = []
        self.resources = []
        self.monsters = []
        self.artifacts = []
        
        # 初始化地图
        self.generate_map()
        self.place_objects()
        
        # 创建一个英雄
        self.player_hero = Hero(10, 10)
        self.heroes.append(self.player_hero)
        
        # Pygame初始化
        pygame.init()
        self.tile_size = 16
        self.screen_width = self.width * self.tile_size
        self.screen_height = self.height * self.tile_size
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("英雄无敌3风格大地图")
        self.clock = pygame.time.Clock()
        
        # 字体初始化
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 10)

    def generate_map(self):
        """生成地形"""
        for y in range(self.height):
            for x in range(self.width):
                # 基础地形
                rand_val = random.random()
                
                if rand_val < 0.4:
                    terrain = TerrainType.GRASS
                elif rand_val < 0.55:
                    terrain = TerrainType.FOREST
                elif rand_val < 0.7:
                    terrain = TerrainType.MOUNTAIN
                elif rand_val < 0.9:
                    terrain = TerrainType.WATER
                else:
                    terrain = TerrainType.DESERT
                
                self.tiles[y][x] = Tile(terrain)

    def place_objects(self):
        """放置地图对象"""
        # 放置城镇
        for i in range(8):
            placed = False
            while not placed:
                x = random.randint(2, self.width-3)
                y = random.randint(2, self.height-3)
                
                # 确保城镇不在水里或山上
                if self.tiles[y][x].terrain_type not in [TerrainType.WATER, TerrainType.MOUNTAIN]:
                    self.tiles[y][x].object_type = ObjectType.TOWN
                    self.towns.append((x, y, f"城镇{i+1}"))
                    placed = True
        
        # 放置资源
        for i in range(15):
            placed = False
            while not placed:
                x = random.randint(1, self.width-2)
                y = random.randint(1, self.height-2)
                
                if self.tiles[y][x].object_type == ObjectType.EMPTY:
                    self.tiles[y][x].object_type = ObjectType.RESOURCE
                    self.resources.append((x, y, f"资源{i+1}"))
                    placed = True
        
        # 放置怪物
        for i in range(20):
            placed = False
            while not placed:
                x = random.randint(1, self.width-2)
                y = random.randint(1, self.height-2)
                
                if self.tiles[y][x].object_type == ObjectType.EMPTY:
                    self.tiles[y][x].object_type = ObjectType.MONSTER
                    self.monsters.append((x, y, f"怪物{i+1}"))
                    placed = True
        
        # 放置宝物
        for i in range(10):
            placed = False
            while not placed:
                x = random.randint(1, self.width-2)
                y = random.randint(1, self.height-2)
                
                if self.tiles[y][x].object_type == ObjectType.EMPTY:
                    self.tiles[y][x].object_type = ObjectType.ARTIFACT
                    self.artifacts.append((x, y, f"宝物{i+1}"))
                    placed = True

    def get_terrain_color(self, terrain_type):
        """获取地形颜色"""
        colors = {
            TerrainType.GRASS: (34, 139, 34),      # 深绿色
            TerrainType.WATER: (64, 164, 223),     # 蓝色
            TerrainType.MOUNTAIN: (139, 137, 137), # 灰色
            TerrainType.FOREST: (0, 100, 0),       # 森林绿
            TerrainType.DESERT: (238, 203, 173),   # 沙色
            TerrainType.SWAMP: (70, 130, 180)      # 青蓝色
        }
        return colors.get(terrain_type, (255, 255, 255))

    def get_object_symbol(self, object_type):
        """获取对象符号"""
        symbols = {
            ObjectType.HERO: '@',
            ObjectType.TOWN: 'T',
            ObjectType.RESOURCE: 'R',
            ObjectType.MONSTER: 'M',
            ObjectType.ARTIFACT: 'A'
        }
        return symbols.get(object_type, '')

    def draw_map(self):
        """绘制地图"""
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                
                # 绘制地形
                color = self.get_terrain_color(tile.terrain_type)
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, 
                                  self.tile_size, self.tile_size)
                pygame.draw.rect(self.screen, color, rect)
                
                # 绘制网格线
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        
        # 绘制地图对象
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                
                if tile.object_type != ObjectType.EMPTY:
                    symbol = self.get_object_symbol(tile.object_type)
                    text_surface = self.font.render(symbol, True, (255, 255, 255))
                    
                    # 居中绘制符号
                    text_rect = text_surface.get_rect()
                    text_rect.center = (
                        x * self.tile_size + self.tile_size // 2,
                        y * self.tile_size + self.tile_size // 2
                    )
                    self.screen.blit(text_surface, text_rect)
        
        # 绘制英雄
        hero_x, hero_y = self.player_hero.x, self.player_hero.y
        hero_rect = pygame.Rect(
            hero_x * self.tile_size, 
            hero_y * self.tile_size, 
            self.tile_size, 
            self.tile_size
        )
        pygame.draw.rect(self.screen, self.player_hero.color, hero_rect)
        
        # 在英雄上绘制特殊标记
        hero_text = self.font.render('@', True, (255, 255, 255))
        text_rect = hero_text.get_rect()
        text_rect.center = (
            hero_x * self.tile_size + self.tile_size // 2,
            hero_y * self.tile_size + self.tile_size // 2
        )
        self.screen.blit(hero_text, text_rect)

    def move_hero(self, dx, dy):
        """移动英雄"""
        new_x = max(0, min(self.width - 1, self.player_hero.x + dx))
        new_y = max(0, min(self.height - 1, self.player_hero.y + dy))
        
        # 检查移动是否有效（不能进入水中或山上）
        target_tile = self.tiles[new_y][new_x]
        if target_tile.terrain_type not in [TerrainType.WATER, TerrainType.MOUNTAIN]:
            self.player_hero.x = new_x
            self.player_hero.y = new_y
        else:
            print(f"无法移动到 {target_tile.terrain_type.name} 地形")

    def run(self):
        """主循环"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_UP:
                        self.move_hero(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.move_hero(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.move_hero(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_hero(1, 0)
            
            # 清屏
            self.screen.fill((0, 0, 0))
            
            # 绘制地图
            self.draw_map()
            
            # 更新显示
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

# 运行游戏
if __name__ == "__main__":
    game = MapRenderer()
    game.run()
