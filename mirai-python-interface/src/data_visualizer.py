import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import pygame.gfxdraw
from datetime import datetime
import threading
import time

class DataVisualizer:
    def __init__(self, motor_controller, width=1400, height=900):
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
            'success': (50, 255, 50),
            'warning': (255, 165, 0),
            'connected': (50, 200, 50),
            'disconnected': (200, 50, 50)
        }
        
        # Fonts
        self.fonts = {
            'title': pygame.font.SysFont('Arial', 36),
            'large': pygame.font.SysFont('Arial', 28),
            'medium': pygame.font.SysFont('Arial', 22),
            'small': pygame.font.SysFont('Arial', 16)
        }
        
        # UI Layout
        self.layout = {
            'padding': 20,
            'panel_spacing': 25,
            'button_spacing': 15,
            'status_height': 40
        }
    
    def setup_plots(self):
        # Create matplotlib figures for real-time plotting
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(10, 8))
        self.canvas = FigureCanvasAgg(self.fig)
        
        # Configure plots
        self.ax1.set_title('Motor Speeds', color='white', fontsize=12)
        self.ax1.set_ylabel('Speed', color='white')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.tick_params(colors='white')
        self.ax1.set_facecolor((0.1, 0.1, 0.1))
        
        self.ax2.set_title('Target vs Actual', color='white', fontsize=12)
        self.ax2.grid(True, alpha=0.3)
        self.ax2.tick_params(colors='white')
        self.ax2.set_facecolor((0.1, 0.1, 0.1))
        
        self.ax3.set_title('Pulse Counts', color='white', fontsize=12)
        self.ax3.set_ylabel('Pulses', color='white')
        self.ax3.grid(True, alpha=0.3)
        self.ax3.tick_params(colors='white')
        self.ax3.set_facecolor((0.1, 0.1, 0.1))
        
        self.ax4.set_title('System Status', color='white', fontsize=12)
        self.ax4.grid(True, alpha=0.3)
        self.ax4.tick_params(colors='white')
        self.ax4.set_facecolor((0.1, 0.1, 0.1))
        
        # Set dark background for all plots
        self.fig.patch.set_facecolor((0.15, 0.15, 0.2))
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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        # Toggle connection (placeholder for actual connection logic)
                        pass
            
            self.update_plots()
            self.render_dashboard()
            
            pygame.display.flip()
            clock.tick(30)  # 30 FPS
    
    def update_plots(self):
        history = self.motor_controller.get_history()
        
        if len(history['timestamp']) > 0:
            timestamps = history['timestamp'][-100:]  # Show only last 100 points
            
            # Update speed plot
            self.ax1.clear()
            self.ax1.plot(timestamps, history['left_speed'][-100:], 
                         label='Left Speed', color='red', linewidth=2)
            self.ax1.plot(timestamps, history['right_speed'][-100:], 
                         label='Right Speed', color='green', linewidth=2)
            self.ax1.set_title('Motor Speeds', color='white', fontsize=12)
            self.ax1.legend(facecolor=(0.2, 0.2, 0.2), edgecolor='white', labelcolor='white')
            self.ax1.grid(True, alpha=0.3)
            self.ax1.tick_params(colors='white')
            self.ax1.set_facecolor((0.1, 0.1, 0.1))
            
            # Update target vs actual plot
            self.ax2.clear()
            self.ax2.plot(timestamps, history['left_target'][-100:], 
                         label='Left Target', color='red', linestyle='--', linewidth=2)
            self.ax2.plot(timestamps, history['left_speed'][-100:], 
                         label='Left Actual', color='red', linewidth=2)
            self.ax2.plot(timestamps, history['right_target'][-100:], 
                         label='Right Target', color='green', linestyle='--', linewidth=2)
            self.ax2.plot(timestamps, history['right_speed'][-100:], 
                         label='Right Actual', color='green', linewidth=2)
            self.ax2.set_title('Target vs Actual Speeds', color='white', fontsize=12)
            self.ax2.legend(facecolor=(0.2, 0.2, 0.2), edgecolor='white', labelcolor='white')
            self.ax2.grid(True, alpha=0.3)
            self.ax2.tick_params(colors='white')
            self.ax2.set_facecolor((0.1, 0.1, 0.1))
            
            # Update pulse count plot
            self.ax3.clear()
            self.ax3.plot(timestamps, history['left_pulses'][-100:], 
                         label='Left Pulses', color='red', linewidth=2)
            self.ax3.plot(timestamps, history['right_pulses'][-100:], 
                         label='Right Pulses', color='green', linewidth=2)
            self.ax3.set_title('Hall Sensor Pulse Counts', color='white', fontsize=12)
            self.ax3.legend(facecolor=(0.2, 0.2, 0.2), edgecolor='white', labelcolor='white')
            self.ax3.grid(True, alpha=0.3)
            self.ax3.tick_params(colors='white')
            self.ax3.set_facecolor((0.1, 0.1, 0.1))
            
            # Update system status
            self.ax4.clear()
            status = self.motor_controller.get_status()
            system_vars = [
                status['system']['emergency_stop'],
                status['system']['braking'],
                status['system']['ros_connected'],
                status['system'].get('serial_connected', False)
            ]
            colors = ['red', 'orange', 'blue', 'green']
            bars = self.ax4.bar(['Emergency', 'Braking', 'ROS', 'Serial'], 
                               system_vars, color=colors, alpha=0.7)
            self.ax4.set_title('System Status', color='white', fontsize=12)
            self.ax4.set_ylim(0, 1)
            self.ax4.grid(True, alpha=0.3)
            self.ax4.tick_params(colors='white')
            self.ax4.set_facecolor((0.1, 0.1, 0.1))
            
            # Draw the canvas
            self.canvas.draw()
            self.canvas.flush_events()
    
    def render_dashboard(self):
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Get current status
        status = self.motor_controller.get_status()
        
        # Draw status bar at top
        self.draw_status_bar()
        
        # Calculate panel dimensions with better spacing
        panel_width = (self.width - 3 * self.layout['panel_spacing']) // 2
        left_panel_x = self.layout['padding']
        right_panel_x = left_panel_x + panel_width + self.layout['panel_spacing']
        panel_y = self.layout['padding'] + self.layout['status_height'] + self.layout['panel_spacing']
        panel_height = (self.height - panel_y - 2 * self.layout['padding']) // 2
        
        # Draw panels with improved layout
        self.draw_panel(left_panel_x, panel_y, panel_width, panel_height, "Motor Status")
        self.draw_panel(right_panel_x, panel_y, panel_width, panel_height, "Real-time Plots")
        self.draw_panel(left_panel_x, panel_y + panel_height + self.layout['panel_spacing'], 
                       panel_width, panel_height, "System Status")
        self.draw_panel(right_panel_x, panel_y + panel_height + self.layout['panel_spacing'], 
                       panel_width, panel_height, "Control Panel")
        
        # Draw content in panels
        self.draw_motor_status(left_panel_x + 20, panel_y + 50, status)
        self.draw_system_status(left_panel_x + 20, panel_y + panel_height + self.layout['panel_spacing'] + 50, status)
        self.draw_control_buttons(right_panel_x + 20, panel_y + panel_height + self.layout['panel_spacing'] + 50)
        self.draw_matplotlib_plot(right_panel_x + 10, panel_y + 40, panel_width - 20, panel_height - 50)
    
    def draw_status_bar(self):
        # Draw status bar at top of screen
        status_bar_rect = pygame.Rect(0, 0, self.width, self.layout['status_height'])
        pygame.draw.rect(self.screen, self.colors['panel'], status_bar_rect)
        
        # Get connection status
        status = self.motor_controller.get_status()
        serial_connected = status['system'].get('serial_connected', False)
        
        # Draw connection status
        connection_text = "Serial: " + ("CONNECTED" if serial_connected else "DISCONNECTED")
        connection_color = self.colors['connected'] if serial_connected else self.colors['disconnected']
        
        connection_surf = self.fonts['medium'].render(connection_text, True, connection_color)
        self.screen.blit(connection_surf, (20, 10))
        
        # Draw timestamp
        time_text = f"Last Update: {status['timestamp'].strftime('%H:%M:%S')}"
        time_surf = self.fonts['small'].render(time_text, True, self.colors['text'])
        self.screen.blit(time_surf, (self.width - time_surf.get_width() - 20, 12))
        
        # Draw title
        title_text = "MIRAI Motor Control Dashboard"
        title_surf = self.fonts['title'].render(title_text, True, self.colors['accent'])
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 5))
    
    def draw_panel(self, x, y, width, height, title):
        # Draw panel background with rounded corners
        pygame.draw.rect(self.screen, self.colors['panel'], (x, y, width, height), border_radius=12)
        
        # Draw panel header
        header_rect = pygame.Rect(x, y, width, 40)
        pygame.draw.rect(self.screen, self.colors['accent'], header_rect, border_radius=12)
        
        # Draw title
        title_text = self.fonts['medium'].render(title, True, self.colors['text'])
        self.screen.blit(title_text, (x + 15, y + 10))
    
    def draw_motor_status(self, x, y, status):
        motors = status['motors']
        
        # Left motor section
        self.draw_text("LEFT MOTOR", x, y, self.fonts['medium'], self.colors['left_motor'])
        self.draw_text(f"Speed: {motors['left']['speed']}/255", x, y + 35, self.fonts['small'])
        self.draw_text(f"Target: {motors['left']['target']}/255", x, y + 60, self.fonts['small'])
        self.draw_text(f"Direction: {motors['left']['direction']}", x, y + 85, self.fonts['small'])
        self.draw_text(f"Pulses: {motors['left']['pulses']}", x, y + 110, self.fonts['small'])
        
        # Right motor section
        self.draw_text("RIGHT MOTOR", x, y + 150, self.fonts['medium'], self.colors['right_motor'])
        self.draw_text(f"Speed: {motors['right']['speed']}/255", x, y + 185, self.fonts['small'])
        self.draw_text(f"Target: {motors['right']['target']}/255", x, y + 210, self.fonts['small'])
        self.draw_text(f"Direction: {motors['right']['direction']}", x, y + 235, self.fonts['small'])
        self.draw_text(f"Pulses: {motors['right']['pulses']}", x, y + 260, self.fonts['small'])
        
        # Draw speed bars with better spacing
        self.draw_speed_bar(x + 180, y + 35, motors['left']['speed'], self.colors['left_motor'])
        self.draw_speed_bar(x + 180, y + 185, motors['right']['speed'], self.colors['right_motor'])
    
    def draw_system_status(self, x, y, status):
        system = status['system']
        
        self.draw_text("SYSTEM STATUS", x, y, self.fonts['medium'], self.colors['accent'])
        
        # Connection status
        serial_connected = system.get('serial_connected', False)
        connection_color = self.colors['connected'] if serial_connected else self.colors['disconnected']
        self.draw_text(f"Serial: {'CONNECTED' if serial_connected else 'DISCONNECTED'}", 
                      x, y + 35, self.fonts['small'], connection_color)
        
        # Other status indicators
        emergency_color = self.colors['emergency'] if system['emergency_stop'] else self.colors['success']
        braking_color = self.colors['warning'] if system['braking'] else self.colors['text']
        ros_color = self.colors['connected'] if system['ros_connected'] else self.colors['disconnected']
        
        self.draw_text(f"Emergency: {'ACTIVE' if system['emergency_stop'] else 'INACTIVE'}", 
                      x, y + 65, self.fonts['small'], emergency_color)
        self.draw_text(f"Braking: {'ACTIVE' if system['braking'] else 'INACTIVE'}", 
                      x, y + 90, self.fonts['small'], braking_color)
        self.draw_text(f"ROS: {'CONNECTED' if system['ros_connected'] else 'DISCONNECTED'}", 
                      x, y + 115, self.fonts['small'], ros_color)
        
        # Performance metrics
        if len(status.get('performance', {})) > 0:
            self.draw_text(f"Update Rate: {status['performance'].get('update_rate', 0):.1f} Hz", 
                          x, y + 145, self.fonts['small'])
            self.draw_text(f"Loop Time: {status['performance'].get('loop_time', 0):.1f} ms", 
                          x, y + 170, self.fonts['small'])
    
    def draw_control_buttons(self, x, y):
        button_width = 140
        button_height = 45
        button_spacing = 15
        
        # Group buttons logically
        control_groups = [
            [
                ("⏩ Forward", self.motor_controller.set_direction, ["left", "FORWARD"]),
                ("⏪ Reverse", self.motor_controller.set_direction, ["left", "REVERSE"]),
                ("⏹ Stop", self.motor_controller.stop_motors, [])
            ],
            [
                ("🚨 Emergency", self.motor_controller.emergency_stop, []),
                ("✅ Clear", self.motor_controller.clear_emergency, []),
                ("🔧 Settings", self.open_settings, [])
            ],
            [
                ("🔄 Soft Brake", self.motor_controller.activate_soft_brake, []),
                ("⚡ Hard Brake", self.motor_controller.activate_hard_brake, []),
                ("📊 Diagnostics", self.motor_controller.print_diagnostics, [])
            ]
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for group_idx, group in enumerate(control_groups):
            for btn_idx, (text, command, args) in enumerate(group):
                btn_x = x + group_idx * (button_width + button_spacing)
                btn_y = y + btn_idx * (button_height + button_spacing)
                
                # Check if mouse is over button
                mouse_over = (btn_x <= mouse_pos[0] <= btn_x + button_width and 
                             btn_y <= mouse_pos[1] <= btn_y + button_height)
                
                # Draw button with hover effect
                btn_color = self.colors['accent'] if mouse_over else self.colors['panel']
                pygame.draw.rect(self.screen, btn_color, (btn_x, btn_y, button_width, button_height), 
                               border_radius=8)
                
                # Draw button text
                text_surf = self.fonts['small'].render(text, True, self.colors['text'])
                self.screen.blit(text_surf, (btn_x + 10, btn_y + 12))
                
                # Handle click
                if mouse_over and pygame.mouse.get_pressed()[0]:
                    pygame.time.delay(200)  # Debounce
                    command(*args)
    
    def open_settings(self):
        # Placeholder for settings dialog
        print("Settings dialog would open here")
        # This could open a modal dialog for changing serial port, baud rate, etc.
    
    def draw_speed_bar(self, x, y, speed, color):
        max_width = 200
        height = 20
        
        # Calculate width based on speed (0-255)
        width = max(5, (speed / 255) * max_width)  # Minimum 5px width for visibility
        
        # Draw background
        pygame.draw.rect(self.screen, (60, 60, 70), (x, y, max_width, height), border_radius=3)
        # Draw filled portion
        pygame.draw.rect(self.screen, color, (x, y, width, height), border_radius=3)
        # Draw border
        pygame.draw.rect(self.screen, self.colors['text'], (x, y, max_width, height), 1, border_radius=3)
        # Draw text
        speed_text = self.fonts['small'].render(f"{speed}/255", True, self.colors['text'])
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