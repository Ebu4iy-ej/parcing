import asyncio
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

async def main() -> None:
    # Инициализируем краулер на базе Playwright
    # headless=False означает, что мы будем своими глазами видеть открытое окно браузера
    crawler = PlaywrightCrawler(
        max_requests_per_crawl=10,
        headless=False, 
    )

    @crawler.router.default_handler
    async def default_handler(context: PlaywrightCrawlingContext) -> None:
        context.log.info(f"Анализируем страницу: {context.request.url}")
        
        # 1. Ждем, пока страница полностью загрузит скрипты и отрисует карточки вакансий.
        # На hh.ru карточки часто имеют атрибут data-qa="vacancy-serp__vacancy"
        await context.page.wait_for_selector('[data-qa="vacancy-serp__vacancy"]', timeout=15000)
        
        # 2. Находим все карточки на текущей странице
        vacancies = await context.page.locator('[data-qa="vacancy-serp__vacancy"]').all()
        
        for vac in vacancies:
            # Playwright работает асинхронно, поэтому для получения текста мы используем await
            
            # Название вакансии
            title_loc = vac.locator('[data-qa="serp-item__title"]')
            title = await title_loc.inner_text() if await title_loc.count() > 0 else "Не указано"
            
            # Зарплата (если есть)
            salary_loc = vac.locator('[data-qa="vacancy-compensation"]')
            salary = await salary_loc.inner_text() if await salary_loc.count() > 0 else "Не указана"
            
            # Компания
            company_loc = vac.locator('[data-qa="vacancy-serp__vacancy-employer"]')
            company = await company_loc.inner_text() if await company_loc.count() > 0 else "Не указана"
            
            # Ссылка на саму вакансию
            link = await title_loc.get_attribute('href') if await title_loc.count() > 0 else ""
            
            await context.push_data({
                "Должность": title,
                "Зарплата": salary,
                "Компания": company,
                "Ссылка": link
            })
            
        # 3. Ищем кнопку "Дальше" и добавляем следующую страницу в очередь
        # 3. Прокручиваем страницу вниз, чтобы подгрузить кнопку пагинации
        await context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await context.page.wait_for_timeout(1000) # Пауза 1 секунда

        # Переходим на следующую страницу
        await context.enqueue_links(
            selector='a[data-qa="pager-next"]'
        )

    # Стартовая ссылка: Аналитик данных в Иваново
    await crawler.run(['https://hh.ru/search/vacancy?text=Аналитик+данных&schedule=remote'])
    
    await crawler.export_data("hh_analytics_dataset.csv")
    print("Парсинг hh.ru завершен! Данные сохранены.")

if __name__ == "__main__":
    asyncio.run(main())