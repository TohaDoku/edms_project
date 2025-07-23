from datetime import datetime

def generate_document_number():
    return f"ВХ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def auto_categorize(title, content):
    keywords = {
        "договор": "Договорные документы",
        "жалоба": "Жалобы",
        "смета": "Финансовые документы",
        "приказ": "Распорядительные",
        "заявление": "Заявления",
    }
    for word, category in keywords.items():
        if word in (title + content).lower():
            return category
    return "Прочее"

def generate_outgoing_number():
    return f"ИСХ-{datetime.now().strftime('%Y%m%d%H%M%S')}"