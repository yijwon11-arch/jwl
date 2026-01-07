"""
스택 (Stack) 자료구조
LIFO (Last In First Out)
"""

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        """스택에 요소 추가"""
        self.items.append(item)

    def pop(self):
        """스택에서 요소 제거 및 반환"""
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.pop()

    def peek(self):
        """스택의 최상단 요소 확인 (제거하지 않음)"""
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items[-1]

    def is_empty(self):
        """스택이 비어있는지 확인"""
        return len(self.items) == 0

    def size(self):
        """스택의 크기 반환"""
        return len(self.items)

    def __str__(self):
        return f"Stack({self.items})"


def is_balanced_parentheses(s):
    """
    괄호 균형 검사 (스택 활용 예시)

    예: "(())" -> True
        "(()" -> False
    """
    stack = Stack()
    pairs = {'(': ')', '[': ']', '{': '}'}

    for char in s:
        if char in pairs:
            stack.push(char)
        elif char in pairs.values():
            if stack.is_empty():
                return False
            if pairs[stack.pop()] != char:
                return False

    return stack.is_empty()


if __name__ == "__main__":
    print("=== Stack 테스트 ===\n")

    # 기본 스택 동작
    stack = Stack()
    print("빈 스택:", stack)

    stack.push(1)
    stack.push(2)
    stack.push(3)
    print("요소 추가 후:", stack)

    print(f"peek(): {stack.peek()}")
    print(f"pop(): {stack.pop()}")
    print("pop 후:", stack)

    # 괄호 균형 검사
    print("\n=== 괄호 균형 검사 ===\n")
    test_cases = [
        ("()", True),
        ("()[]{}", True),
        ("(]", False),
        ("([)]", False),
        ("{[]}", True),
    ]

    for s, expected in test_cases:
        result = is_balanced_parentheses(s)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{s}' -> {result} (expected: {expected})")
