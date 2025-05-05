import cv2
import numpy as np
from logger import log_event, log_error

def detect_lines(image):
    """
    Detect lines in the image using Hough transform.
    
    Args:
        image (numpy.ndarray): Input image
        
    Returns:
        numpy.ndarray: Detected lines
    """
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using HoughLinesP
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=100,
            minLineLength=100,
            maxLineGap=10
        )
        
        return lines
        
    except Exception as e:
        log_error(f"Line detection failed: {str(e)}")
        return None

def analyze_line_pattern(lines):
    """
    Analyze detected lines to determine if they form a chart pattern.
    
    Args:
        lines (numpy.ndarray): Detected lines
        
    Returns:
        tuple: (is_chart, confidence)
    """
    try:
        if lines is None or len(lines) < 5:
            return False, 0
            
        # Calculate line angles
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            angles.append(angle)
            
        # Convert angles to numpy array
        angles = np.array(angles)
        
        # Count horizontal-ish (-30 to 30 degrees) and vertical-ish (60 to 120 degrees) lines
        horizontal = np.sum((angles >= -30) & (angles <= 30))
        vertical = np.sum((angles >= 60) & (angles <= 120))
        
        # Calculate confidence based on line distribution
        total_lines = len(lines)
        horiz_ratio = horizontal / total_lines
        vert_ratio = vertical / total_lines
        
        # Chart patterns typically have more horizontal than vertical lines
        if horiz_ratio > 0.6 and vert_ratio < 0.3:
            confidence = min(100, int(horiz_ratio * 100))
            return True, confidence
            
        return False, 0
        
    except Exception as e:
        log_error(f"Line pattern analysis failed: {str(e)}")
        return False, 0

def detect_grid_pattern(image):
    """
    Detect if the image contains a grid pattern typical of charts.
    
    Args:
        image (numpy.ndarray): Input image
        
    Returns:
        bool: True if grid pattern detected
    """
    try:
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )
        
        # Find contours
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_LIST,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Count rectangular contours
        rect_count = 0
        for contour in contours:
            # Approximate contour to polygon
            epsilon = 0.04 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            
            # Check if polygon has 4 vertices (rectangular)
            if len(approx) == 4:
                rect_count += 1
                
        # If we find multiple rectangles, likely a grid
        return rect_count > 5
        
    except Exception as e:
        log_error(f"Grid pattern detection failed: {str(e)}")
        return False

def detect_chart(image):
    """
    Main function to detect if an image contains a stock chart.
    
    Args:
        image (numpy.ndarray): Input image
        
    Returns:
        tuple: (is_chart, confidence, metadata)
    """
    try:
        log_event("Starting chart detection...")
        
        # Detect lines
        lines = detect_lines(image)
        if lines is None:
            return False, 0, {}
            
        # Analyze line patterns
        is_chart, confidence = analyze_line_pattern(lines)
        
        # Check for grid pattern
        has_grid = detect_grid_pattern(image)
        
        # Combine evidence
        metadata = {
            "num_lines": len(lines),
            "has_grid": has_grid,
            "line_confidence": confidence
        }
        
        # Adjust confidence based on grid presence
        if has_grid:
            confidence = min(100, confidence + 20)
            
        # Final decision
        if is_chart and confidence >= 60:
            log_event(f"Chart detected with {confidence}% confidence")
            return True, confidence, metadata
            
        log_event("No chart pattern detected")
        return False, confidence, metadata
        
    except Exception as e:
        log_error(f"Chart detection failed: {str(e)}")
        return False, 0, {}
