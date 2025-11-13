"""
특허 데이터베이스 관리 모듈
Patent Database Management Module
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import os

from ..models.patent import Patent
from ..models.search_result import SearchResult, SearchMetadata


class PatentDatabase:
    """특허 데이터베이스 관리 클래스"""

    def __init__(self, db_path: str = "data/patents.db"):
        """
        데이터베이스 초기화

        Args:
            db_path: 데이터베이스 파일 경로
        """
        # 디렉토리가 없으면 생성
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_database()

    def _initialize_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # 특허 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                application_number TEXT,
                application_date TEXT,
                publication_number TEXT,
                publication_date TEXT,
                registration_number TEXT,
                registration_date TEXT,
                abstract TEXT,
                description TEXT,
                claims_text TEXT,
                status TEXT,
                country TEXT,
                priority_date TEXT,
                priority_number TEXT,
                family_id TEXT,
                url TEXT,
                source TEXT,
                created_at TEXT,
                updated_at TEXT,
                data JSON
            )
        """)

        # 검색 이력 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                search_id TEXT PRIMARY KEY,
                query JSON NOT NULL,
                source TEXT,
                total_results INTEGER,
                retrieved_count INTEGER,
                search_time REAL,
                timestamp TEXT,
                metadata JSON
            )
        """)

        # 검색 결과-특허 연결 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_id TEXT,
                patent_id TEXT,
                rank INTEGER,
                FOREIGN KEY (search_id) REFERENCES search_history(search_id),
                FOREIGN KEY (patent_id) REFERENCES patents(id)
            )
        """)

        # 인덱스 생성
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patent_app_number
            ON patents(application_number)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patent_reg_number
            ON patents(registration_number)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patent_country
            ON patents(country)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_search_timestamp
            ON search_history(timestamp)
        """)

        self.conn.commit()

    def save_patent(self, patent: Patent) -> bool:
        """
        특허 저장

        Args:
            patent: Patent 객체

        Returns:
            저장 성공 여부
        """
        try:
            cursor = self.conn.cursor()

            # 특허 데이터를 JSON으로 직렬화
            patent_data = patent.to_dict()

            cursor.execute("""
                INSERT OR REPLACE INTO patents (
                    id, title, application_number, application_date,
                    publication_number, publication_date,
                    registration_number, registration_date,
                    abstract, description, claims_text,
                    status, country, priority_date, priority_number,
                    family_id, url, source, created_at, updated_at, data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patent.id,
                patent.title,
                patent.application_number,
                patent.application_date,
                patent.publication_number,
                patent.publication_date,
                patent.registration_number,
                patent.registration_date,
                patent.abstract,
                patent.description,
                patent.claims_text,
                patent.status,
                patent.country,
                patent.priority_date,
                patent.priority_number,
                patent.family_id,
                patent.url,
                patent.source,
                patent.created_at,
                datetime.now().isoformat(),
                json.dumps(patent_data, ensure_ascii=False)
            ))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"특허 저장 오류: {str(e)}")
            return False

    def save_patents(self, patents: List[Patent]) -> int:
        """
        여러 특허 일괄 저장

        Args:
            patents: Patent 객체 리스트

        Returns:
            저장된 특허 개수
        """
        count = 0
        for patent in patents:
            if self.save_patent(patent):
                count += 1
        return count

    def get_patent(self, patent_id: str) -> Optional[Patent]:
        """
        특허 조회

        Args:
            patent_id: 특허 ID

        Returns:
            Patent 객체 또는 None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT data FROM patents WHERE id = ?", (patent_id,))
            row = cursor.fetchone()

            if row:
                patent_data = json.loads(row['data'])
                return Patent.from_dict(patent_data)

            return None

        except Exception as e:
            print(f"특허 조회 오류: {str(e)}")
            return None

    def search_patents(self, **criteria) -> List[Patent]:
        """
        특허 검색

        Args:
            **criteria: 검색 조건 (title, country, status 등)

        Returns:
            Patent 객체 리스트
        """
        try:
            cursor = self.conn.cursor()

            query = "SELECT data FROM patents WHERE 1=1"
            params = []

            if 'title' in criteria:
                query += " AND title LIKE ?"
                params.append(f"%{criteria['title']}%")

            if 'country' in criteria:
                query += " AND country = ?"
                params.append(criteria['country'])

            if 'status' in criteria:
                query += " AND status = ?"
                params.append(criteria['status'])

            if 'source' in criteria:
                query += " AND source = ?"
                params.append(criteria['source'])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            patents = []
            for row in rows:
                patent_data = json.loads(row['data'])
                patents.append(Patent.from_dict(patent_data))

            return patents

        except Exception as e:
            print(f"특허 검색 오류: {str(e)}")
            return []

    def save_search_result(self, search_result: SearchResult) -> bool:
        """
        검색 결과 저장

        Args:
            search_result: SearchResult 객체

        Returns:
            저장 성공 여부
        """
        try:
            cursor = self.conn.cursor()

            # 검색 이력 저장
            metadata = search_result.metadata
            cursor.execute("""
                INSERT OR REPLACE INTO search_history (
                    search_id, query, source, total_results,
                    retrieved_count, search_time, timestamp, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                search_result.search_id,
                json.dumps(metadata.query, ensure_ascii=False),
                metadata.source,
                metadata.total_results,
                metadata.retrieved_count,
                metadata.search_time,
                metadata.timestamp,
                json.dumps(asdict(metadata), ensure_ascii=False)
            ))

            # 특허 저장 및 연결
            for rank, patent in enumerate(search_result.patents, 1):
                self.save_patent(patent)

                cursor.execute("""
                    INSERT INTO search_results (search_id, patent_id, rank)
                    VALUES (?, ?, ?)
                """, (search_result.search_id, patent.id, rank))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"검색 결과 저장 오류: {str(e)}")
            self.conn.rollback()
            return False

    def get_search_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        검색 이력 조회

        Args:
            limit: 최대 결과 개수

        Returns:
            검색 이력 리스트
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM search_history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            history = []

            for row in rows:
                history.append({
                    'search_id': row['search_id'],
                    'query': json.loads(row['query']),
                    'source': row['source'],
                    'total_results': row['total_results'],
                    'retrieved_count': row['retrieved_count'],
                    'search_time': row['search_time'],
                    'timestamp': row['timestamp']
                })

            return history

        except Exception as e:
            print(f"검색 이력 조회 오류: {str(e)}")
            return []

    def get_search_result_by_id(self, search_id: str) -> Optional[SearchResult]:
        """
        검색 ID로 검색 결과 조회

        Args:
            search_id: 검색 ID

        Returns:
            SearchResult 객체 또는 None
        """
        try:
            cursor = self.conn.cursor()

            # 검색 메타데이터 조회
            cursor.execute("""
                SELECT * FROM search_history WHERE search_id = ?
            """, (search_id,))
            history_row = cursor.fetchone()

            if not history_row:
                return None

            metadata = SearchMetadata(
                query=json.loads(history_row['query']),
                total_results=history_row['total_results'],
                retrieved_count=history_row['retrieved_count'],
                search_time=history_row['search_time'],
                source=history_row['source'],
                timestamp=history_row['timestamp']
            )

            # 검색 결과 특허 조회
            cursor.execute("""
                SELECT p.data
                FROM search_results sr
                JOIN patents p ON sr.patent_id = p.id
                WHERE sr.search_id = ?
                ORDER BY sr.rank
            """, (search_id,))

            patent_rows = cursor.fetchall()
            patents = []

            for row in patent_rows:
                patent_data = json.loads(row['data'])
                patents.append(Patent.from_dict(patent_data))

            return SearchResult(
                metadata=metadata,
                patents=patents,
                search_id=search_id
            )

        except Exception as e:
            print(f"검색 결과 조회 오류: {str(e)}")
            return None

    def delete_patent(self, patent_id: str) -> bool:
        """특허 삭제"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM patents WHERE id = ?", (patent_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"특허 삭제 오류: {str(e)}")
            return False

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()


# Helper function import 추가
from dataclasses import asdict
