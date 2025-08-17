"""
This module contains the NovelFullParser class and its variations.
"""
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from ..parser import Parser

class NovelFullParser(Parser):
    def get_title(self):
        title_tag = self.soup.select_one('h3.title')
        return title_tag.get_text() if title_tag else None

    def get_author(self):
        author_tag = self.soup.select_one('ul.info-meta li a')
        return author_tag.get_text() if author_tag else None

    def get_cover_image_url(self):
        img_tag = self.soup.select_one('div.book img')
        return urljoin(self.base_url, img_tag['src']) if img_tag and img_tag.has_attr('src') else None

    def get_chapter_urls(self, downloader):
        toc_page_urls = self._get_toc_page_urls()

        if not toc_page_urls: # No pagination
            return self._extract_chapters_from_page(self.soup)

        all_chapter_urls = []
        for url in toc_page_urls:
            content = downloader.get(url)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                all_chapter_urls.extend(self._extract_chapters_from_page(soup))

        return all_chapter_urls

    def _extract_chapters_from_page(self, soup):
        chapter_links = soup.select('ul.list-chapter a')
        urls = []
        for link in chapter_links:
            urls.append(urljoin(self.base_url, link['href']))
        return urls

    def _get_toc_page_urls(self):
        last_page_link_tag = self.soup.select_one("li.last a")
        if not last_page_link_tag:
            return []

        last_page_href = last_page_link_tag['href']

        limit = last_page_link_tag.get('data-page')
        if not limit:
            parsed_url = urlparse(last_page_href)
            query_params = parse_qs(parsed_url.query)
            if 'page_num' in query_params:
                limit = query_params['page_num'][0]
            elif 'page' in query_params:
                 limit = query_params['page'][0]

        if not limit:
            return []

        limit = int(limit)

        base_toc_url = urljoin(self.base_url, last_page_href)

        toc_urls = []
        for i in range(1, limit + 1):
            toc_urls.append(self._build_toc_page_url(base_toc_url, i))

        return toc_urls

    def _build_toc_page_url(self, link, i):
        parsed_url = urlparse(link)
        hostname = parsed_url.hostname

        if hostname == "freenovelsread.com":
            path_parts = parsed_url.path.strip('/').split('/')
            new_path = f"/{path_parts[0]}/{i}"
            return parsed_url._replace(path=new_path, query="").geturl()
        elif hostname == "novelfulll.com":
            return parsed_url._replace(query=f"page_num={i}").geturl()
        else:
            return parsed_url._replace(query=f"page={i}&per-page=50").geturl()

    def get_chapter_content(self, chapter_content):
        from bs4 import NavigableString
        soup = BeautifulSoup(chapter_content, 'html.parser')

        # Watermark removal logic
        watermark = self._find_watermark(soup)
        if watermark:
            for p in soup.find_all("p"):
                for text_node in p.find_all(string=True):
                    if watermark in text_node:
                        new_text = text_node.replace(watermark, '')
                        text_node.replace_with(NavigableString(new_text))

        content_div = soup.select_one("#chr-content") or soup.select_one("#chapter-content")
        if content_div:
            return str(self.clean_content(content_div))
        return chapter_content

    def _find_watermark(self, soup):
        search_token = "original11Content.replace(\""
        for script in soup.find_all("script"):
            if script.string and search_token in script.string:
                script_content = script.string
                start_index = script_content.find(search_token) + len(search_token)
                end_index = script_content.find("\"", start_index)
                if end_index != -1:
                    return script_content[start_index:end_index]
        return None

    def get_chapter_title(self, chapter_content):
        soup = BeautifulSoup(chapter_content, 'html.parser')
        title_tag = soup.select_one("h2")
        return title_tag.get_text() if title_tag else ""

class Novel35Parser(NovelFullParser):
    def _get_toc_page_urls(self):
        paginate_links = self.soup.select("ul.pagination li a:not([rel])")
        if not paginate_links:
            return []

        last_page_url = paginate_links[-1]['href']
        parsed_url = urlparse(last_page_url)
        query_params = parse_qs(parsed_url.query)
        max_page = int(query_params.get('page', [1])[0])

        urls = []
        for i in range(1, max_page + 1):
            query_params['page'] = [str(i)]
            urls.append(parsed_url._replace(query=urlencode(query_params, doseq=True)).geturl())

        return urls

    def get_chapter_content(self, chapter_content):
        soup = BeautifulSoup(chapter_content, 'html.parser')
        content_div = soup.select_one("div.chapter-content")
        if content_div:
            return str(self.clean_content(content_div))
        return chapter_content

    def get_chapter_title(self, chapter_content):
        soup = BeautifulSoup(chapter_content, 'html.parser')
        title_tag = soup.select_one("div.chapter-title")
        return title_tag.get_text() if title_tag else ""

class NovelHyphenBinParser(NovelFullParser):
    def clean_content(self, element):
        for mark in element.select(".novel_online, .unlock-buttons"):
            if mark.next_sibling and mark.next_sibling.next_sibling:
                mark.next_sibling.next_sibling.decompose()
            mark.decompose()
        return super().clean_content(element)

class NovelbinParser(NovelFullParser):
    def get_chapter_urls(self, downloader):
        parsed_url = urlparse(self.base_url)
        slug_parts = parsed_url.path.strip('/').split('/')
        if not slug_parts:
            return []

        slug = slug_parts[-1]
        toc_url = f"https://novelbin.com/ajax/chapter-archive?novelId={slug}"
        toc_html = downloader.get(toc_url)
        if not toc_html:
            return []

        soup = BeautifulSoup(toc_html, 'html.parser')
        return self._extract_chapters_from_page(soup)

    def clean_content(self, element):
        for mark in element.select(".unlock-buttons"):
            mark.decompose()
        return super().clean_content(element)
