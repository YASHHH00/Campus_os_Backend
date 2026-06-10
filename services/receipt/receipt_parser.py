import re
from core.models import ReceiptInfo, ReceiptItem
from core.logging import get_logger

logger = get_logger(__name__)

# Regex patterns for Indian receipts
TOTAL_PATTERNS = [
    r'(?:total|grand total|amount|net amount)[:\s]*[₹Rs\.]*\s*(\d+(?:\.\d{1,2})?)',
    r'[₹Rs\.]+\s*(\d+(?:\.\d{1,2})?)\s*(?:/-|only)',
]
ITEM_PATTERN = r'^(.+?)\s+(?:[₹Rs\.]+)?\s*(\d+(?:\.\d{1,2})?)\s*$'

def parse(text: str) -> ReceiptInfo:
    """
    Parse receipt text to find total, items, and suggested splits.
    """
    total = 0.0
    items = []
    lines = text.split('\n')
    
    # 1. Extract total
    for pattern in TOTAL_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                val = float(match.group(1))
                if val > total: # Often there are subtotals, grab the max
                    total = val
            except ValueError:
                pass

    # 2. Extract items
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(ITEM_PATTERN, line, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Filter out non-item lines that look like items
            if any(kw in name.lower() for kw in ['total', 'tax', 'cgst', 'sgst', 'discount', 'change', 'cash']):
                continue
                
            try:
                amt = float(match.group(2))
                if amt > 0:
                    items.append(ReceiptItem(name=name, amount=amt))
            except ValueError:
                pass

    # 3. Handle cases where total is not explicitly found
    estimated_total = False
    sum_items = sum(item.amount for item in items)
    
    if total == 0.0:
        if sum_items > 0:
            total = sum_items
            estimated_total = True
    else:
        # Validate sum of items ≈ total (±10% for tax/rounding)
        if items and sum_items > 0:
            if not (0.9 * total <= sum_items <= 1.1 * total):
                logger.warning(f"Receipt sum mismatch: items sum {sum_items} vs total {total}")

    # 4. Generate suggested splits
    suggested_split = {}
    if total > 0:
        for split_count in [2, 3, 4]:
            suggested_split[str(split_count)] = round(total / split_count, 2)

    return ReceiptInfo(
        total=total,
        currency="INR",
        items=items,
        suggested_split=suggested_split,
        estimated_total=estimated_total
    )
