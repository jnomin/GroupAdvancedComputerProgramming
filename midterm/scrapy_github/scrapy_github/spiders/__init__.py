import scrapy
from scrapy_github.items import ScrapyGithubItem

class GithubReposSpider(scrapy.Spider):
    name = 'github_repos'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/Muugii1234?tab=repositories']

    def parse(self, response):
        repos = response.css('li[itemprop="owns"]')
        for repo in repos:
            relative_url = repo.css('a[itemprop="name codeRepository"]::attr(href)').get()
            repo_url = response.urljoin(relative_url)
            yield scrapy.Request(repo_url, callback=self.parse_repo, meta={'repo_url': repo_url})

    def parse_repo(self, response):
        item = ScrapyGithubItem()
        item['url'] = response.meta['repo_url']

        about = response.css('p.f4.my-3::text').get()
        item['about'] = about.strip() if about else None

        # Last updated
        updated = response.css('relative-time::attr(datetime)').get()
        item['last_updated'] = updated

        # Check if repo is empty
        is_empty = response.css('div.Box.mt-3 p::text').re_first(r'This repository is empty')
        if is_empty:
            item['languages'] = None
            item['commits'] = None
            if not item['about']:
                repo_name = response.url.split("/")[-1]
                item['about'] = repo_name
            yield item
            return

        # Get languages
        langs = response.css('ul.list-style-none span[itemprop="programmingLanguage"]::text').getall()
        item['languages'] = langs

        # Get number of commits
        commits = response.css('li.Commits span.d-none.d-sm-inline strong::text').get()
        item['commits'] = commits.strip() if commits else None

        if not item['about']:
            repo_name = response.url.split("/")[-1]
            item['about'] = repo_name

        yield item
