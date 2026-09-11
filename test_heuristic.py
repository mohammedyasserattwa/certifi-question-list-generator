import re

def guess_next_image_url(last_url: str):
    match = re.search(r"^(.*?)(\d+)(\.[a-zA-Z0-9]+)$", last_url)
    if match:
        base, num_str, ext = match.groups()
        next_num = int(num_str) + 1
        # Pad with zeros if original had them
        next_num_str = str(next_num).zfill(len(num_str))
        return f"{base}{next_num_str}{ext}"
    return None

urls = [
    "http://example.com/image17.png",
    "http://example.com/image001.jpg",
    "http://example.com/fig-1.jpeg"
]

for u in urls:
    print(f"{u} -> {guess_next_image_url(u)}")
