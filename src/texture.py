import sys

import pygame, os
from typing import List, Tuple, Optional, overload


# Block colors (0: Boundry, 1: Grass, 2: Dirt, 3: Stone, 4: Snow, 5: Water)
BLOCK_TEXTURE_CACHE = {
    0: (0, 0, 0), # Boundry, not meant to be drawn
    1: (34, 177, 76),   # Grass
    2: (121, 85, 58),   # Dirt
    3: (128, 128, 128), # Stone
    4: (240, 240, 240),  # Snow
    5: (100, 150, 255), # Water
    "Sprite_sheet" : None #spritesheet cache
}

def init_block_textures():
    global BLOCK_TEXTURE_CACHE
    sheet = SpriteSheet()
    sheet.extract_grid(r"block_textures\Set_2.png", (32,32))
    BLOCK_TEXTURE_CACHE["Sprite_sheet"] = sheet
    __assign_blocks()

def resize_blocks(w, h):
    global BLOCK_TEXTURE_CACHE
    sheet:SpriteSheet = BLOCK_TEXTURE_CACHE["Sprite_sheet"]

    sheet.rezize_images((w,h))

def __assign_blocks():
    global BLOCK_TEXTURE_CACHE

    sheet:SpriteSheet = BLOCK_TEXTURE_CACHE["Sprite_sheet"]

    BLOCK_TEXTURE_CACHE[1] = sheet.get_image(0)
    BLOCK_TEXTURE_CACHE[2] = sheet.get_image(1)
    BLOCK_TEXTURE_CACHE[3] = sheet.get_image(2)
    BLOCK_TEXTURE_CACHE[4] = sheet.get_image(3)
    

def load_image(path: str) -> pygame.Surface:
    """Load an image from disk with alpha support."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.abspath(os.path.join(script_dir, "..", 'assets', 'images'))
        image = pygame.image.load(os.path.join(BASE_DIR, path))

        return image
    except pygame.error as e:
        raise FileNotFoundError(f"Unable to load image at {path} : {e}") from e


# =====================================================
# Sprite Sheets
# =====================================================
class SpriteSheet:
    def __init__(self):
        #only init
        self.sprite_sheet = None
        self.sprite_sheet_rect = None
        self.images: List[pygame.Surface] = []
        self.original_image: List[pygame.Surface] = []
        
    # ---------------------------------------------------------
    # Method 1: Extract using a list of Rects
    # ---------------------------------------------------------
    def extract_from_rects(
        self,
        path: str,
        rects: List[pygame.Rect],
        scale: Tuple[int, int],
        alpha: int = 255,
        convert_alpha: bool = True
    ) :
        self.sprite_sheet = load_image(path)
        if convert_alpha:
            self.sprite_sheet = self.sprite_sheet.convert_alpha()
       
        self.sprite_sheet_rect = self.sprite_sheet.get_rect()
        images: List[pygame.Surface] = []

        for rect in rects:
            image = pygame.Surface(rect.size, pygame.SRCALPHA)
            image.blit(self.sprite_sheet, (0, 0), rect)
            image = pygame.transform.scale(image, scale)
            image.set_alpha(alpha)
            images.append(image)

        self.images.extend(images)
        self.original_image.extend(images)


    # ---------------------------------------------------------
    # Method 2: Extract grid-style
    # ---------------------------------------------------------
    def extract_grid(
        self,
        path: str,
        crop_size: Tuple[int, int],
        start: Tuple[int, int] = (0, 0),
        scale: Tuple[int, int] | None = None,
        alpha: int = 255,
        convert_alpha: bool = True
    ):

        self.sprite_sheet = load_image(path)
        if convert_alpha:
            self.sprite_sheet = self.sprite_sheet.convert_alpha()
        self.sprite_sheet_rect = self.sprite_sheet.get_rect()
        images: List[pygame.Surface] = []
        
        w_crop, h_crop = crop_size
        x_start, y_start = start

        for y in range(y_start, self.sprite_sheet_rect.height, h_crop):
            for x in range(x_start, self.sprite_sheet_rect.width, w_crop):
                rect = pygame.Rect(x, y, w_crop, h_crop)

                image = pygame.Surface(rect.size, pygame.SRCALPHA)
                image.blit(self.sprite_sheet, (0, 0), rect)

                if scale:
                    image = pygame.transform.scale(image, scale)

                image.set_alpha(alpha)
                images.append(image)
                self.original_image.append(image)

        self.images.extend(images)

    def extract_single_image(self, path: str, scale: Tuple[int, int], alpha: int = 255, convert_alpha: bool = True):
        image = load_image(path)
        image = pygame.transform.scale(image, scale)
        if convert_alpha:
            image = image.convert_alpha()
        else:   image = image.convert()
        image.set_alpha(alpha)
        self.images.append(image)
        self.original_image.append(image)

#   all the init of @overload functions are in the SpriteSheet class, so that we can use it to rotate and scale images easily. We can also use it to extract images from a sprite sheet easily. The @overload functions are just for type hinting and do not have any implementation. The actual implementation is in the functions below them. This way we can have multiple ways to rotate and scale images without having to write multiple functions for each case.
    @overload
    def rotate_images(self, angle: int) -> None: ...

    @overload 
    def rotate_images(self, angle: int, index: int) -> None: ... 

    @overload
    def rezize_images(self, size: Tuple[int, int]) -> None: ...

    @overload
    def rezize_images(self, size: Tuple[int, int], index: int) -> None: ...

   
#   The actual implementation of the above functions. The index parameter is optional, if it is provided, only the image at that index will be rotated or resized, otherwise all images will be rotated or resized.

    def rezize_images(self, size: Tuple[int, int], index: Optional[int] = None) -> None:
        if index is not None:
            self.images[index] = pygame.transform.scale(self.original_image[index], size)
            return
        else:
            for i in range(len(self.images)):
                self.images[i] = pygame.transform.scale(self.original_image[i], size)
            return

    def rotate_images(self, angle: int, index: int | None = None) -> None:
        if index is not None:
            self.images[index] = pygame.transform.rotate(self.original_image[index], angle)
            return
        else:
            for i in range(len(self.images)):
                self.images[i] = pygame.transform.rotate(self.original_image[i], angle)
            return
        


    # ---------------------------------------------------------
    def get_image(self, index: int) -> pygame.Surface:
        return self.images[index]
    
    def remove(self, index:int):
        self.images.pop(index)
    
def test():
    # Initialize Pygame and the display
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("SpriteSheet Renderer")
    clock = pygame.time.Clock()

    # Load textures
    init_block_textures()

    # Grab the grass block image from your cache
    grass_img = BLOCK_TEXTURE_CACHE[2]

    # Main game loop
    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Rendering
        # Clear screen with a background color (e.g., a sky blue)
        screen.fill((135, 206, 235))
        
        # Draw the grass image at (100, 100) on the screen
        screen.blit(grass_img, (100, 100))

        # 3. Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    test()