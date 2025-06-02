from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

PARTICIPANT_NUMBER = os.getenv("PARTICIPANT_NUMBER")
DATE_OF_BIRTH = os.getenv("DATE_OF_BIRTH")


async def check_cert() -> str:
    """
    Checks for the existence of a telc certificate by trying all issue dates
    from today up to 30 days in the past. Uses a single browser session
    for performance.

    Returns:
        str: A message indicating whether the certificate was found or not.
    """
    if not PARTICIPANT_NUMBER or not DATE_OF_BIRTH:
        logger.warning("Missing environment variables.")
        return "❌ Required environment variables are missing. Please check your .env file."

    today = datetime.today()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        await page.goto("https://results.telc.net/")

        # Fill in static fields: participant number and date of birth
        await page.get_by_label("Teilnehmernummer").fill(PARTICIPANT_NUMBER)
        await page.get_by_label("Geburtsdatum").fill(DATE_OF_BIRTH)

        # Try all issue dates from today to 30 days ago
        for offset in range(0, 31):
            issue_date = (today - timedelta(days=offset)).strftime("%d.%m.%Y")
            logger.info(f"Trying issue date: {issue_date}")

            try:
                # Fill in the issue date
                await page.get_by_label("Datum der Ausstellung").fill(issue_date)

                # Click the search button (primary or fallback)
                try:
                    await page.get_by_role("button", name="Zertifikat suchen").click()
                except:
                    logger.warning("Primary search button not found. Trying fallback.")
                    await page.locator('button:has(svg.fa-magnifying-glass)').click()

                # Wait up to 3 seconds for the "not found" message to appear
                try:
                    await page.wait_for_selector(
                        "text=Dieses Zertifikat konnte nicht gefunden werden.",
                        timeout=3000
                    )
                    # Not found — continue to next date
                    continue
                except:
                    # If "not found" message does not appear, assume it's found
                    await browser.close()
                    return f"✅ Certificate found! (Issue date: {issue_date})"

            except Exception as e:
                logger.exception(f"Error checking for date {issue_date}")
                continue

        await browser.close()
        return "❌ Certificate not found in the last 30 days."
