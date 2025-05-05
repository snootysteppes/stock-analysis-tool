import threading
from pynput import keyboard
import time
import os

# Import our modules
import config
import screenshot
import ocr
import chart_detection
import analysis
from overlay import OverlayApp
import logger

class StockAnalyzer:
    def __init__(self):
        """Initialize the stock analyzer application"""
        self.running = False
        self.overlay = None
        self.keyboard_listener = None
        self.last_trigger_time = 0
        self.trigger_cooldown = 1.0  # Seconds between allowed triggers
        
    def setup(self):
        """Set up the application components"""
        try:
            # Create templates directory if it doesn't exist
            os.makedirs('templates', exist_ok=True)
            
            # Initialize OCR templates
            logger.log_event("Loading OCR templates...")
            self.templates = ocr.load_templates()
            
            # Create and configure overlay
            logger.log_event("Creating overlay window...")
            self.overlay = OverlayApp()
            logger.set_overlay(self.overlay)
            
            # Set up keyboard listener
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press
            )
            
            logger.log_event("Setup complete")
            return True
            
        except Exception as e:
            logger.log_error(f"Setup failed: {str(e)}")
            return False
            
    def on_key_press(self, key):
        """Handle keyboard events"""
        try:
            # Check if it's a CTRL key press
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                current_time = time.time()
                
                # Check cooldown
                if current_time - self.last_trigger_time < self.trigger_cooldown:
                    return
                    
                self.last_trigger_time = current_time
                self.process_screen()
                
            # Check for escape key to exit
            elif key == keyboard.Key.esc:
                self.stop()
                
        except Exception as e:
            logger.log_error(f"Key press handler error: {str(e)}")
            
    def process_screen(self):
        """Process the screen capture and run analysis"""
        try:
            # Update status
            self.overlay.update_status("Capturing screen...")
            
            # Capture screen
            img = screenshot.capture_screen()
            if img is None:
                logger.log_error("Screen capture failed")
                return
                
            # Look for chart patterns
            self.overlay.update_status("Detecting charts...")
            is_chart, confidence, metadata = chart_detection.detect_chart(img)
            
            if is_chart:
                logger.log_event(
                    f"Chart pattern detected ({confidence}% confidence)"
                )
                
            # Run OCR to find ticker
            self.overlay.update_status("Running OCR...")
            ticker = ocr.detect_ticker(img, self.templates)
            
            if not ticker:
                self.overlay.update_status("No ticker found")
                logger.log_event("OCR completed - no ticker found")
                return
                
            # Update overlay with detected ticker
            self.overlay.update_ticker(ticker)
            logger.log_event(f"Detected ticker: {ticker}")
            
            # Run market analysis
            self.overlay.update_status(f"Analyzing {ticker}...")
            result = analysis.analyze_stock(ticker)
            
            # Update overlay with results
            self.overlay.update_status("Analysis complete")
            self.overlay.update_ticker(
                f"{ticker} - ${result['price_data']['price']:.2f}" if result.get('price_data') else ticker
            )
            self.overlay.update_recommendation(
                result['recommendation'],
                result['confidence']
            )
            
            # Log analysis metadata
            logger.log_event(
                f"Analysis complete for {ticker}:"
                f" {result['recommendation']} ({result['confidence']}% confidence)"
            )
            if result.get('metadata'):
                logger.log_event(
                    f"Sentiment: {result['sentiment']}, "
                    f"News items: {result['metadata']['news_count']}"
                )
                
        except Exception as e:
            logger.log_error(f"Processing error: {str(e)}")
            self.overlay.update_status("Processing error")
            
    def run(self):
        """Start the application"""
        try:
            self.running = True
            
            # Start keyboard listener
            self.keyboard_listener.start()
            
            # Update initial status
            self.overlay.update_status("Ready - Press CTRL to analyze")
            logger.log_event("Application started - waiting for trigger")
            
            # Start overlay
            self.overlay.run()
            
        except Exception as e:
            logger.log_error(f"Runtime error: {str(e)}")
            
        finally:
            self.stop()
            
    def stop(self):
        """Stop the application"""
        try:
            self.running = False
            
            # Stop keyboard listener
            if self.keyboard_listener:
                self.keyboard_listener.stop()
                
            # Close overlay
            if self.overlay:
                self.overlay.close()
                
            logger.log_event("Application stopped")
            
        except Exception as e:
            logger.log_error(f"Shutdown error: {str(e)}")

def main():
    """Main entry point"""
    try:
        # Create and setup analyzer
        analyzer = StockAnalyzer()
        
        if analyzer.setup():
            # Run the application
            analyzer.run()
        else:
            logger.log_error("Failed to setup application")
            
    except Exception as e:
        logger.log_error(f"Application error: {str(e)}")
        
    finally:
        # Ensure everything is cleaned up
        if 'analyzer' in locals():
            analyzer.stop()

if __name__ == "__main__":
    main()
