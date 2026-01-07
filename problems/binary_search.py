"""
이진 탐색 (Binary Search)
난이도: Easy

문제: 정렬된 배열에서 target 값을 찾아 인덱스를 반환하라.
      없으면 -1을 반환한다.
"""

def binary_search(arr, target):
    """
    시간복잡도: O(log n)
    공간복잡도: O(1)
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def binary_search_recursive(arr, target, left=None, right=None):
    """
    재귀 방식
    시간복잡도: O(log n)
    공간복잡도: O(log n) - 재귀 호출 스택
    """
    if left is None:
        left = 0
    if right is None:
        right = len(arr) - 1

    if left > right:
        return -1

    mid = (left + right) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)


if __name__ == "__main__":
    test_cases = [
        ([1, 3, 5, 7, 9, 11], 7, 3),
        ([1, 3, 5, 7, 9, 11], 1, 0),
        ([1, 3, 5, 7, 9, 11], 11, 5),
        ([1, 3, 5, 7, 9, 11], 4, -1),
    ]

    print("=== Binary Search 테스트 ===\n")
    for arr, target, expected in test_cases:
        result = binary_search(arr, target)
        result_rec = binary_search_recursive(arr, target)
        status = "✓" if result == expected else "✗"
        print(f"{status} Array: {arr}, Target: {target}")
        print(f"  반복문: {result}, 재귀: {result_rec}, Expected: {expected}\n")
