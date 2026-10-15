import asyncio
import re
import pandas as pd

from playwright.async_api import async_playwright


all_companies = []

MAX_CONCURRENT_PAGES = 5
semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)


# ==========================================
# 1. جمع روابط الشركات من كافة صفحات دالاس
# ==========================================
async def get_all_dallas_company_links(context, max_pages=15):

    company_links = []

    for page_num in range(1, max_pages + 1):
        city_url = f"https://www.quicktransportsolutions.com/carrier/texas/dallas.php?page={page_num}"
        page = await context.new_page()

        try:
            print(f"🔍 Collecting links from Dallas Page {page_num}...")

            await page.goto(
                city_url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            links = page.locator('a[href*="/truckingcompany/texas/"]')
            count = await links.count()

            # التوقف فور الوصول لصفحة لا تحتوي على شركات
            if count == 0:
                print(f"🛑 Reached the end of pages at page {page_num - 1}")
                await page.close()
                break

            for i in range(count):
                href = await links.nth(i).get_attribute("href")

                if not href or "carrierregister.php" in href:
                    continue

                if href.startswith("/"):
                    href = "https://www.quicktransportsolutions.com" + href

                company_links.append(href)

        except Exception as e:
            print(f"❌ Error scraping page {page_num}: {e}")

        finally:
            await page.close()

    # إزالة التكرار
    company_links = list(dict.fromkeys(company_links))
    print(f"\n✅ Total unique companies found across all pages: {len(company_links)}")

    return company_links


# ==========================================
# 2. استخراج بيانات الشركة التفصيلية
# ==========================================
async def scrape_company_details(context, url):

    async with semaphore:
        page = None

        try:
            page = await context.new_page()

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            company_name = "N/A"
            phone = "N/A"
            usdot = "N/A"
            trucks = "N/A"
            drivers = "N/A"

            # 1. اسم الشركة
            h1 = page.locator("h1")

            if await h1.count() > 0:
                company_name = await h1.text_content()

                if company_name:
                    company_name = company_name.strip()

            page_text = await page.locator("body").inner_text()

            # 2. الهاتف
            phone_match = re.search(
                r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
                page_text
            )

            if phone_match:
                phone = phone_match.group().strip()

            # 3. USDOT
            usdot_match = re.search(
                r"USDOT[#\s:]*(\d+)",
                page_text,
                re.IGNORECASE
            )

            if usdot_match:
                usdot = usdot_match.group(1).strip()

            # 4. الشاحنات (Trucks)
            trucks_match = re.search(
                r"Trucks:\s*(\d+)",
                page_text,
                re.IGNORECASE
            )

            if trucks_match:
                trucks = trucks_match.group(1).strip()

            # 5. السائقين (Drivers)
            drivers_match = re.search(
                r"Drivers:\s*(\d+)",
                page_text,
                re.IGNORECASE
            )

            if drivers_match:
                drivers = drivers_match.group(1).strip()

            all_companies.append({
                "Company Name": company_name,
                "Phone": phone,
                "Trucks": trucks,
                "Drivers": drivers,
                "City": "Dallas",
                "State": "Texas",
                "USDOT": usdot,
                "Source URL": url
            })

            print(f"✅ Extracted: {company_name} | Phone: {phone} | USDOT: {usdot}")

        except Exception as e:
            print(f"❌ Error scraping company ({url}): {e}")

        finally:
            if page:
                await page.close()


# ==========================================
# 3. تصدير البيانات إلى Excel
# ==========================================
def export_to_excel():

    if not all_companies:
        print("❌ No data extracted!")
        return

    df = pd.DataFrame(all_companies)
    file_name = "dallas_trucking_companies.xlsx"
    df.to_excel(file_name, index=False)

    print(f"\n🎉 File saved successfully: {file_name}")
    print(f"📊 Total Companies Extracted in Dallas: {len(all_companies)}")


# ==========================================
# 4. الدالة الرئيسية (Main)
# ==========================================
async def main():

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        # يمكنك تعديل max_pages للعدد الذي تريده (مثلاً 10 أو 20 صفحة)
        company_links = await get_all_dallas_company_links(context, max_pages=10)

        if company_links:
            print(f"\n🚚 Extracting details for {len(company_links)} companies...")

            tasks = [
                scrape_company_details(context, url)
                for url in company_links
            ]

            await asyncio.gather(*tasks, return_exceptions=True)

        await browser.close()

    export_to_excel()


if __name__ == "__main__":
    asyncio.run(main())