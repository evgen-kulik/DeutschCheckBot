import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

PARTICIPANT_NUMBER = os.getenv("PARTICIPANT_NUMBER")
DATE_OF_BIRTH = os.getenv("DATE_OF_BIRTH")
DATE_OF_ISSUE = os.getenv("DATE_OF_ISSUE")


async def check_cert() -> str:
    if not PARTICIPANT_NUMBER or not DATE_OF_BIRTH or not DATE_OF_ISSUE:
        return "❌ Not all environment variables found. Check .env file."

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://results.telc.net/")

        await page.get_by_label("Teilnehmernummer").fill(PARTICIPANT_NUMBER)
        await page.get_by_label("Geburtsdatum").fill(DATE_OF_BIRTH)
        await page.get_by_label("Datum der Ausstellung").fill(DATE_OF_ISSUE)

        try:
            await page.get_by_role("button", name="Zertifikat suchen").click()
        except:
            await page.locator('button:has(svg.fa-magnifying-glass)').click()

        await page.wait_for_timeout(2000)
        content = await page.content()

        await browser.close()

        if "Dieses Zertifikat konnte nicht gefunden werden." in content:
            return "❌ Certificate not found!"
        elif "Hier können Sie die Ergebnisse des Ihnen vorliegenden telc Zertifikats verifizieren." in content:
            return "✅ Certificate found!"
        else:
            return "⚠️ Parsing error"
