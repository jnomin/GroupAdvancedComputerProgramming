import scrapy
import json
from github_scraper.items import GithubScraperItem

class GithubSpider(scrapy.Spider):
    name = "github"
    USERNAME = "Muugii1234"
    BASE_API = f"https://api.github.com/users/{USERNAME}/repos"
    HEADERS = {'Accept': 'application/vnd.github+json'}

    custom_settings = {
        'FEEDS': {
            'github_repos.xml': {
                'format': 'xml',
                'overwrite': True
            }
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.BASE_API,
            headers=self.HEADERS,
            callback=self.parse_repos
        )

    def parse_repos(self, response):
        repos = json.loads(response.text)

        for repo in repos:
            is_empty = repo['size'] == 0
            repo_name = repo['name']
            about = repo['description'] or (repo_name if not is_empty else None)

            item = GithubScraperItem(
                url=repo['html_url'],
                about=about,
                last_updated=repo['updated_at'],
                languages='None',
                commits='None'
            )

            if not is_empty:
                # Get languages next
                meta = {'item': item, 'commits_url': repo['commits_url'].replace('{/sha}', '')}
                yield scrapy.Request(
                    url=repo['languages_url'],
                    headers=self.HEADERS,
                    callback=self.parse_languages,
                    meta=meta
                )
            else:
                yield item  # Empty repo, skip commits/languages

    def parse_languages(self, response):
        item = response.meta['item']
        commits_url = response.meta['commits_url']

        lang_data = json.loads(response.text)
        item['languages'] = ', '.join(lang_data.keys()) if lang_data else 'None'

        # Get commit count next
        yield scrapy.Request(
            url=commits_url,
            headers=self.HEADERS,
            callback=self.parse_commits,
            meta={'item': item}
        )

    def parse_commits(self, response):
        item = response.meta['item']
        link_header = response.headers.get('Link', b'').decode('utf-8')

        if 'rel="last"' in link_header:
            try:
                last_page = link_header.split('rel="last"')[0].split('page=')[-1].split('>')[0]
                item['commits'] = int(last_page)
            except:
                item['commits'] = 'Unknown'
        else:
            item['commits'] = 1 if response.status == 200 else 'None'

        yield item
