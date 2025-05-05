import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import config
from logger import log_event, log_error

class OverlayApp:
    def __init__(self):
        """Initialize the overlay window and UI elements"""
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.load_background()
        
    def setup_window(self):
        """Configure the main window properties"""
        try:
            # Set window properties
            self.root.title("Stock Analysis Overlay")
            self.root.geometry(f"{config.OVERLAY_WIDTH}x{config.OVERLAY_HEIGHT}+50+50")
            self.root.overrideredirect(True)  # Remove window decorations
            self.root.attributes("-topmost", True)  # Keep on top
            self.root.attributes("-alpha", config.OVERLAY_OPACITY)
            
            # Configure window background
            self.root.configure(bg=config.OVERLAY_BG_COLOR)
            
            # Bind escape key to close
            self.root.bind("<Escape>", lambda e: self.root.destroy())
            
            # Make window draggable
            self.root.bind("<Button-1>", self.start_move)
            self.root.bind("<B1-Motion>", self.do_move)
            
        except Exception as e:
            log_error(f"Failed to setup window: {str(e)}")
            
    def create_widgets(self):
        """Create and arrange UI widgets"""
        try:
            # Create main frame
            self.main_frame = tk.Frame(
                self.root,
                bg=config.OVERLAY_BG_COLOR
            )
            self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
            
            # Status header
            self.status_label = tk.Label(
                self.main_frame,
                text="Waiting for trigger...",
                font=config.TICKER_FONT,
                fg=config.TEXT_COLOR,
                bg=config.OVERLAY_BG_COLOR
            )
            self.status_label.pack(pady=(0, 10))
            
            # Ticker display
            self.ticker_frame = tk.Frame(
                self.main_frame,
                bg=config.OVERLAY_BG_COLOR
            )
            self.ticker_frame.pack(fill='x', pady=5)
            
            self.ticker_label = tk.Label(
                self.ticker_frame,
                text="",
                font=config.TICKER_FONT,
                fg=config.TEXT_COLOR,
                bg=config.OVERLAY_BG_COLOR
            )
            self.ticker_label.pack(side='left')
            
            # Recommendation display
            self.rec_frame = tk.Frame(
                self.main_frame,
                bg=config.OVERLAY_BG_COLOR
            )
            self.rec_frame.pack(fill='x', pady=5)
            
            self.rec_label = tk.Label(
                self.rec_frame,
                text="",
                font=config.RECOMMEND_FONT,
                fg=config.TEXT_COLOR,
                bg=config.OVERLAY_BG_COLOR
            )
            self.rec_label.pack(side='left')
            
            # Console/log display
            self.console_frame = tk.Frame(
                self.main_frame,
                bg=config.OVERLAY_BG_COLOR
            )
            self.console_frame.pack(fill='both', expand=True, pady=(10, 0))
            
            self.console = tk.Text(
                self.console_frame,
                height=8,
                width=40,
                font=config.LOG_FONT,
                bg="#2e2e2e",
                fg="lime",
                wrap=tk.WORD
            )
            self.console.pack(fill='both', expand=True)
            
            # Close button
            self.close_button = tk.Button(
                self.main_frame,
                text="×",
                font=("Arial", 16, "bold"),
                fg=config.TEXT_COLOR,
                bg=config.OVERLAY_BG_COLOR,
                bd=0,
                command=self.root.destroy
            )
            self.close_button.place(relx=1.0, rely=0, anchor="ne")
            
        except Exception as e:
            log_error(f"Failed to create widgets: {str(e)}")
            
    def load_background(self):
        """Load and set the background image from Pexels"""
        try:
            # Fetch background image
            response = requests.get(config.BG_IMAGE_URL)
            if response.status_code == 200:
                # Load and resize image
                img = Image.open(BytesIO(response.content))
                img = img.resize(
                    (config.OVERLAY_WIDTH, config.OVERLAY_HEIGHT),
                    Image.Resampling.LANCZOS
                )
                
                # Convert to PhotoImage
                self.bg_image = ImageTk.PhotoImage(img)
                
                # Create canvas for background
                self.bg_canvas = tk.Canvas(
                    self.root,
                    width=config.OVERLAY_WIDTH,
                    height=config.OVERLAY_HEIGHT,
                    highlightthickness=0
                )
                self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
                
                # Add image to canvas
                self.bg_canvas.create_image(
                    0, 0,
                    image=self.bg_image,
                    anchor="nw"
                )
                
                # Lower canvas to background
                self.bg_canvas.lower()
                
            else:
                log_error("Failed to fetch background image")
                
        except Exception as e:
            log_error(f"Failed to load background: {str(e)}")
            
    def start_move(self, event):
        """Begin window drag operation"""
        self.x = event.x
        self.y = event.y
        
    def do_move(self, event):
        """Handle window drag operation"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        
    def update_status(self, status):
        """Update the status display"""
        try:
            self.status_label.config(text=status)
            self.root.update_idletasks()
        except Exception as e:
            log_error(f"Failed to update status: {str(e)}")
            
    def update_ticker(self, ticker):
        """Update the ticker display"""
        try:
            self.ticker_label.config(text=ticker)
            self.root.update_idletasks()
        except Exception as e:
            log_error(f"Failed to update ticker: {str(e)}")
            
    def update_recommendation(self, rec, confidence):
        """Update the recommendation display"""
        try:
            # Set color based on recommendation
            color = {
                "BUY": config.SUCCESS_COLOR,
                "SELL": config.ERROR_COLOR,
                "HOLD": config.WARNING_COLOR
            }.get(rec, config.TEXT_COLOR)
            
            self.rec_label.config(
                text=f"{rec} ({confidence}% confidence)",
                fg=color
            )
            self.root.update_idletasks()
        except Exception as e:
            log_error(f"Failed to update recommendation: {str(e)}")
            
    def append_log(self, message):
        """Add a message to the console log"""
        try:
            self.console.insert(tk.END, f"{message}\n")
            self.console.see(tk.END)  # Scroll to bottom
            self.root.update_idletasks()
        except Exception as e:
            log_error(f"Failed to append log: {str(e)}")
            
    def run(self):
        """Start the overlay window"""
        try:
            self.root.mainloop()
        except Exception as e:
            log_error(f"Overlay window error: {str(e)}")
            
    def close(self):
        """Close the overlay window"""
        try:
            self.root.destroy()
        except Exception as e:
            log_error(f"Failed to close overlay: {str(e)}")
