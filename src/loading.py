import pygame as pg
import threading
import time
import utils
import texture
import math

class Loading:
    def __init__(self, main_app):
        self.app = main_app
        self.screen = main_app.screen
        
        # Track tasks and their states
        self.tasks = {
            "Textures": {"desc": "Loading & scaling block textures...", "status": "pending", "progress": 0.0},
            "Terrain": {"desc": "Pre-generating spawn chunks...", "status": "pending", "progress": 0.0},
            "Cache": {"desc": "Warming up font and UI cache...", "status": "pending", "progress": 0.0}
        }
        
        self.total_progress = 0.0
        self.font_color = (255, 255, 255)
        self.bar_bg_color = (40, 45, 52)
        self.bar_fill_color = (0, 180, 216)
        self.accent_color = (144, 224, 239)

    def run(self):
        # We start the terrain generation in a background thread (thread-safe math calculations)
        terrain_thread = threading.Thread(target=self.task_generate_terrain)
        terrain_thread.start()

        # We run Pygame-related texture loading and UI rendering on the main thread 
        # to guarantee Pygame rendering safety.
        self.task_initialize_textures()
        self.task_prewarm_cache()

        # Wait for the terrain generation background thread to wrap up completely
        while terrain_thread.is_alive() or self.total_progress < 1.0:
            self.events()
            
            # Smoothly animate the visual progress indicator
            completed = sum(1.0 for t in self.tasks.values() if t["status"] == "completed")
            # Terrain contributes dynamically based on its exact chunk generation progress
            terrain_contrib = self.tasks["Terrain"]["progress"] if self.tasks["Terrain"]["status"] != "completed" else 1.0
            
            # Calculate an aggregate progress value
            total_tasks_completed = 0.0
            if self.tasks["Textures"]["status"] == "completed":
                total_tasks_completed += 1.0
            if self.tasks["Cache"]["status"] == "completed":
                total_tasks_completed += 1.0
            total_tasks_completed += terrain_contrib
            
            target_prog = total_tasks_completed / len(self.tasks)
            self.total_progress += (target_prog - self.total_progress) * 0.1
            
            if abs(self.total_progress - 1.0) < 0.01 and completed == len(self.tasks):
                self.total_progress = 1.0
                
            self.display()
            time.sleep(0.01) # Maintain loading loop stability

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                import sys
                sys.exit()

    def display(self):
        # Clear screen to a deep, premium dark background
        self.screen.fill((18, 20, 24))
        
        w, h = self.screen.get_size()
        cx, cy = w // 2, h // 2
        
        # Pulse animation factor for the text glow
        pulse = (math.sin(time.time() * 5) + 1.0) / 2.0
        animated_accent = (
            int(self.accent_color[0] + (255 - self.accent_color[0]) * pulse * 0.2),
            int(self.accent_color[1] + (255 - self.accent_color[1]) * pulse * 0.2),
            int(self.accent_color[2] + (255 - self.accent_color[2]) * pulse * 0.2)
        )

        # 1. Main Loading Text
        utils.draw_text(self.screen, "Pytherra", 64, animated_accent, (cx - 110, cy - 100))
        
        # 2. Progress Bar Outline and Filling
        bar_w, bar_h = 450, 16
        bar_x, bar_y = cx - (bar_w // 2), cy + 10
        
        # Draw background track
        pg.draw.rect(self.screen, self.bar_bg_color, (bar_x, bar_y, bar_w, bar_h), border_radius=8)
        # Draw dynamic progress bar
        fill_w = int(bar_w * self.total_progress)
        if fill_w > 0:
            pg.draw.rect(self.screen, self.bar_fill_color, (bar_x, bar_y, fill_w, bar_h), border_radius=8)
            
        # 3. Dynamic Task Description Text
        active_desc = "Finishing startup..."
        for task_name, info in self.tasks.items():
            if info["status"] == "running" or (info["status"] == "pending" and active_desc == "Finishing startup..."):
                active_desc = info["desc"]
                break
                
        # Draw progress percentage
        percent_str = f"{int(self.total_progress * 100)}%"
        utils.draw_text(self.screen, percent_str, 28, self.font_color, (cx - 20, cy + 35))
        utils.draw_text(self.screen, active_desc, 24, (160, 166, 178), (cx - 150, cy + 70))

        pg.display.flip()

    # --- REAL LOADING WORKERS ---

    def task_initialize_textures(self):
        """Initializes and pre-allocates block graphics."""
        self.tasks["Textures"]["status"] = "running"
        self.display()
        
        try:
            # Check if block assets are ready to load
            texture.init_block_textures()
        except Exception:
            # Safe fallback if asset directory is missing locally
            print("Warning: Block texture assets not found. Using fallback colors.")
            
        self.tasks["Textures"]["status"] = "completed"

    def task_generate_terrain(self):
        """Pre-calculates world chunks surrounding the spawning coordinates."""
        self.tasks["Terrain"]["status"] = "running"
        
        # We generate 81 chunks (from chunk coordinate -40 to 40)
        # This gives a beautiful pre-loaded radius of over 2,500 blocks!
        start_chunk = -40
        end_chunk = 40
        total_chunks = (end_chunk - start_chunk) + 1
        
        for idx, cx in enumerate(range(start_chunk, end_chunk + 1)):
            self.app.world.get_chunk(cx)
            # Dynamically calculate sub-task progress so the loading bar moves smoothly
            self.tasks["Terrain"]["progress"] = (idx + 1) / total_chunks
            
        self.tasks["Terrain"]["status"] = "completed"

    def task_prewarm_cache(self):
        """Pre-allocates textures for standard UI font rendering."""
        self.tasks["Cache"]["status"] = "running"
        self.display()
        
        # Pre-cache frequently drawn UI strings to prevent lag spike when they load mid-game
        common_strings = ["FPS: 60", "Player Pos: 0, 0", "Collision: bottom", "Scale: W:1.0, H:1.0", "Grounded (not jump): True"]
        for s in common_strings:
            utils.create_text(s, 40, (255, 255, 255))
            
        self.tasks["Cache"]["status"] = "completed"