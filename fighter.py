import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0  # 0= Idle 1= Run 2= Jump 3= Attack1 4= Attack2 5= Hit 6= Death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.displayed_health = 100
        self.alive = True
        self.original_x = x
        self.attack_duration = 0  # Duration the attack animation should last

    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def move(self, screen_width, screen_height, surface, target, round_over):
        if self.player == 1:
            SPEED = 15  # Faster speed for character 1
        else:
            SPEED = 10  # Default speed for character 2
        
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        # Keypresses
        key = pygame.key.get_pressed()
        if not self.attacking and self.alive and not round_over:
            if self.player == 1:
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                elif key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_w] and not self.jump:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

            if self.player == 2:
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                elif key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                if key[pygame.K_UP] and not self.jump:
                    self.vel_y = -30
                    self.jump = True
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2

        self.vel_y += GRAVITY
        dy += self.vel_y
        GROUND_LEVEL = screen_height - -100

        if self.rect.left + dx < 0:
            dx = 0 - self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > GROUND_LEVEL:
            self.vel_y = 0
            self.jump = False
            dy = GROUND_LEVEL - self.rect.bottom

        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # 6: Death
        elif self.hit:
            self.update_action(5)  # 5: Hit
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3)  # 3: Attack 1
            elif self.attack_type == 2:
                self.update_action(4)  # 4: Attack 2
        elif self.jump:
            self.update_action(2)  # 2: Jump
        elif self.running:
            self.update_action(1)  # 1: Run
        else:
            self.update_action(0)  # 0: Idle
        
        health_diff = self.health - self.displayed_health
        if abs(health_diff) > 0.1:
            self.displayed_health += health_diff * 0.1

        animation_cd = 75
        if pygame.time.get_ticks() - self.update_time > animation_cd:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            if self.frame_index >= len(self.animation_list[self.action]):
                if not self.alive:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0
                    if self.action in [3, 4]:
                        self.attacking = False
                        self.attack_cooldown = 20
                    if self.action == 5:
                        self.hit = False
                        self.attacking = False
                        self.attack_cooldown = 20
            self.image = self.animation_list[self.action][self.frame_index]

    def attack(self, target):
        if self.attack_cooldown == 0:
            # Execute Attack
            self.attacking = True
            self.attack_sound.play()

            # Different attack sizes for each character
            if self.player == 1:
                attacking_rect = pygame.Rect(
                    self.rect.centerx - (2 * self.rect.width * self.flip), 
                    self.rect.y, 
                    2 * self.rect.width, 
                    self.rect.height
                )
                
            else:  # Player 2
                attacking_rect = pygame.Rect(
                    self.rect.centerx - (4 * self.rect.width * self.flip), 
                    self.rect.y, 
                    4 * self.rect.width, 
                    self.rect.height
                )

            # Determine damage based on attack type
            damage = 10 if self.attack_type == 1 else 20

            if attacking_rect.colliderect(target.rect):
                target.health -= damage
                target.hit = True

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
