from services.receipt import receipt_parser

def test_parse_receipt_basic():
    text = "Canteen Bill\nSamosa 20\nChai Rs 15\nTotal: Rs. 35"
    info = receipt_parser.parse(text)
    
    assert info.total == 35.0
    assert len(info.items) == 2
    assert info.items[0].name == "Samosa"
    assert info.items[0].amount == 20.0
    assert info.items[1].name == "Chai"
    assert info.items[1].amount == 15.0
    
    assert info.suggested_split["2"] == 17.5
    assert not info.estimated_total

def test_parse_receipt_estimated_total():
    text = "Vada Pav 30\nCold Drink 40"
    info = receipt_parser.parse(text)
    
    assert info.total == 70.0
    assert info.estimated_total is True
    assert len(info.items) == 2

def test_parse_receipt_tax_ignored_as_item():
    text = "Burger 100\nCGST 2.5\nSGST 2.5\nTotal 105"
    info = receipt_parser.parse(text)
    
    assert info.total == 105.0
    # Items might exclude CGST/SGST due to filter
    item_names = [i.name.lower() for i in info.items]
    assert "cgst" not in item_names
    assert "burger" in item_names
