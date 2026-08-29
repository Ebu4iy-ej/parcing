import asyncio
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from urllib.parse import urljoin

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
            
        # 3. Прокручиваем страницу вниз и явно ищем ссылку "Дальше"
        await context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await context.page.wait_for_timeout(1000)

        next_button = context.page.locator('[data-qa="pager-next"]')
        
        if await next_button.count() > 0:
            next_href = await next_button.get_attribute('href')
            if next_href:
                # Собираем полный URL из относительного адреса
                next_url = urljoin(context.request.url, next_href)
                context.log.info(f"Найдена следующая страница: {next_url}")
                # Принудительно добавляем ссылку в очередь задач
                await context.add_requests([next_url])
        else:
            context.log.info("Кнопка 'Дальше' не найдена на странице.")
        
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