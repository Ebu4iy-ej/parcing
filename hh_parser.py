import asyncio
from urllib.parse import urljoin
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

async def main() -> None:
    crawler = PlaywrightCrawler(
        max_requests_per_crawl=40,
        headless=False, 
    )

    @crawler.router.default_handler
    async def default_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f"Анализируем страницу: {context.request.url}")
        
        # Ожидаем загрузки карточек вакансий
        await context.page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]', timeout=15000)
        
        vacancies = await context.page.locator('[data-qa="vacancy-serp__vacancy"]').all()
        
        for vac in vacancies:
            # Название вакансии
            title_loc = vac.locator('[data-qa="serp-item__title"]')
            title = await title_loc.inner_text() if await title_loc.count() > 0 else "Не указано"
            
            # Зарплата: ищем по маске любой атрибут или класс со словом compensation
            salary_loc = vac.locator('[data-qa*="compensation"], [class*="compensation"]')
            
            if await salary_loc.count() > 0:
                salary_raw = await salary_loc.first.inner_text()
                # Очищаем от неразрывных пробелов и переносов строк
                salary = salary_raw.replace('\xa0', ' ').replace('\n', ' ').strip()
            else:
                salary = "Не указана"
            
            # Компания
            company_loc = vac.locator('[data-qa="vacancy-serp__vacancy-employer"]')
            company = await company_loc.inner_text() if await company_loc.count() > 0 else "Не указана"
            
            # Ссылка
            link = await title_loc.get_attribute('href') if await title_loc.count() > 0 else ""
            
            await context.push_data({
                "Должность": title,
                "Зарплата": salary,
                "Компания": company,
                "Ссылка": link
            })
            
        # Прокручиваем страницу вниз
        await context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await context.page.wait_for_timeout(1000)

        # Пагинация
        next_button = context.page.locator('[data-qa="pager-next"]')
        if await next_button.count() > 0:
            next_href = await next_button.get_attribute('href')
            if next_href:
                next_url = urljoin(context.request.url, next_href)
                context.log.info(f"Найдена следующая страница: {next_url}")
                await context.add_requests([next_url])
        else:
            context.log.info("Кнопка 'Дальше' не найдена на странице.")

    # Целевая ссылка: Аналитик данных | Удаленка | Без опыта + От 1 до 3 лет
    target_url = (
        "https://hh.ru/search/vacancy?"
        "text=Аналитик+данных"
        "&schedule=remote"
        "&experience=noExperience"
        "&experience=between1And3"
    )
    
    await crawler.run([target_url])
    await crawler.export_data("hh_analytics_dataset.csv")
    print("Парсинг hh.ru завершен! Данные сохранены.")

if __name__ == "__main__":
    asyncio.run(main())