import scrapy
from github_scraper.items import GithubScraperItem

class GithubReposSpider(scrapy.Spider):
    name = 'github_repos'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/jnomin?tab=repositories']

    def parse(self, response):
        repos = response.css('li[itemprop="owns"]')
        for repo in repos:
            item = GithubScraperItem()
            repo_url = response.urljoin(repo.css('a[itemprop="name codeRepository"]::attr(href)').get())
            item['url'] = repo_url

            about = repo.css('p[itemprop="description"]::text').get()
            item['about'] = about.strip() if about else repo.css('a[itemprop="name codeRepository"]::text').get().strip()
            item['last_updated'] = repo.css('relative-time::attr(datetime)').get()

            # Request the repo details page
            yield scrapy.Request(repo_url, callback=self.parse_repo_details, meta={'item': item})

    def parse_repo_details(self, response):
        item = response.meta['item']

        if response.css('div.Layout-main'):
            languages = response.css('div.Layout-sidebar li span::text').getall()
            item['languages'] = [lang.strip() for lang in languages if lang.strip()]
            
            commits = response.xpath('//a[contains(@href, "/commits")]/span/text()').get()
            item['commits'] = commits.strip() if commits else '1'
        else:
            item['languages'] = None
            item['commits'] = None

        yield item
