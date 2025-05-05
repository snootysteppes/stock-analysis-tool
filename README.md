# Stock Analysis Tool

A Python application that monitors the screen for stock tickers and charts, providing real-time analysis and recommendations.

## Features

- Screen monitoring and OCR for stock ticker detection
- Custom OCR implementation for uppercase letters and numbers
- Chart pattern recognition using computer vision
- Real-time stock data analysis using yfinance
- News sentiment analysis
- Modern, transparent overlay UI
- Live console logging
- Draggable overlay window
- Background image from Pexels

## Requirements

- Python 3.7+
- Required packages listed in requirements.txt
- Windows operating system (for screen capture functionality)

## Installation

1. Clone this repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. The overlay window will appear on your screen
3. Press CTRL key when you want to analyze a stock ticker or chart on your screen
4. The application will:
   - Capture the screen
   - Detect any stock tickers using OCR
   - Identify chart patterns
   - Fetch real-time stock data
   - Analyze news sentiment
   - Display results in the overlay window

5. Press ESC key to exit the application

## How It Works

### Screen Capture and OCR
- When CTRL is pressed, the application captures the current screen
- Custom OCR pipeline processes the image to detect stock tickers
- Focuses on 3-5 character uppercase patterns typical of stock symbols

### Chart Detection
- Analyzes captured image for line chart patterns
- Uses edge detection and line analysis
- Identifies typical stock chart characteristics

### Market Analysis
- Fetches real-time stock data using yfinance
- Retrieves recent news headlines
- Performs sentiment analysis on news
- Generates buy/sell recommendations with confidence levels

### Overlay Interface
- Transparent, always-on-top window
- Displays detected ticker, current status, and recommendations
- Includes live console logging
- Draggable window position
- Modern UI with semi-transparent background

## File Structure

- `main.py`: Main application entry point
- `config.py`: Configuration settings
- `logger.py`: Logging functionality
- `screenshot.py`: Screen capture handling
- `ocr.py`: Custom OCR implementation
- `chart_detection.py`: Chart pattern recognition
- `analysis.py`: Stock analysis and recommendations
- `overlay.py`: UI implementation
- `templates/`: Directory for OCR character templates

## Notes

- The application requires screen capture permissions
- For optimal OCR results, ensure clear visibility of stock tickers
- News API key (optional) can be configured in config.py
- The overlay window can be moved by clicking and dragging
- Console log shows detailed operation history

## Error Handling

The application includes comprehensive error handling:
- Screen capture failures
- OCR processing issues
- Network connectivity problems
- API rate limits
- Invalid stock symbols

## Performance

- Minimal CPU usage when idle
- Brief processing time for analysis (typically 1-2 seconds)
- Configurable trigger cooldown to prevent rapid-fire activation

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
