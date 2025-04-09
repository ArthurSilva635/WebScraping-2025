import scrapy


class NotebookSpider(scrapy.Spider):
    name = "notebook"
    allowed_domains = ["lista.mercadolivre.com.br"]
    start_urls = ["https://lista.mercadolivre.com.br/notebook#D[A:Notebook]"]

    def parse(self, response):
        products = response.css('div.ui-search-result__wrapper')

        for product in products:
            yield{

                'brand': product.css('span.poly-component__brand::text').get(),
                'name': product.css('a.poly-component__title').get()

            }


        pass
