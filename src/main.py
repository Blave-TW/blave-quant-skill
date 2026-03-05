from googlenews_fetch import GoogleNewsFetcher


class BlaveQuantSkill:
    def fetch_news(self, keyword, max_results=10, lang="en", period="7d"):
        fetcher = GoogleNewsFetcher(lang=lang, period=period)
        return fetcher.search(keyword, max_results=max_results)
