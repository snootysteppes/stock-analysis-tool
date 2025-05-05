import yfinance as yf
import requests
from datetime import datetime, timedelta
import json
from logger import log_event, log_error, log_warning
import config

# Keywords for sentiment analysis
POSITIVE_KEYWORDS = {
    'buy', 'bullish', 'upgrade', 'growth', 'profit', 'gain', 'positive',
    'surge', 'jump', 'rise', 'up', 'higher', 'strong', 'success', 'beat',
    'exceed', 'outperform', 'record'
}

NEGATIVE_KEYWORDS = {
    'sell', 'bearish', 'downgrade', 'loss', 'negative', 'decline', 'drop',
    'fall', 'down', 'lower', 'weak', 'fail', 'miss', 'underperform',
    'bankruptcy', 'debt', 'risk'
}

def fetch_stock_data(ticker):
    """
    Fetch recent stock data using yfinance.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Stock data including price and trend information
    """
    try:
        log_event(f"Fetching stock data for {ticker}...")
        
        # Get stock info
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        
        if hist.empty:
            raise ValueError(f"No data found for ticker {ticker}")
            
        # Calculate basic metrics
        current_price = hist['Close'][-1]
        prev_close = hist['Close'][-2] if len(hist) > 1 else current_price
        price_change = ((current_price - prev_close) / prev_close) * 100
        
        # Calculate 5-day trend
        trend = (hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0] * 100
        
        # Calculate volume trend
        avg_volume = hist['Volume'].mean()
        latest_volume = hist['Volume'][-1]
        volume_trend = ((latest_volume - avg_volume) / avg_volume) * 100
        
        return {
            'price': current_price,
            'price_change': price_change,
            'trend': trend,
            'volume': latest_volume,
            'volume_trend': volume_trend
        }
        
    except Exception as e:
        log_error(f"Failed to fetch stock data: {str(e)}")
        return None

def fetch_news(ticker):
    """
    Fetch recent news articles about the stock.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        list: List of news headlines
    """
    try:
        log_event(f"Fetching news for {ticker}...")
        headlines = []
        
        # Try yfinance news first
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if news:
            headlines.extend([item['title'] for item in news[:5]])
        
        # If NewsAPI key is configured, use it as backup
        if not headlines and config.NEWS_API_KEY:
            url = (
                f"https://newsapi.org/v2/everything?"
                f"q={ticker}+stock&"
                f"apiKey={config.NEWS_API_KEY}&"
                f"sortBy=publishedAt&"
                f"language=en&"
                f"pageSize=5"
            )
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('articles'):
                    headlines.extend([
                        article['title'] for article in data['articles']
                    ])
        
        if not headlines:
            log_warning(f"No news found for {ticker}")
            
        return headlines
        
    except Exception as e:
        log_error(f"Failed to fetch news: {str(e)}")
        return []

def analyze_sentiment(headlines):
    """
    Analyze sentiment of news headlines.
    
    Args:
        headlines (list): List of news headlines
        
    Returns:
        tuple: (sentiment_score, sentiment_label)
    """
    try:
        if not headlines:
            return 0, "Neutral"
            
        total_score = 0
        for headline in headlines:
            headline = headline.lower()
            
            # Count positive and negative words
            pos_count = sum(1 for word in POSITIVE_KEYWORDS if word in headline)
            neg_count = sum(1 for word in NEGATIVE_KEYWORDS if word in headline)
            
            # Calculate headline score
            score = pos_count - neg_count
            total_score += score
            
        # Normalize score to range [-100, 100]
        max_possible = max(len(headlines) * 3, 1)  # assume max 3 keywords per headline
        normalized_score = (total_score / max_possible) * 100
        
        # Determine sentiment label
        if normalized_score > 20:
            label = "Positive"
        elif normalized_score < -20:
            label = "Negative"
        else:
            label = "Neutral"
            
        return normalized_score, label
        
    except Exception as e:
        log_error(f"Sentiment analysis failed: {str(e)}")
        return 0, "Neutral"

def make_recommendation(stock_data, sentiment_score):
    """
    Generate trading recommendation based on stock data and sentiment.
    
    Args:
        stock_data (dict): Stock price and trend data
        sentiment_score (float): News sentiment score
        
    Returns:
        tuple: (recommendation, confidence)
    """
    try:
        if not stock_data:
            return "HOLD", 50
            
        # Initialize base confidence
        confidence = 50
        
        # Analyze price trend
        trend_signal = "NEUTRAL"
        if stock_data['trend'] > 2:  # 2% up
            trend_signal = "BUY"
            confidence += 10
        elif stock_data['trend'] < -2:  # 2% down
            trend_signal = "SELL"
            confidence += 10
            
        # Factor in volume
        if stock_data['volume_trend'] > 20:  # 20% above average
            confidence += 10
            
        # Consider sentiment
        sentiment_signal = "NEUTRAL"
        if sentiment_score > 20:
            sentiment_signal = "BUY"
            confidence += 15
        elif sentiment_score < -20:
            sentiment_signal = "SELL"
            confidence += 15
            
        # Make final recommendation
        if trend_signal == sentiment_signal == "BUY":
            return "BUY", min(confidence + 15, 100)
        elif trend_signal == sentiment_signal == "SELL":
            return "SELL", min(confidence + 15, 100)
        elif trend_signal == "BUY" and sentiment_signal != "SELL":
            return "BUY", confidence
        elif trend_signal == "SELL" and sentiment_signal != "BUY":
            return "SELL", confidence
        else:
            return "HOLD", max(confidence - 10, 50)
            
    except Exception as e:
        log_error(f"Recommendation generation failed: {str(e)}")
        return "HOLD", 50

def analyze_stock(ticker):
    """
    Main function to analyze a stock and generate recommendations.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Analysis results including recommendation and metadata
    """
    try:
        log_event(f"Starting analysis for {ticker}...")
        
        # Initialize result structure
        result = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'recommendation': 'HOLD',
            'confidence': 50,
            'sentiment': 'Neutral',
            'price_data': None,
            'metadata': {}
        }
        
        # Fetch stock data
        stock_data = fetch_stock_data(ticker)
        if stock_data:
            result['price_data'] = stock_data
            
        # Fetch and analyze news
        headlines = fetch_news(ticker)
        sentiment_score, sentiment_label = analyze_sentiment(headlines)
        result['sentiment'] = sentiment_label
        
        # Generate recommendation
        rec, conf = make_recommendation(stock_data, sentiment_score)
        result['recommendation'] = rec
        result['confidence'] = conf
        
        # Add metadata
        result['metadata'] = {
            'news_count': len(headlines),
            'sentiment_score': sentiment_score,
            'price_trend': stock_data['trend'] if stock_data else None,
            'volume_trend': stock_data['volume_trend'] if stock_data else None
        }
        
        log_event(
            f"Analysis complete: {ticker} - {rec} ({conf}% confidence)"
        )
        return result
        
    except Exception as e:
        log_error(f"Stock analysis failed: {str(e)}")
        return {
            'ticker': ticker,
            'recommendation': 'HOLD',
            'confidence': 50,
            'sentiment': 'Neutral',
            'error': str(e)
        }
