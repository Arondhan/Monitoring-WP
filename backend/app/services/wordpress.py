"""
Сервис для получения контента WordPress-страниц (для мониторинга Uptime Checker).
"""
import re
from typing import Optional, Dict, List
import httpx
from bs4 import BeautifulSoup


async def get_wordpress_content(url: str, timeout: int = 10) -> Dict[str, object]:
    """
    Получить контент страницы WordPress: meta title, description, h1, h2.

    Используется Uptime Checker для:
    - определения, является ли сайт WordPress
    - отображения SEO-информации (meta title/description)
    - отображения структуры заголовков (h1, h2)

    Returns:
        Dict с полями:
        - meta_title: str
        - meta_title_length: int
        - meta_description: str
        - meta_description_length: int
        - h1: str
        - h2: List[str]
    """
    result: Dict[str, object] = {
        "meta_title": None,
        "meta_title_length": None,
        "meta_description": None,
        "meta_description_length": None,
        "h1": None,
        "h2": [],
    }

    try:
        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            verify=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text

        soup = BeautifulSoup(html, "lxml")

        # Meta title
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            meta_title = title_tag.string.strip()
            result["meta_title"] = meta_title
            result["meta_title_length"] = len(meta_title)

        # Meta description (обычный или Yoast/RankMath)
        meta_desc = None
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()
        else:
            yoast_desc = soup.find("meta", attrs={"property": "og:description"})
            if yoast_desc and yoast_desc.get("content"):
                meta_desc = yoast_desc["content"].strip()

        if meta_desc:
            result["meta_description"] = meta_desc
            result["meta_description_length"] = len(meta_desc)

        # H1
        h1_tag = soup.find("h1")
        if h1_tag:
            h1_text = h1_tag.get_text(strip=True)
            if h1_text:
                result["h1"] = h1_text

        # H2 (список)
        h2_tags = soup.find_all("h2")
        h2_list: List[str] = []
        for tag in h2_tags:
            text = tag.get_text(strip=True)
            if text:
                h2_list.append(text)
        result["h2"] = h2_list

    except httpx.TimeoutException:
        pass
    except httpx.HTTPError:
        pass
    except Exception:
        pass

    return result


class WordPressService:
    """Сервис для работы с WordPress-страницами (мониторинг)."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def get_content(self, url: str) -> Dict[str, object]:
        """Получить контент страницы."""
        return await get_wordpress_content(url, timeout=self.timeout)


_wordpress_service: Optional[WordPressService] = None


def get_wordpress_service() -> WordPressService:
    """Получить singleton-инстанс WordPressService."""
    global _wordpress_service
    if _wordpress_service is None:
        _wordpress_service = WordPressService()
    return _wordpress_service
