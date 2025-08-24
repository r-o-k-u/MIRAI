import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame.gfxdraw
from datetime import datetime
import threading
import time

class DataVisualizer:
    def __init__(self, motor_controller, width=1200, height=800):
        self.motor_controller = motor_controller
        self.width = width
        self.height = height
        self.running = False
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("MIRAI Motor Control Dashboard")
        
        # Initialize matplotlib figures
        self.setup_plots()
        
        # Colors
        self.colors = {
            'background': (25, 25, 35),
            'panel': (40, 40, 50),
            'text': (220, 220, 220),
            'accent': (0, 150, 255),
            'left_motor': (255, 100, 100),
            'right_motor': (100, 255, 100),
            'emergency': (255, 50, 50),
            'success': (50, 255, 50)
        }
        
        # Fonts
        self.fonts = {
            'large': pygame.font.SysFont('Arial', 32),
            'medium': pygame.font.SysFont('Arial', 24),
            'small': pygame.font.SysFont('Arial', 18)
        }
    
    def setup_plots(self):
        # Create matplotlib figures for real-time plotting
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(10, 8))
        self.canvas = FigureCanvasAgg(self.fig)
        
        # Configure plots
        self.ax1.set_title('Motor Speeds')
        self.ax1.set_ylabel('Speed')
        self.ax1.grid(True)
        
        self.ax2.set_title('Motor Targets vs Actual')
        self.ax2.grid(True)
        
        self.ax3.set_title('Pulse Counts')
        self.ax3.set_ylabel('Pulses')
        self.ax3.grid(True)
        
        self.ax4.set_title('System Status')
        self.ax4.grid(True)
        
        plt.tight_layout()
    
    def start(self):
        self.running = True
        self.visualization_thread = threading.Thread(target=self._visualization_loop)
        self.visualization_thread.start()
        print("Data visualizer started")
    
    def stop(self):
        self.running = False
        if self.visualization_thread:
            self.visualization_thread.join()
        pygame.quit()
        print("Data visualizer stopped")
    
    def _visualization_loop(self):
        clock = pygame.time.Clock()
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.update_plots()
            self.render_dashboard()
            
            pygame.display.flip()
            clock.tick(30)  # 30 FPS
    
    def update_plots(self):
        history = self.motor_controller.get_history()
        
        if len(history['timestamp']) > 0:
            # Update speed plot
            self.ax1.clear()
            self.ax1.plot(history['timestamp'], history['left_speed'], 
                         label='Left Speed', color='red')
            self.ax1.plot(history['timestamp'], history['right_speed'], 
                         label='Right Speed', color='green')
            self.ax1.set_title('Motor Speeds')
            self.ax1.legend()
            self.ax1.grid(True)
            
            # Update target vs actual plot
            self.ax2.clear()
            self.ax2.plot(history['timestamp'], history['left_target'], 
                         label='Left Target', color='red', linestyle='--')
            self.ax2.plot(history['timestamp'], history['left_speed'], 
                         label='Left Actual', color='red')
            self.ax2.plot(history['timestamp'], history['right_target'], 
                         label='Right Target', color='green', linestyle='--')
            self.ax2.plot(history['timestamp'], history['right_speed'], 
                         label='Right Actual', color='green')
            self.ax2.set_title('Target vs Actual Speeds')
            self.ax2.legend()
            self.ax2.grid(True)
            
            # Update pulse count plot
            self.ax3.clear()
            self.ax3.plot(history['timestamp'], history['left_pulses'], 
                         label='Left Pulses', color='red')
            self.ax3.plot(history['timestamp'], history['right_pulses'], 
                         label='Right Pulses', color='green')
            self.ax3.set_title('Hall Sensor Pulse Counts')
            self.ax3.legend()
            self.ax3.grid(True)
            
            # Update system status (simplified)
            self.ax4.clear()
            status = self.motor_controller.get_status()
            system_vars = [
                status['system']['emergency_stop'],
                status['system']['braking'],
                status['system']['ros_connected']
            ]
            self.ax4.bar(['Emergency', 'Braking', 'ROS Connected'], 
                        system_vars, color=['red', 'orange', 'blue'])
            self.ax4.set_title('System Status')
            self.ax4.set_ylim(0, 1)
            
            # Draw the canvas
            self.canvas.draw()
            self.canvas.flush_events()
    
    def render_dashboard(self):
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Get current status
        status = self.motor_controller.get_status()
        
        # Draw panels
        self.draw_panel(20, 20, 560, 760, "Motor Status")
        self.draw_panel(600, 20, 580, 360, "Real-time Plots")
        self.draw_panel(600, 400, 580, 380, "Control Panel")
        
        # Draw motor status
        self.draw_motor_status(40, 60, status)
        
        # Draw system status
        self.draw_system_status(40, 300, status)
        
        # Draw control buttons
        self.draw_control_buttons(620, 430)
        
        # Draw matplotlib plots
        self.draw_matplotlib_plot(610, 40, 560, 340)
    
    def draw_panel(self, x, y, width, height, title):
        # Draw panel background
        pygame.draw.rect(self.screen, self.colors['panel'], (x, y, width, height), border_radius=10)
        pygame.draw.rect(self.screen, self.colors['accent'], (x, y, width, 40), border_radius=10)
        
        # Draw title
        title_text = self.fonts['medium'].render(title, True, self.colors['text'])
        self.screen.blit(title_text, (x + 20, y + 10))
    
    def draw_motor_status(self, x, y, status):
        motors = status['motors']
        
        # Left motor
        self.draw_text(f"Left Motor:", x, y, self.fonts['medium'])
        self.draw_text(f"Speed: {motors['left']['speed']}/255", x, y + 40, self.fonts['small'])
        self.draw_text(f"Target: {motors['left']['target']}/255", x, y + 70, self.fonts['small'])
        self.draw_text(f"Direction: {motors['left']['direction']}", x, y + 100, self.fonts['small'])
        self.draw_text(f"Pulses: {motors['left']['pulses']}", x, y + 130, self.fonts['small'])
        
        # Right motor
        self.draw_text(f"Right Motor:", x, y + 200, self.fonts['medium'])
        self.draw_text(f"Speed: {motors['right']['speed']}/255", x, y + 240, self.fonts['small'])
        self.draw_text(f"Target: {motors['right']['target']}/255", x, y + 270, self.fonts['small'])
        self.draw_text(f"Direction: {motors['right']['direction']}", x, y + 300, self.fonts['small'])
        self.draw_text(f"Pulses: {motors['right']['pulses']}", x, y + 330, self.fonts['small'])
        
        # Draw speed bars
        self.draw_speed_bar(x + 200, y + 40, motors['left']['speed'], self.colors['left_motor'])
        self.draw_speed_bar(x + 200, y + 240, motors['right']['speed'], self.colors['right_motor'])
    
    def draw_system_status(self, x, y, status):
        system = status['system']
        
        self.draw_text("System Status:", x, y, self.fonts['medium'])
        
        emergency_color = self.colors['emergency'] if system['emergency_stop'] else self.colors['success']
        braking_color = self.colors['accent'] if system['braking'] else self.colors['text']
        ros_color = self.colors['success'] if system['ros_connected'] else self.colors['text']
        
        self.draw_text(f"Emergency Stop: {'ACTIVE' if system['emergency_stop'] else 'INACTIVE'}", 
                      x, y + 40, self.fonts['small'], emergency_color)
        self.draw_text(f"Braking: {'ACTIVE' if system['braking'] else 'INACTIVE'}", 
                      x, y + 70, self.fonts['small'], braking_color)
        self.draw_text(f"ROS Connected: {'YES' if system['ros_connected'] else 'NO'}", 
                      x, y + 100, self.fonts['small'], ros_color)
        self.draw_text(f"Last Update: {status['timestamp'].strftime('%H:%M:%S')}", 
                      x, y + 130, self.fonts['small'])
    
    def draw_control_buttons(self, x, y):
        button_width = 120
        button_height = 40
        button_spacing = 20
        
        buttons = [
            ("Forward", self.motor_controller.set_direction, ["left", "FORWARD"]),
            ("Reverse", self.motor_controller.set_direction, ["left", "REVERSE"]),
            ("Stop", self.motor_controller.stop_motors, []),
            ("Emergency", self.motor_controller.emergency_stop, []),
            ("Clear", self.motor_controller.clear_emergency, []),
            ("Soft Brake", self.motor_controller.activate_soft_brake, []),
            ("Hard Brake", self.motor_controller.activate_hard_brake, [])
        ]
        
        for i, (text, command, args) in enumerate(buttons):
            btn_x = x + (i % 3) * (button_width + button_spacing)
            btn_y = y + (i // 3) * (button_height + button_spacing)
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()
            
            # Check if mouse is over button
            if (btn_x <= mouse_pos[0] <= btn_x + button_width and 
                btn_y <= mouse_pos[1] <= btn_y + button_height):
                color = self.colors['accent']
                if mouse_click[0]:  # Left click
                    command(*args)
            else:
                color = self.colors['panel']
            
            # Draw button
            pygame.draw.rect(self.screen, color, (btn_x, btn_y, button_width, button_height), border_radius=5)
            text_surf = self.fonts['small'].render(text, True, self.colors['text'])
            self.screen.blit(text_surf, (btn_x + 10, btn_y + 10))
    
    def draw_speed_bar(self, x, y, speed, color):
        max_width = 200
        height = 20
        width = (speed / 255) * max_width
        
        # Draw background
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, max_width, height))
        # Draw filled portion
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        # Draw border
        pygame.draw.rect(self.screen, self.colors['text'], (x, y, max_width, height), 1)
        # Draw text
        speed_text = self.fonts['small'].render(f"{speed}", True, self.colors['text'])
        self.screen.blit(speed_text, (x + max_width + 10, y))
    
    def draw_text(self, text, x, y, font, color=None):
        if color is None:
            color = self.colors['text']
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
    
    def draw_matplotlib_plot(self, x, y, width, height):
        # Convert matplotlib figure to pygame surface
        buf = self.canvas.buffer_rgba()
        plot_surface = pygame.image.frombuffer(buf, self.canvas.get_width_height(), 'RGBA')
        # Scale and draw
        scaled_surface = pygame.transform.smoothscale(plot_surface, (width, height))
        self.screen.blit(scaled_surface, (x, y))