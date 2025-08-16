from playwright.sync_api import sync_playwright
import re
import time

BASE_URL = "https://withhive.com/notice/game/1952"

def extract_notices_from_page(page):
    page.wait_for_selector("#notice_list_ul li.row", timeout=10000)
    notices_data = []

    notices = page.query_selector_all("#notice_list_ul li.row")
    for notice in notices:
        title_elem = notice.query_selector("div.col:nth-child(2) a")
        date_elem = notice.query_selector("div.col:nth-child(3)")
        thumb_elem = notice.query_selector("div.col:nth-child(2) a span.thumb")

        title = title_elem.inner_text().strip()
        date = date_elem.inner_text().strip()

        # Extraire l'URL de l'image depuis le style
        style = thumb_elem.get_attribute("style") if thumb_elem else ""
        image_url = re.search(r'url\((.*?)\)', style).group(1) if style else None

        # Extraire l'ID depuis l'attribut onclick pour créer le lien
        onclick = title_elem.get_attribute("onclick") if title_elem else ""
        match = re.search(r'\$notice\.goDetailUrlView\((\d+)\)', onclick)
        detail_id = match.group(1) if match else None
        detail_link = f"{BASE_URL}/detail/{detail_id}" if detail_id else None

        notices_data.append({
            "title": title,
            "date": date,
            "image": image_url,
            "link": detail_link
        })

    return notices_data

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(BASE_URL)

        all_notices = []

        while True:
            notices = extract_notices_from_page(page)
            all_notices.extend(notices)

            # Vérifier s’il y a une page suivante
            next_btn = page.query_selector("div#paging_div a.btn_next:not(.no_hover)")
            if next_btn and "onclick" in next_btn.get_attribute("outerHTML"):
                next_btn.click()
                time.sleep(1)  # attendre que la page charge
            else:
                break

        # Affichage
        for notice in all_notices:
            print(f"Titre : {notice['title']}")
            print(f"Date : {notice['date']}")
            print(f"Image : {notice['image']}")
            print(f"Lien : {notice['link']}")
            print("-"*50)

        browser.close()

if __name__ == "__main__":
    main()
