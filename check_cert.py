import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()
logger = logging.getLogger(__name__)

PARTICIPANT_NUMBER = os.getenv("PARTICIPANT_NUMBER")
DATE_OF_BIRTH = os.getenv("DATE_OF_BIRTH")


async def check_cert_with_date(issue_date: str) -> str:
    """
    Attempts to verify a certificate on the telc results website
    using a specific issue date.

    Args:
        issue_date (str): The date the certificate was issued, formatted as "dd.mm.yyyy".

    Returns:
        str: A message indicating whether the certificate was found,
             not found, or could not be interpreted.
    """
    logger.info(f"Checking certificate with issue date: {issue_date}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        await page.goto("https://results.telc.net/")

        await page.get_by_label("Teilnehmernummer").fill(PARTICIPANT_NUMBER)
        await page.get_by_label("Geburtsdatum").fill(DATE_OF_BIRTH)
        await page.get_by_label("Datum der Ausstellung").fill(issue_date)

        try:
            await page.get_by_role("button", name="Zertifikat suchen").click()
        except:
            logger.warning("Primary search button not found. Trying fallback button.")
            await page.locator('button:has(svg.fa-magnifying-glass)').click()

        await page.wait_for_timeout(2000)
        content = await page.content()
        await browser.close()

        if "Dieses Zertifikat konnte nicht gefunden werden." in content:
            return "not found"
        elif "Hier können Sie die Ergebnisse des Ihnen vorliegenden telc Zertifikats verifizieren." in content:
            return "✅ Certificate found!"
        else:
            return "⚠️ Unable to parse certificate status."


async def check_cert() -> str:
    """
    Checks for the existence of a certificate by attempting verification
    for today and each of the previous 30 days.

    Returns:
        str: A message indicating the result of the certificate search.
    """
    if not PARTICIPANT_NUMBER or not DATE_OF_BIRTH:
        logger.warning("Missing environment variables.")
        return "❌ Required environment variables are missing. Please check your .env file."

    today = datetime.today()
    for offset in range(0, 31):
        try_date = today - timedelta(days=offset)
        date_str = try_date.strftime("%d.%m.%Y")
        try:
            result = await check_cert_with_date(date_str)
            if result == "✅ Certificate found!":
                logger.info(f"Certificate found with issue date: {date_str}")
                return f"{result} (Issue date: {date_str})"
        except Exception as e:
            logger.exception(f"Error while checking with date {date_str}")

    logger.info("Certificate not found in the last 30 days.")
    return "❌ Certificate not found in the last 30 days."
