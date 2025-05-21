def safe_float(text):
    try:
        return float(text.replace(",", "."))
    except:
        return 5.0
