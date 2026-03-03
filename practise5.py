import re
import json
from pathlib import Path

RAW_FILE = "raw.txt"

# --- helpers ---
def money_to_float(s: str) -> float:
    # "1 200,00" -> 1200.00
    s = s.replace(" ", "").replace("\u00a0", "")  # обычный и неразрывный пробел
    s = s.replace(",", ".")
    return float(s)

def find_first(regex, text, flags=0):
    m = re.search(regex, text, flags)
    return m.group(1) if m else None

def main():
    text = Path(RAW_FILE).read_text(encoding="utf-8", errors="ignore")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    dt_str = find_first(r"Время:\s*(\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}:\d{2})", text)

    payment_method = 0
    if re.search(r"Банковская карта\s*:", text):
        payment_method = "Банковская карта"
    elif re.search(r"Наличные\s*:", text, re.I):
        payment_method = "Наличные"

    total_str = 0

    for i, ln in enumerate(lines):
        if re.fullmatch(r"ИТОГО\s*:", ln):
            if i + 1 < len(lines):
                total_str = lines[i + 1]
            break
    total = money_to_float(total_str) if total_str and re.search(r"\d", total_str) else None

    items = []
    i = 0
    qty_price_re = re.compile(r"^\s*([\d.,]+)\s*x\s*([\d\s]+,\d{2})\s*$", re.I)
    money_line_re = re.compile(r"^\s*([\d\s]+,\d{2})\s*$")

    while i < len(lines):
        if re.fullmatch(r"\d+\.", lines[i]):
 
            name = lines[i + 1] if i + 1 < len(lines) else ""
            qty = None
            unit_price = None
            line_total = None

            if i + 2 < len(lines):
                m = qty_price_re.match(lines[i + 2])
                if m:
                    qty = float(m.group(1).replace(",", "."))  # "2,000" -> 2.000
                    unit_price = money_to_float(m.group(2))

            if i + 3 < len(lines):
                m2 = money_line_re.match(lines[i + 3])
                if m2:
                    line_total = money_to_float(m2.group(1))

            items.append({
                "name": name,
                "qty": qty,
                "unit_price": unit_price,
                "line_total": line_total
            })

            i += 1
        i += 1

    all_prices_str = re.findall(r"\b\d{1,3}(?:[ \u00a0]\d{3})*,\d{2}\b", text)
    all_prices = [money_to_float(x) for x in all_prices_str]

    computed_total = sum(it["line_total"] for it in items if isinstance(it.get("line_total"), (int, float)))

    output = {
        "datetime": dt_str,
        "payment_method": payment_method,
        "total": total,
        "computed_total": round(computed_total, 2),
        "items": items,
        "all_prices": all_prices,
        "product_names": [it["name"] for it in items],
    }

    print(json.dumps(output, ensure_ascii=False, separators=(",", ":"), indent=2))


if __name__ == "__main__":
    main()