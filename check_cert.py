import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Loading variables from .env
load_dotenv()

PARTICIPANT_NUMBER = os.getenv("PARTICIPANT_NUMBER")
DATE_OF_BIRTH = os.getenv("DATE_OF_BIRTH")
DATE_OF_ISSUE = os.getenv("DATE_OF_ISSUE")


def check_cert() -> str:
    if not PARTICIPANT_NUMBER or not DATE_OF_BIRTH or not DATE_OF_ISSUE:
        return "❌ Not all environment variables found. Check .env file."

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://results.telc.net/")

        page.get_by_label("Teilnehmernummer").fill(PARTICIPANT_NUMBER)
        page.get_by_label("Geburtsdatum").fill(DATE_OF_BIRTH)
        page.get_by_label("Datum der Ausstellung").fill(DATE_OF_ISSUE)

        try:
            # Let's try to click on the button by its name (if the text is available)
            page.get_by_role("button", name="Zertifikat suchen").click()
        except:
            # If it doesn't work, use the icon locator
            page.locator('button:has(svg.fa-magnifying-glass)').click()

        page.wait_for_timeout(2000)  # Let's wait a bit for the page to refresh

        content = page.content()

        if "Dieses Zertifikat konnte nicht gefunden werden." in content:
            print("❌ Certificate not found!")
        elif "Hier können Sie die Ergebnisse des Ihnen vorliegenden telc Zertifikats verifizieren." in content:
            print("✅ Certificate found!")
        else:
            print("⚠️ Parsing error")

        browser.close()
