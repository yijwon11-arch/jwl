"""
유사도 분석 모듈

특허 문서 간의 유사도를 TF-IDF와 코사인 유사도로 계산합니다.
"""

from typing import List, Dict, Tuple
import re
from collections import Counter

# Optional imports - 설치되지 않은 경우 간단한 유사도 계산 사용
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class SimilarityAnalyzer:
    """특허 간 유사도를 분석하는 클래스"""

    def __init__(self, language: str = 'multilingual'):
        """
        SimilarityAnalyzer 초기화

        Args:
            language: 분석 언어 ('ko', 'en', 'multilingual')
        """
        self.language = language
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),  # 1-gram과 2-gram 사용
                min_df=1,
                stop_words=None  # 커스텀 불용어 처리는 전처리에서
            )
        else:
            self.vectorizer = None
            print("참고: scikit-learn이 설치되지 않아 간단한 유사도 계산을 사용합니다.")

    def analyze(self, source_patent: Dict, candidate_patents: List[Dict]) -> List[Dict]:
        """
        원본 특허와 후보 특허들 간의 유사도를 분석합니다.

        Args:
            source_patent: 원본 특허 정보
            candidate_patents: 비교할 후보 특허 리스트

        Returns:
            유사도 점수가 추가된 후보 특허 리스트 (유사도 높은 순 정렬)
        """
        if not candidate_patents:
            return []

        # 텍스트 추출
        source_text = self._extract_text(source_patent)
        candidate_texts = [self._extract_text(patent) for patent in candidate_patents]

        # sklearn이 있으면 TF-IDF 사용, 없으면 간단한 유사도 계산
        if HAS_SKLEARN and self.vectorizer:
            try:
                # 모든 문서를 합쳐서 벡터화
                all_texts = [source_text] + candidate_texts

                # TF-IDF 벡터화
                tfidf_matrix = self.vectorizer.fit_transform(all_texts)

                # 코사인 유사도 계산
                source_vector = tfidf_matrix[0:1]
                candidate_vectors = tfidf_matrix[1:]

                similarities = cosine_similarity(source_vector, candidate_vectors)[0]

                # 결과에 유사도 점수 추가
                for i, patent in enumerate(candidate_patents):
                    patent['similarity_score'] = float(similarities[i])
                    patent['similarity_percentage'] = f"{similarities[i] * 100:.2f}%"

            except Exception as e:
                print(f"유사도 분석 중 오류 발생: {e}")
                # 오류 발생 시 간단한 유사도 계산으로 폴백
                self._simple_similarity_calculation(source_text, candidate_texts, candidate_patents)
        else:
            # sklearn이 없으면 간단한 유사도 계산
            self._simple_similarity_calculation(source_text, candidate_texts, candidate_patents)

        # 유사도 높은 순으로 정렬
        sorted_patents = sorted(
            candidate_patents,
            key=lambda x: x['similarity_score'],
            reverse=True
        )

        return sorted_patents

    def _simple_similarity_calculation(self, source_text: str, candidate_texts: List[str], candidate_patents: List[Dict]) -> None:
        """
        간단한 자카드 유사도를 계산합니다.

        Args:
            source_text: 원본 텍스트
            candidate_texts: 후보 텍스트 리스트
            candidate_patents: 후보 특허 리스트 (in-place 수정)
        """
        # 원본 텍스트를 단어 집합으로 변환
        source_words = set(source_text.lower().split())

        for i, candidate_text in enumerate(candidate_texts):
            # 후보 텍스트를 단어 집합으로 변환
            candidate_words = set(candidate_text.lower().split())

            # 자카드 유사도 계산
            if source_words and candidate_words:
                intersection = len(source_words.intersection(candidate_words))
                union = len(source_words.union(candidate_words))
                similarity = intersection / union if union > 0 else 0.0
            else:
                similarity = 0.0

            candidate_patents[i]['similarity_score'] = similarity
            candidate_patents[i]['similarity_percentage'] = f"{similarity * 100:.2f}%"

    def _extract_text(self, patent: Dict) -> str:
        """
        특허 정보에서 분석용 텍스트를 추출합니다.

        Args:
            patent: 특허 정보 딕셔너리

        Returns:
            결합된 텍스트
        """
        parts = []

        # 제목 (가중치 3배)
        if patent.get('title'):
            parts.append(patent['title'] * 3)

        # 초록 (가중치 2배)
        if patent.get('abstract'):
            parts.append(patent['abstract'] * 2)

        # 청구항
        if patent.get('claims'):
            if isinstance(patent['claims'], list):
                parts.append(' '.join(patent['claims']))
            else:
                parts.append(str(patent['claims']))

        # 키워드 (가중치 2배)
        if patent.get('keywords'):
            keywords = patent['keywords']
            if isinstance(keywords, list):
                parts.append(' '.join(keywords) * 2)
            else:
                parts.append(str(keywords) * 2)

        text = ' '.join(parts)

        # 전처리
        text = self._preprocess_text(text)

        return text

    def _preprocess_text(self, text: str) -> str:
        """
        텍스트를 전처리합니다.

        Args:
            text: 원본 텍스트

        Returns:
            전처리된 텍스트
        """
        # 소문자 변환
        text = text.lower()

        # 특수 문자 제거 (한글, 영문, 숫자, 공백만 유지)
        text = re.sub(r'[^a-z가-힣0-9\s]', ' ', text)

        # 여러 공백을 하나로
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def calculate_keyword_overlap(
        self,
        source_patent: Dict,
        candidate_patent: Dict
    ) -> Tuple[float, List[str]]:
        """
        두 특허 간의 키워드 중복도를 계산합니다.

        Args:
            source_patent: 원본 특허
            candidate_patent: 비교 대상 특허

        Returns:
            (중복도 점수, 공통 키워드 리스트) 튜플
        """
        # 키워드 추출
        source_keywords = set(self._extract_keywords_from_text(
            self._extract_text(source_patent)
        ))
        candidate_keywords = set(self._extract_keywords_from_text(
            self._extract_text(candidate_patent)
        ))

        if not source_keywords or not candidate_keywords:
            return 0.0, []

        # 자카드 유사도 계산
        intersection = source_keywords.intersection(candidate_keywords)
        union = source_keywords.union(candidate_keywords)

        overlap_score = len(intersection) / len(union) if union else 0.0

        return overlap_score, list(intersection)

    def _extract_keywords_from_text(self, text: str, top_n: int = 20) -> List[str]:
        """
        텍스트에서 키워드를 추출합니다.

        Args:
            text: 입력 텍스트
            top_n: 추출할 키워드 수

        Returns:
            키워드 리스트
        """
        # 단어 분리
        words = re.findall(r'[a-z가-힣0-9]+', text.lower())

        # 빈도 계산
        word_freq = {}
        for word in words:
            if len(word) > 1:  # 1글자 단어 제외
                word_freq[word] = word_freq.get(word, 0) + 1

        # 빈도순 정렬
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # 상위 키워드 반환
        return [word for word, freq in sorted_words[:top_n]]

    def get_detailed_analysis(
        self,
        source_patent: Dict,
        candidate_patent: Dict
    ) -> Dict:
        """
        두 특허 간의 상세 분석을 수행합니다.

        Args:
            source_patent: 원본 특허
            candidate_patent: 비교 대상 특허

        Returns:
            상세 분석 결과 딕셔너리
        """
        # TF-IDF 유사도
        analyzed = self.analyze(source_patent, [candidate_patent])
        tfidf_score = analyzed[0]['similarity_score'] if analyzed else 0.0

        # 키워드 중복도
        keyword_overlap, common_keywords = self.calculate_keyword_overlap(
            source_patent,
            candidate_patent
        )

        return {
            'tfidf_similarity': tfidf_score,
            'keyword_overlap': keyword_overlap,
            'common_keywords': common_keywords,
            'overall_score': (tfidf_score + keyword_overlap) / 2,
            'patent_info': candidate_patent
        }
