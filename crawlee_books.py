import asyncio
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

async def main() -> None:
    crawler = BeautifulSoupCrawler(
        #max_requests_per_crawl=5,
    )

    @crawler.router.default_handler
    # Исправлен регистр и имя переменной приведено к context
    async def default_handler(context: BeautifulSoupCrawlingContext) -> None:
        context.log.info(f"Обработка страницы: {context.request.url}")
        
        books = context.soup.find_all("article", class_="product_pod")
        
        for book in books:
            title = book.h3.a["title"]
            price = float(book.find("p", class_="price_color").text.replace("£", "").replace("Â", ""))
            availability = book.find("p", class_="instock availability").text.strip()
            star_rating = book.p["class"][1]
            
            # Теперь везде используется context
            await context.push_data({
                "Название книги": title,
                "Цена": price,
                "Наличие": availability,
                "Рейтинг": star_rating
            })
            
        await context.enqueue_links(
            selector=".next a"
        )

    # Отступы исправлены: эти команды вне функции default_handler
    await crawler.run(['https://books.toscrape.com/catalogue/page-1.html'])
    
    await crawler.export_data("crawlee_books_dataset.csv")
    print("Данные успешно экспортированы в crawlee_books_dataset.csv")


if __name__ == "__main__":
    asyncio.run(main())