"""
LeetCode #1: Two Sum
난이도: Easy

문제: 정수 배열 nums와 목표값 target이 주어졌을 때,
      합이 target이 되는 두 수의 인덱스를 반환하라.
"""

def two_sum(nums, target):
    """
    시간복잡도: O(n)
    공간복잡도: O(n)
    """
    seen = {}

    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i

    return []


def two_sum_brute_force(nums, target):
    """
    브루트포스 방식 (비교용)
    시간복잡도: O(n^2)
    """
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


if __name__ == "__main__":
    # 테스트 케이스
    test_cases = [
        ([2, 7, 11, 15], 9, [0, 1]),
        ([3, 2, 4], 6, [1, 2]),
        ([3, 3], 6, [0, 1]),
    ]

    print("=== Two Sum 테스트 ===\n")
    for nums, target, expected in test_cases:
        result = two_sum(nums, target)
        status = "✓" if result == expected else "✗"
        print(f"{status} Input: {nums}, Target: {target}")
        print(f"  Expected: {expected}, Got: {result}\n")
