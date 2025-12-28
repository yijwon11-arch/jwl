"""
파일 파싱 모듈

다양한 형식의 파일(PDF, TXT, DOCX, 이미지 등)에서 특허 정보를 추출합니다.
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional

# Optional imports
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False

try:
    from docx import Document
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


class FileParser:
    """다양한 형식의 파일에서 특허 정보를 추출하는 클래스"""

    def __init__(self):
        """FileParser 초기화"""
        self.supported_formats = {
            '.json': self._parse_json,
            '.txt': self._parse_text,
            '.pdf': self._parse_pdf,
            '.docx': self._parse_docx,
            '.doc': self._parse_docx,
            '.png': self._parse_image,
            '.jpg': self._parse_image,
            '.jpeg': self._parse_image,
            '.tiff': self._parse_image,
        }

    def parse_file(self, file_path: str) -> Dict:
        """
        파일을 파싱하여 특허 정보를 추출합니다.

        Args:
            file_path: 파일 경로

        Returns:
            특허 정보 딕셔너리

        Raises:
            ValueError: 지원하지 않는 파일 형식
            FileNotFoundError: 파일이 존재하지 않음
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        file_extension = path.suffix.lower()

        if file_extension not in self.supported_formats:
            raise ValueError(
                f"지원하지 않는 파일 형식입니다: {file_extension}\n"
                f"지원 형식: {', '.join(self.supported_formats.keys())}"
            )

        parser_func = self.supported_formats[file_extension]
        return parser_func(file_path)

    def _parse_json(self, file_path: str) -> Dict:
        """JSON 파일 파싱"""
        import json

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return {
            'title': data.get('title', ''),
            'abstract': data.get('abstract', ''),
            'claims': data.get('claims', []),
            'keywords': data.get('keywords', [])
        }

    def _parse_text(self, file_path: str) -> Dict:
        """텍스트 파일 파싱"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 텍스트에서 특허 정보 추출
        return self._extract_patent_info_from_text(content)

    def _parse_pdf(self, file_path: str) -> Dict:
        """PDF 파일 파싱"""
        if not HAS_PYPDF2:
            raise ImportError(
                "PDF 파일을 파싱하려면 PyPDF2가 필요합니다.\n"
                "설치: pip install PyPDF2"
            )

        text = ""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise ValueError(f"PDF 파싱 중 오류 발생: {e}")

        return self._extract_patent_info_from_text(text)

    def _parse_docx(self, file_path: str) -> Dict:
        """DOCX 파일 파싱"""
        if not HAS_DOCX:
            raise ImportError(
                "DOCX 파일을 파싱하려면 python-docx가 필요합니다.\n"
                "설치: pip install python-docx"
            )

        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"DOCX 파싱 중 오류 발생: {e}")

        return self._extract_patent_info_from_text(text)

    def _parse_image(self, file_path: str) -> Dict:
        """이미지 파일 파싱 (OCR)"""
        if not HAS_OCR:
            raise ImportError(
                "이미지 파일을 파싱하려면 pytesseract와 Pillow가 필요합니다.\n"
                "설치: pip install pytesseract Pillow\n"
                "또한 Tesseract OCR 엔진 설치 필요: https://github.com/tesseract-ocr/tesseract"
            )

        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='kor+eng')
        except Exception as e:
            raise ValueError(f"이미지 OCR 중 오류 발생: {e}")

        return self._extract_patent_info_from_text(text)

    def _extract_patent_info_from_text(self, text: str) -> Dict:
        """
        텍스트에서 특허 정보를 추출합니다.

        Args:
            text: 입력 텍스트

        Returns:
            특허 정보 딕셔너리
        """
        # 기본 구조
        patent_info = {
            'title': '',
            'abstract': '',
            'claims': [],
            'keywords': []
        }

        # 제목 추출
        title = self._extract_title(text)
        if title:
            patent_info['title'] = title

        # 초록 추출
        abstract = self._extract_abstract(text)
        if abstract:
            patent_info['abstract'] = abstract

        # 청구항 추출
        claims = self._extract_claims(text)
        if claims:
            patent_info['claims'] = claims

        # 제목이나 초록이 없으면 전체 텍스트를 초록으로 사용
        if not patent_info['title'] and not patent_info['abstract']:
            # 첫 줄을 제목으로
            lines = text.strip().split('\n')
            if lines:
                patent_info['title'] = lines[0][:200]
                patent_info['abstract'] = '\n'.join(lines[1:])[:2000]

        return patent_info

    def _extract_title(self, text: str) -> str:
        """텍스트에서 제목 추출"""
        # 패턴: "제목:", "Title:", "발명의 명칭" 등
        patterns = [
            r'(?:제목|Title|발명의\s*명칭|명칭)\s*[:：]\s*(.+)',
            r'^(.+?)(?:\n|$)',  # 첫 줄
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if len(title) > 10 and len(title) < 300:  # 적절한 길이
                    return title

        return ""

    def _extract_abstract(self, text: str) -> str:
        """텍스트에서 초록 추출"""
        # 패턴: "초록:", "Abstract:", "요약" 등
        patterns = [
            r'(?:초록|Abstract|요약|발명의\s*내용)\s*[:：]\s*(.+?)(?=\n\n|청구항|Claims|$)',
            r'(?:본\s*발명은|This\s+invention)\s*(.+?)(?=\n\n|청구항|Claims|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                if len(abstract) > 50:  # 최소 길이
                    return abstract[:2000]  # 최대 2000자

        return ""

    def _extract_claims(self, text: str) -> list:
        """텍스트에서 청구항 추출"""
        claims = []

        # 패턴: "청구항 1:", "Claim 1:", "1." 등
        patterns = [
            r'(?:청구항|Claim)\s*(\d+)\s*[:：]\s*(.+?)(?=(?:청구항|Claim)\s*\d+|$)',
            r'(?:^|\n)(\d+)\.\s*(.+?)(?=\n\d+\.|$)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            for match in matches:
                claim_text = match.group(2).strip()
                if claim_text and len(claim_text) > 10:
                    claims.append(claim_text[:1000])  # 각 청구항 최대 1000자

        return claims[:20]  # 최대 20개 청구항

    def get_supported_formats(self) -> list:
        """지원하는 파일 형식 목록 반환"""
        return list(self.supported_formats.keys())

    def check_dependencies(self) -> Dict[str, bool]:
        """
        선택적 의존성 설치 여부 확인

        Returns:
            {'format': installed} 딕셔너리
        """
        return {
            'pdf': HAS_PYPDF2,
            'docx': HAS_DOCX,
            'image_ocr': HAS_OCR
        }
