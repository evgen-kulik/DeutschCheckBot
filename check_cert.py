import os
import logging
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
logger = logging.getLogger(__name__)

PARTICIPANT_NUMBER = os.getenv("PARTICIPANT_NUMBER")
DATE_OF_BIRTH = os.getenv("DATE_OF_BIRTH")
DATE_OF_ISSUE = os.getenv("DATE_OF_ISSUE")


async def check_certificate() -> str:
    if not PARTICIPANT_NUMBER or not DATE_OF_BIRTH or not DATE_OF_ISSUE:
        logger.warning("Missing environment variables.")
        return "❌ Required environment variables are missing. Please check your .env file."

    try:
        logger.info("Launching browser...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
            page = await browser.new_page()
            logger.info("Navigating to certificate verification page...")
            await page.goto("https://results.telc.net/")

            logger.info("Filling form fields...")
            await page.get_by_label("Teilnehmernummer").fill(PARTICIPANT_NUMBER)
            await page.get_by_label("Geburtsdatum").fill(DATE_OF_BIRTH)
            await page.get_by_label("Datum der Ausstellung").fill(DATE_OF_ISSUE)

            try:
                await page.get_by_role("button", name="Zertifikat suchen").click()
            except:
                logger.warning("Fallback: Clicking button with icon")
                await page.locator('button:has(svg.fa-magnifying-glass)').click()

            await page.wait_for_timeout(2000)
            content = await page.content()
            await browser.close()

            if "Dieses Zertifikat konnte nicht gefunden werden." in content:
                logger.info("Certificate not found.")
                return "❌ Certificate not found!"
            elif "Hier können Sie die Ergebnisse des Ihnen vorliegenden telc Zertifikats verifizieren." in content:
                logger.info("Certificate found.")
                return "✅ Certificate found!"
            else:
                logger.warning("Unexpected content format.")
                return "⚠️ Unable to parse certificate status."

    except Exception as e:
        logger.exception("Unexpected error during certificate check.")
        return "⚠️ An unexpected error occurred during the certificate check."
