#!/usr/bin/env python3
"""
AI 뉴스 수집 스크립트
매일 전날의 AI 관련 뉴스를 수집하여 마크다운 파일로 정리합니다.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path


def fetch_news_from_gnews(query: str, days_ago: int = 1) -> list:
    """
    GNews API를 사용하여 뉴스를 가져옵니다.
    무료 플랜: 하루 100건 요청 가능
    """
    api_key = os.environ.get("GNEWS_API_KEY")
    if not api_key:
        print("Warning: GNEWS_API_KEY not set, using fallback method")
        return []

    # 전날 날짜 계산
    target_date = datetime.now() - timedelta(days=days_ago)
    from_date = target_date.strftime("%Y-%m-%dT00:00:00Z")
    to_date = target_date.strftime("%Y-%m-%dT23:59:59Z")

    url = "https://gnews.io/api/v4/search"
    params = {
        "q": query,
        "lang": "en",
        "country": "us",
        "max": 10,
        "from": from_date,
        "to": to_date,
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print(f"Error fetching from GNews: {e}")
        return []


def fetch_news_from_newsapi(query: str, days_ago: int = 1) -> list:
    """
    NewsAPI를 사용하여 뉴스를 가져옵니다.
    무료 플랜: 하루 100건 요청 가능
    """
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        print("Warning: NEWS_API_KEY not set")
        return []

    target_date = datetime.now() - timedelta(days=days_ago)
    date_str = target_date.strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": date_str,
        "to": date_str,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 10,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except Exception as e:
        print(f"Error fetching from NewsAPI: {e}")
        return []


def fetch_news_from_rss() -> list:
    """
    RSS 피드에서 AI 뉴스를 가져옵니다 (API 키 불필요).
    """
    import xml.etree.ElementTree as ET

    rss_feeds = [
        "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=machine+learning&hl=en-US&gl=US&ceid=US:en",
        "https://news.google.com/rss/search?q=ChatGPT+OR+OpenAI+OR+Claude+OR+Anthropic&hl=en-US&gl=US&ceid=US:en",
    ]

    articles = []
    seen_titles = set()

    for feed_url in rss_feeds:
        try:
            response = requests.get(feed_url, timeout=30)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            for item in root.findall(".//item"):
                title = item.find("title")
                link = item.find("link")
                pub_date = item.find("pubDate")
                description = item.find("description")
                source = item.find("source")

                if title is not None and title.text not in seen_titles:
                    seen_titles.add(title.text)
                    articles.append({
                        "title": title.text if title is not None else "No Title",
                        "url": link.text if link is not None else "",
                        "publishedAt": pub_date.text if pub_date is not None else "",
                        "description": description.text if description is not None else "",
                        "source": {"name": source.text if source is not None else "Unknown"}
                    })
        except Exception as e:
            print(f"Error fetching RSS feed {feed_url}: {e}")

    return articles[:20]  # 최대 20개 기사 반환


def format_news_to_markdown(articles: list, date_str: str) -> str:
    """
    뉴스 기사 목록을 마크다운 형식으로 변환합니다.
    """
    md_content = f"""# 🤖 AI 뉴스 다이제스트

**날짜**: {date_str}
**생성 시간**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC

---

## 📰 주요 AI 뉴스

"""

    if not articles:
        md_content += "*오늘의 뉴스를 찾지 못했습니다.*\n"
        return md_content

    for i, article in enumerate(articles, 1):
        title = article.get("title", "No Title")
        url = article.get("url", article.get("link", "#"))
        source = article.get("source", {})
        source_name = source.get("name", "Unknown") if isinstance(source, dict) else str(source)
        description = article.get("description", "")
        published = article.get("publishedAt", "")

        # HTML 태그 제거 (간단한 처리)
        if description:
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = description[:200] + "..." if len(description) > 200 else description

        md_content += f"""### {i}. {title}

**출처**: {source_name}
**링크**: [{url}]({url})
{f"**발행일**: {published}" if published else ""}

{description if description else ""}

---

"""

    md_content += """
## 📊 통계

| 항목 | 값 |
|------|-----|
| 총 기사 수 | {} |
| 수집 방법 | RSS/API |

---

*이 다이제스트는 자동으로 생성되었습니다.*
""".format(len(articles))

    return md_content


def save_news(content: str, date_str: str, output_dir: str = "news"):
    """
    뉴스 내용을 파일로 저장합니다.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"ai-news-{date_str}.md"
    filepath = output_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"News saved to: {filepath}")
    return filepath


def update_readme(date_str: str, news_dir: str = "news"):
    """
    README.md에 최신 뉴스 링크를 추가합니다.
    """
    readme_path = Path("README.md")
    news_file = f"ai-news-{date_str}.md"
    news_link = f"- [{date_str}](./{news_dir}/{news_file})"

    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
    else:
        content = "# AI News Digest\n\n매일 자동으로 수집되는 AI 뉴스입니다.\n\n## 📅 뉴스 아카이브\n\n"

    # 뉴스 아카이브 섹션이 없으면 추가
    if "## 📅 뉴스 아카이브" not in content:
        content += "\n## 📅 뉴스 아카이브\n\n"

    # 이미 해당 날짜의 링크가 있는지 확인
    if news_link not in content:
        # 뉴스 아카이브 섹션 바로 다음에 링크 추가
        archive_marker = "## 📅 뉴스 아카이브\n\n"
        if archive_marker in content:
            content = content.replace(archive_marker, archive_marker + news_link + "\n")
        else:
            content += news_link + "\n"

    readme_path.write_text(content, encoding="utf-8")
    print(f"README.md updated with link to {news_file}")


def main():
    """
    메인 실행 함수
    """
    print("=" * 50)
    print("AI News Digest Generator")
    print("=" * 50)

    # 전날 날짜
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")

    print(f"\nFetching AI news for: {date_str}")

    # 뉴스 수집 시도 (API 우선, RSS 대체)
    articles = []

    # 1. GNews API 시도
    if os.environ.get("GNEWS_API_KEY"):
        print("Trying GNews API...")
        articles = fetch_news_from_gnews("artificial intelligence OR machine learning OR ChatGPT OR OpenAI")

    # 2. NewsAPI 시도
    if not articles and os.environ.get("NEWS_API_KEY"):
        print("Trying NewsAPI...")
        articles = fetch_news_from_newsapi("artificial intelligence OR machine learning")

    # 3. RSS 피드 사용 (대체)
    if not articles:
        print("Using RSS feeds...")
        articles = fetch_news_from_rss()

    print(f"\nCollected {len(articles)} articles")

    # 마크다운 생성 및 저장
    markdown_content = format_news_to_markdown(articles, date_str)
    save_news(markdown_content, date_str)

    # README 업데이트
    update_readme(date_str)

    print("\n✅ News digest generated successfully!")


if __name__ == "__main__":
    main()
