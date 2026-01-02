#!/usr/bin/env python3
"""
GitHub 리포지토리를 공개로 전환하는 스크립트
"""

import subprocess
import json
import sys

def change_repo_visibility():
    """리포지토리를 공개로 변경"""

    # GitHub CLI를 사용하여 변경 시도
    try:
        cmd = [
            'gh', 'repo', 'edit',
            'yijwon11-arch/jwl',
            '--visibility', 'public'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print("✓ 리포지토리가 성공적으로 공개로 전환되었습니다!")
            print(result.stdout)
            return True
        else:
            print(f"오류: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("오류: 명령 실행 시간 초과")
        return False
    except FileNotFoundError:
        print("오류: GitHub CLI (gh)가 설치되지 않았습니다.")
        print("\n대신 다음 방법을 사용하세요:")
        print("1. https://github.com/yijwon11-arch/jwl/settings 방문")
        print("2. 페이지 하단 'Danger Zone'으로 스크롤")
        print("3. 'Change visibility' 클릭")
        print("4. 'Change to public' 선택")
        return False
    except Exception as e:
        print(f"예상치 못한 오류: {e}")
        return False

if __name__ == '__main__':
    success = change_repo_visibility()
    sys.exit(0 if success else 1)
