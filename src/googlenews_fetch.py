from GoogleNews import GoogleNews


class GoogleNewsFetcher:
    def __init__(self, lang="en", period="7d"):
        self.gn = GoogleNews(lang=lang, period=period)

    def search(self, keyword, max_results=10):
        self.gn.search(keyword)
        results = self.gn.results()
        return results[:max_results]
