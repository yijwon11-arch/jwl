# AI News Digest

매일 오전 9시(KST)에 자동으로 AI 관련 뉴스를 수집하고 정리합니다.

## 🚀 기능

- **자동 뉴스 수집**: GitHub Actions를 통해 매일 오전 9시에 자동 실행
- **다양한 소스**: Google News RSS, GNews API, NewsAPI 지원
- **마크다운 정리**: 읽기 쉬운 마크다운 형식으로 뉴스 정리
- **아카이브**: 날짜별로 뉴스 파일 보관

## 📁 프로젝트 구조

```
├── .github/workflows/
│   └── daily-ai-news.yml    # GitHub Actions 워크플로우
├── scripts/
│   └── fetch_ai_news.py     # 뉴스 수집 스크립트
├── news/                     # 수집된 뉴스 저장 디렉토리
├── requirements.txt
└── README.md
```

## ⚙️ 설정

### API 키 (선택사항)

더 나은 뉴스 수집을 위해 API 키를 설정할 수 있습니다:

1. **GNews API**: [gnews.io](https://gnews.io/)에서 무료 API 키 발급
2. **NewsAPI**: [newsapi.org](https://newsapi.org/)에서 무료 API 키 발급

GitHub Repository Settings → Secrets and variables → Actions에서 다음 시크릿을 추가하세요:

- `GNEWS_API_KEY`
- `NEWS_API_KEY`

> ⚠️ API 키가 없어도 Google News RSS 피드를 통해 뉴스 수집이 가능합니다.

## 🔧 수동 실행

GitHub Actions 탭에서 "Daily AI News Digest" 워크플로우를 수동으로 실행할 수 있습니다.

## 📅 뉴스 아카이브

