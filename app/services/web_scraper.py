import logging
from typing import List, Dict
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

INFINITEPAY_URLS = [
    "https://www.infinitepay.io",
    "https://www.infinitepay.io/maquininha",
    "https://www.infinitepay.io/maquininha-celular",
    "https://www.infinitepay.io/tap-to-pay",
    "https://www.infinitepay.io/pdv",
    "https://www.infinitepay.io/receba-na-hora",
    "https://www.infinitepay.io/gestao-de-cobranca-2",
    "https://www.infinitepay.io/gestao-de-cobranca",
    "https://www.infinitepay.io/link-de-pagamento",
    "https://www.infinitepay.io/loja-online",
    "https://www.infinitepay.io/boleto",
    "https://www.infinitepay.io/conta-digital",
    "https://www.infinitepay.io/conta-pj",
    "https://www.infinitepay.io/pix",
    "https://www.infinitepay.io/pix-parcelado",
    "https://www.infinitepay.io/emprestimo",
    "https://www.infinitepay.io/cartao",
    "https://www.infinitepay.io/rendimento",
]


class WebScraper:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def scrape_url(self, url: str) -> Dict[str, str]:
        try:
            logger.info(f"Scraping URL: {url}")
            response = httpx.get(url, headers=self.headers, timeout=self.timeout, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            title = soup.title.string if soup.title else url.split("/")[-1]
            text = soup.get_text(separator="\n", strip=True)

            text = "\n".join([line for line in text.split("\n") if line.strip()])

            logger.info(f"Successfully scraped {url}: {len(text)} characters")

            return {
                "url": url,
                "title": title.strip(),
                "content": text,
                "length": len(text)
            }

        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping {url}: {e}")
            return {"url": url, "title": "", "content": "", "length": 0, "error": str(e)}
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {"url": url, "title": "", "content": "", "length": 0, "error": str(e)}

    def scrape_all(self, urls: List[str] = None) -> List[Dict[str, str]]:
        urls = urls or INFINITEPAY_URLS
        logger.info(f"Starting scraping {len(urls)} URLs")

        results = []
        for url in urls:
            result = self.scrape_url(url)
            if result["content"]:
                results.append(result)

        logger.info(f"Scraping complete: {len(results)}/{len(urls)} successful")
        return results
