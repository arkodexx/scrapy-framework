import scrapy
import json
from scrapy.http import JsonRequest
import asyncio

from core_framework.config_loader import load_config
config = load_config()

class CrawlerSpider(scrapy.Spider):
    name = "crawler"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/118.0.5993.117 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;"
                  "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    async def start(self):
        for site in config.get("sites", []):
            meta = {}

            if site.get("use_playwright"):
                meta["playwright"] = True
                meta["playwright_include_page"] = True

            method = site.get("method", "GET").upper()
            payload = site.get("payload", {})

            if method == "POST":
                yield JsonRequest(
                    url=site["url"],
                    headers=config.get("headers", {}),
                    data=payload,
                    method="POST",
                    meta=meta,
                    callback=self.main_parse,
                    cb_kwargs={"site_name": site["name"]}
                )
            else:
                yield scrapy.Request(
                    url=site["url"],
                    headers=config.get("headers", {}),
                    meta=meta,
                    callback=self.main_parse,
                    cb_kwargs={"site_name": site["name"]}
                )

    def main_parse(self, response, site_name):
        self.logger.info(f"Scraping site: {site_name} -> {response.url}")

        # Write your main parse logic here
        yield {
            "site": site_name,
            "url": response.url,
            "data": response.text[:500]
        }
