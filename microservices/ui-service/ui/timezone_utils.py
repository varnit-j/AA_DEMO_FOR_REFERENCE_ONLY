"""
Timezone utility functions for converting UTC times to user's local timezone
"""
from datetime import datetime, timezone
import pytz

def convert_utc_to_local(date_string, target_timezone='Asia/Calcutta'):
    """
    Convert UTC datetime string to local timezone
    
    Args:
        date_string: UTC datetime string in various formats
        target_timezone: Target timezone (default: Asia/Calcutta)
    
    Returns:
        dict with converted times and debug info
    """
    try:
        print(f"[TIME_DEBUG] Converting date: {date_string}")
        
        # Parse the date string
        dt = None
        if len(date_string) == 16:  # Format: 2026-01-23 08:00
            dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        elif len(date_string) == 19:  # Format: 2026-01-23 08:00:00
            dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        elif 'T' in date_string:  # ISO format
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        else:
            # Try to parse as is
            dt = datetime.fromisoformat(date_string)
        
        # Assume UTC if no timezone info
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # Convert to target timezone
        target_tz = pytz.timezone(target_timezone)
        local_dt = dt.astimezone(target_tz)
        
        result = {
            'original': date_string,
            'utc': dt.strftime('%Y-%m-%d %H:%M:%S UTC'),
            'local': local_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'local_with_tz': local_dt.strftime('%Y-%m-%d %H:%M:%S IST'),
            'success': True
        }
        
        print(f"[TIME_DEBUG] Conversion successful: {result['local_with_tz']}")
        return result
        
    except Exception as e:
        print(f"[TIME_DEBUG] Error converting date {date_string}: {e}")
        return {
            'original': date_string,
            'utc': date_string + ' (UTC)',
            'local': date_string,
            'local_with_tz': date_string + ' (UTC)',
            'success': False,
            'error': str(e)
        }

def add_timezone_info_to_transactions(transactions):
    """
    Add timezone conversion info to transaction list
    
    Args:
        transactions: List of transaction dictionaries
    
    Returns:
        List of transactions with timezone info added
    """
    processed_transactions = []
    
    for transaction in transactions:
        processed_transaction = transaction.copy()
        
        # Convert date if present
        if 'date' in processed_transaction:
            time_info = convert_utc_to_local(processed_transaction['date'])
            processed_transaction['date'] = time_info['local']
            processed_transaction['date_local'] = time_info['local_with_tz']
            processed_transaction['date_utc'] = time_info['utc']
            processed_transaction['time_conversion_success'] = time_info['success']
        
        processed_transactions.append(processed_transaction)
    
    return processed_transactions