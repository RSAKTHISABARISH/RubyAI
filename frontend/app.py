import pygame
import threading
import math
import time
import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ruby.ruby_mainframe import Ruby


# -------------------------------
# CONFIG
# -------------------------------
WIDTH, HEIGHT = 600, 600
FPS = 60

BG_COLOR = (18, 18, 24)
IDLE_COLOR = (120, 120, 120)
LISTENING_COLOR = (0, 180, 255)
SPEAKING_COLOR = (255, 90, 90)
THINKING_COLOR = (255, 255, 255)


# -------------------------------
# PULSING CIRCLE
# -------------------------------
class PulseCircle:
    def __init__(self, center, base_radius=60):
        self.center = center
        self.base_radius = base_radius
        self.time = 0

    def draw(self, screen, color, intensity=1.0):
        self.time += 0.05
        pulse = math.sin(self.time) * 10 * intensity
        radius = int(self.base_radius + pulse)
        pygame.draw.circle(screen, color, self.center, radius)


# -------------------------------
# RUBY THREAD
# -------------------------------
class RubyWorker(threading.Thread):
    def __init__(self, ruby):
        super().__init__(daemon=True)
        self.ruby = ruby
        self.running = True

    def run(self):
        while self.running:
            try:
                user_input = self.ruby.listen()
                if user_input:
                    self.ruby.speak(user_input)
            except Exception as e:
                print("Ruby error:", e)
                time.sleep(1)

    def stop(self):
        self.running = False


# -------------------------------
# MAIN UI
# -------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ruby Voice Agent")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 22)

    ruby = Ruby()
    worker = RubyWorker(ruby)
    worker.start()
    pulse_circle = PulseCircle(center=(WIDTH // 2, HEIGHT // 2))

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Stop speaking immediately
                if ruby.ruby_state == "Speaking":
                    print("🛑 Stopping TTS")
                    ruby.tts.stop()
                    ruby.ruby_state = "Idel"

        # -----------------------
        # STATE → COLOR
        # -----------------------
        if ruby.ruby_state == "Listening":
            color = LISTENING_COLOR
            intensity = 1.5
            status_text = "Listening..."
        elif ruby.ruby_state == "Speaking":
            color = SPEAKING_COLOR
            intensity = 1.2
            status_text = "Speaking..."
        elif ruby.ruby_state == "Thinking":
            color = THINKING_COLOR
            intensity = 1.2
            status_text = "Thinking..."
        elif ruby.ruby_state == "Playing Video":
            color = THINKING_COLOR
            intensity = 1.2
            status_text = "Playing Video..."
        elif ruby.ruby_state == "Searching Video":
            color = THINKING_COLOR
            intensity = 1.2
            status_text = "Searching Video..."
        else:
            color = IDLE_COLOR
            intensity = 0.5
            status_text = "Idle"

        # -----------------------
        # DRAW
        # -----------------------
        screen.fill(BG_COLOR)

        pulse_circle.draw(screen, color, intensity)

        text_surface = font.render(status_text, True, (220, 220, 220))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()

    worker.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
