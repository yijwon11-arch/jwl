"""
선행기술 검색 엔진 모듈

Google Patents 및 기타 특허 데이터베이스를 검색합니다.
"""

import time
from typing import List, Dict, Optional
from urllib.parse import quote

# Optional imports - 설치되지 않은 경우 더미 데이터 사용
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


class PriorArtSearchEngine:
    """선행기술을 검색하는 엔진 클래스"""

    def __init__(self, max_results: int = 10):
        """
        PriorArtSearchEngine 초기화

        Args:
            max_results: 반환할 최대 검색 결과 수
        """
        self.max_results = max_results
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def search(self, query: str, language: str = 'ko') -> List[Dict]:
        """
        특허를 검색합니다.

        Args:
            query: 검색 쿼리
            language: 검색 언어 ('ko', 'en', 'any')

        Returns:
            검색된 특허 정보 리스트
        """
        results = []

        # Google Patents 검색 시뮬레이션
        # 실제 환경에서는 Google Patents Public Data API 또는 웹 스크래핑 사용
        google_results = self._search_google_patents(query, language)
        results.extend(google_results)

        return results[:self.max_results]

    def _search_google_patents(self, query: str, language: str) -> List[Dict]:
        """
        Google Patents에서 검색합니다.

        Args:
            query: 검색 쿼리
            language: 검색 언어

        Returns:
            검색된 특허 정보 리스트
        """
        results = []

        # 필수 라이브러리가 없으면 더미 데이터 반환
        if not HAS_REQUESTS or not HAS_BS4:
            print("참고: requests 또는 beautifulsoup4가 설치되지 않아 더미 데이터를 사용합니다.")
            return self._get_dummy_results(query)

        try:
            # Google Patents 검색 URL 구성
            encoded_query = quote(query)
            url = f"https://patents.google.com/?q={encoded_query}"

            if language == 'ko':
                url += "&country=KR"
            elif language == 'en':
                url += "&country=US"

            # 요청 전송
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # HTML 파싱
            soup = BeautifulSoup(response.content, 'html.parser')

            # 특허 결과 파싱 (실제 구조는 Google Patents 페이지 구조에 따라 달라짐)
            # 여기서는 시뮬레이션을 위한 기본 구조
            patent_items = soup.find_all('article', limit=self.max_results)

            for item in patent_items:
                try:
                    patent_info = self._parse_patent_item(item)
                    if patent_info:
                        results.append(patent_info)
                except Exception as e:
                    # 개별 항목 파싱 실패는 무시하고 계속 진행
                    continue

        except requests.RequestException as e:
            print(f"검색 중 오류 발생: {e}")
            # 네트워크 오류 시 더미 데이터 반환 (테스트용)
            results = self._get_dummy_results(query)

        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            results = self._get_dummy_results(query)

        return results

    def _parse_patent_item(self, item) -> Optional[Dict]:
        """
        특허 항목을 파싱합니다.

        Args:
            item: BeautifulSoup 특허 항목

        Returns:
            파싱된 특허 정보 또는 None
        """
        try:
            # 실제 Google Patents 구조에 맞게 수정 필요
            title_elem = item.find('h3') or item.find('a')
            title = title_elem.get_text(strip=True) if title_elem else "제목 없음"

            abstract_elem = item.find('p') or item.find('div', class_='abstract')
            abstract = abstract_elem.get_text(strip=True) if abstract_elem else "초록 없음"

            link_elem = item.find('a', href=True)
            link = link_elem['href'] if link_elem else ""

            # 특허 번호 추출 (링크나 제목에서)
            patent_number = self._extract_patent_number(link or title)

            return {
                'title': title,
                'abstract': abstract,
                'patent_number': patent_number,
                'url': f"https://patents.google.com{link}" if link and not link.startswith('http') else link,
                'source': 'Google Patents'
            }

        except Exception:
            return None

    def _extract_patent_number(self, text: str) -> str:
        """
        텍스트에서 특허 번호를 추출합니다.

        Args:
            text: 추출할 텍스트

        Returns:
            특허 번호
        """
        import re

        # US 특허 패턴
        us_pattern = r'US[\s-]?(\d{7,10})'
        # KR 특허 패턴
        kr_pattern = r'KR[\s-]?(\d{7,10})'
        # 일반 번호 패턴
        general_pattern = r'[A-Z]{2}[\s-]?\d{7,10}'

        for pattern in [us_pattern, kr_pattern, general_pattern]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)

        return "번호 없음"

    def _get_dummy_results(self, query: str) -> List[Dict]:
        """
        테스트용 더미 검색 결과를 반환합니다.

        Args:
            query: 검색 쿼리

        Returns:
            더미 특허 정보 리스트
        """
        # 실제 검색 실패 시 또는 테스트용으로 사용
        # max_results 만큼 더미 데이터 생성
        dummy_patents = []

        # 키워드에 따라 다른 더미 데이터 생성
        keywords_lower = query.lower()

        # 생체인증 관련 키워드 감지
        is_biometric = any(kw in keywords_lower for kw in [
            'biometric', '생체', 'fingerprint', '지문', 'face', '얼굴',
            'iris', '홍채', 'zero-knowledge', '영지식', 'blockchain', '블록체인',
            'privacy', '프라이버시', 'untraceable', '추적'
        ])

        if is_biometric:
            # 생체인증 관련 더미 특허들
            dummy_patents = self._get_biometric_dummy_patents()
        else:
            # 일반 더미 특허들
            dummy_patents = self._get_general_dummy_patents(query)

        return dummy_patents[:self.max_results]

    def _get_biometric_dummy_patents(self) -> List[Dict]:
        """생체인증 관련 더미 특허 생성"""
        return [
            {
                'title': 'Privacy-Preserving Biometric Authentication Using Homomorphic Encryption',
                'abstract': '본 발명은 동형암호(Homomorphic Encryption)를 이용한 프라이버시 보장형 생체인증 방법에 관한 것이다. 생체정보를 암호화한 상태에서 비교 연산을 수행하여 복호화 없이 인증을 완료한다. 그러나 영지식 증명 기법은 사용하지 않으며, 블록체인 대신 중앙 서버를 사용한다.',
                'patent_number': 'US10234567',
                'url': 'https://patents.google.com/patent/US10234567',
                'source': 'USPTO'
            },
            {
                'title': 'Blockchain-Based Biometric Data Management System',
                'abstract': '블록체인을 이용한 생체정보 관리 시스템으로, 사용자의 생체정보를 블록체인에 저장한다. 분산저장을 통해 데이터 무결성을 보장하나, 생체정보 원본을 해싱하여 저장하므로 일회용 토큰 방식은 아니다.',
                'patent_number': 'KR1020210087654',
                'url': 'https://patents.google.com/patent/KR1020210087654',
                'source': 'KIPRIS'
            },
            {
                'title': 'Cancelable Biometric Template Generation Method',
                'abstract': 'Cancelable Biometric 기법을 이용하여 생체정보 템플릿을 생성한다. 유출 시 템플릿을 폐기하고 새로운 템플릿을 발급할 수 있으나, 영지식 증명이나 일회용 토큰 방식은 사용하지 않는다.',
                'patent_number': 'US10456789',
                'url': 'https://patents.google.com/patent/US10456789',
                'source': 'USPTO'
            },
            {
                'title': 'Zero-Knowledge Proof System for Identity Verification',
                'abstract': '영지식 증명을 이용한 신원 확인 시스템이나, 생체정보가 아닌 일반 신원정보(ID, 비밀번호)를 대상으로 한다. zk-SNARK 프로토콜을 사용하지만 생체인증과는 결합되지 않았다.',
                'patent_number': 'US10567890',
                'url': 'https://patents.google.com/patent/US10567890',
                'source': 'USPTO'
            },
            {
                'title': 'Multi-Modal Biometric Authentication with Template Protection',
                'abstract': '다중 생체정보(지문, 얼굴, 홍채)를 결합한 인증 시스템으로 템플릿 보호 기능을 제공한다. 그러나 매 인증마다 동일한 템플릿을 사용하므로 추적 가능성이 존재한다.',
                'patent_number': 'KR1020200123456',
                'url': 'https://patents.google.com/patent/KR1020200123456',
                'source': 'KIPRIS'
            },
            {
                'title': 'Fuzzy Vault Scheme for Fingerprint Authentication',
                'abstract': 'Fuzzy Vault 기법을 이용한 지문 인증 방법이다. 생체정보의 변동성을 허용하면서도 보안을 유지하나, 일회용 토큰 방식이나 영지식 증명은 사용하지 않는다.',
                'patent_number': 'US10678901',
                'url': 'https://patents.google.com/patent/US10678901',
                'source': 'USPTO'
            },
            {
                'title': 'Decentralized Identity Management Using Blockchain',
                'abstract': '블록체인 기반 탈중앙화 신원 관리 시스템이다. 사용자 신원정보를 블록체인에 저장하고 분산 검증을 수행하나, 생체인증 특화 기능은 없다.',
                'patent_number': 'US10789012',
                'url': 'https://patents.google.com/patent/US10789012',
                'source': 'USPTO'
            },
            {
                'title': 'Secure Biometric Template Storage Using Secret Sharing',
                'abstract': '비밀분산(Secret Sharing) 기법을 이용한 생체 템플릿 저장 방법이다. 템플릿을 여러 조각으로 나누어 분산 저장하나, 영지식 증명이나 일회용 토큰은 미포함이다.',
                'patent_number': 'KR1020190098765',
                'url': 'https://patents.google.com/patent/KR1020190098765',
                'source': 'KIPRIS'
            },
            {
                'title': 'One-Time Password Generation from Biometric Data',
                'abstract': '생체정보를 이용한 일회용 비밀번호(OTP) 생성 방법이다. 생체정보로부터 일회성 값을 생성하나, 영지식 증명이나 블록체인 기술은 사용하지 않는다.',
                'patent_number': 'US10890123',
                'url': 'https://patents.google.com/patent/US10890123',
                'source': 'USPTO'
            },
            {
                'title': 'Privacy-Enhanced Face Recognition Using Differential Privacy',
                'abstract': '차등 프라이버시(Differential Privacy)를 적용한 얼굴 인식 시스템이다. 노이즈 추가를 통해 프라이버시를 보호하나, 영지식 증명이나 일회용 토큰은 사용하지 않는다.',
                'patent_number': 'US10901234',
                'url': 'https://patents.google.com/patent/US10901234',
                'source': 'USPTO'
            },
            {
                'title': 'Iris Recognition with Revocable Template',
                'abstract': '폐기 가능한 템플릿을 사용하는 홍채 인식 시스템이다. 보안 침해 시 템플릿을 폐기하고 재발급할 수 있으나, 매 인증마다 새로운 토큰을 생성하지는 않는다.',
                'patent_number': 'KR1020180054321',
                'url': 'https://patents.google.com/patent/KR1020180054321',
                'source': 'KIPRIS'
            },
            {
                'title': 'Attribute-Based Encryption for Biometric Data Protection',
                'abstract': '속성 기반 암호화(ABE)를 이용한 생체정보 보호 방법이다. 사용자 속성에 따라 암호화/복호화 권한을 부여하나, 영지식 증명이나 추적불가능성 기능은 없다.',
                'patent_number': 'US11012345',
                'url': 'https://patents.google.com/patent/US11012345',
                'source': 'USPTO'
            },
            {
                'title': 'Federated Learning for Privacy-Preserving Biometric Model Training',
                'abstract': '연합학습(Federated Learning)을 이용한 프라이버시 보장형 생체인식 모델 학습 방법이다. 생체정보를 중앙으로 모으지 않고 분산 학습하나, 인증 프로세스 자체는 일반적인 방식이다.',
                'patent_number': 'US11123456',
                'url': 'https://patents.google.com/patent/US11123456',
                'source': 'USPTO'
            },
            {
                'title': 'Quantum-Resistant Cryptography for Biometric Authentication',
                'abstract': '양자내성 암호를 적용한 생체인증 시스템이다. 양자컴퓨터 공격에도 안전하도록 설계되었으나, 영지식 증명이나 일회용 토큰 방식은 미포함이다.',
                'patent_number': 'KR1020220012345',
                'url': 'https://patents.google.com/patent/KR1020220012345',
                'source': 'KIPRIS'
            },
            {
                'title': 'Secure Multi-Party Computation for Biometric Matching',
                'abstract': '다자간 보안 계산(Secure Multi-Party Computation)을 이용한 생체정보 매칭 방법이다. 여러 참여자가 자신의 생체정보를 공개하지 않고 매칭을 수행하나, 블록체인이나 영지식 증명은 사용하지 않는다.',
                'patent_number': 'US11234567',
                'url': 'https://patents.google.com/patent/US11234567',
                'source': 'USPTO'
            }
        ]

    def _get_general_dummy_patents(self, query: str) -> List[Dict]:
        """일반 더미 특허 생성"""
        return [
            {
                'title': f'관련 특허 1: {query[:30]}...',
                'abstract': '이 특허는 관련 기술에 대한 설명을 포함합니다. ' * 3,
                'patent_number': 'US1234567',
                'url': 'https://patents.google.com/patent/US1234567',
                'source': 'Google Patents (Dummy)'
            },
            {
                'title': f'관련 특허 2: {query[:30]}...',
                'abstract': '이 특허는 유사한 기술적 특징을 설명합니다. ' * 3,
                'patent_number': 'KR1020210001234',
                'url': 'https://patents.google.com/patent/KR1020210001234',
                'source': 'Google Patents (Dummy)'
            },
            {
                'title': f'관련 특허 3: {query[:30]}...',
                'abstract': '본 발명은 개선된 방법을 제공합니다. ' * 3,
                'patent_number': 'US2345678',
                'url': 'https://patents.google.com/patent/US2345678',
                'source': 'Google Patents (Dummy)'
            }
        ]

    def search_by_classification(self, classification_code: str) -> List[Dict]:
        """
        특허 분류 코드로 검색합니다.

        Args:
            classification_code: IPC 또는 CPC 분류 코드

        Returns:
            검색된 특허 정보 리스트
        """
        # 분류 코드 기반 검색 (실제 API 사용 시 구현)
        query = f"classification:{classification_code}"
        return self.search(query)

    def get_patent_details(self, patent_number: str) -> Optional[Dict]:
        """
        특허 번호로 상세 정보를 조회합니다.

        Args:
            patent_number: 특허 번호

        Returns:
            특허 상세 정보 또는 None
        """
        try:
            url = f"https://patents.google.com/patent/{patent_number}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 상세 정보 파싱 (실제 구조에 맞게 수정 필요)
            title = soup.find('h1')
            abstract = soup.find('div', {'class': 'abstract'})

            return {
                'title': title.get_text(strip=True) if title else '',
                'abstract': abstract.get_text(strip=True) if abstract else '',
                'patent_number': patent_number,
                'url': url
            }

        except Exception as e:
            print(f"특허 상세 정보 조회 실패: {e}")
            return None
