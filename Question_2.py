class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def maxPathSum(self, root):
        self.max_sum = float('-inf')

        def dfs(node):
            if not node:
                return 0
            
            left_gain = max(dfs(node.left), 0)
            right_gain = max(dfs(node.right), 0)

            current_sum = node.val + left_gain + right_gain
            self.max_sum = max(self.max_sum, current_sum)

            return node.val + max(left_gain, right_gain)

        dfs(root)
        return self.max_sum


#  Example 1 Tree 
root1 = TreeNode(1)
root1.left = TreeNode(2)
root1.right = TreeNode(3)

sol1 = Solution()
result1 = sol1.maxPathSum(root1)

print("Example 1")
print("OUTPUT:")
print("Maximum Net Power Generation:", result1)
print("Explanation: 2 + 1 + 3 = 6")
print("------\n")


#  Example 2 Tree 
root2 = TreeNode(-10)
root2.left = TreeNode(9)
root2.right = TreeNode(20)
root2.right.left = TreeNode(15)
root2.right.right = TreeNode(7)

sol2 = Solution()
result2 = sol2.maxPathSum(root2)

print("Example 2")
print("OUTPUT:")
print("Maximum Net Power Generation:", result2)
print("Explanation: 15 + 20 + 7 = 42 (Excludes -10)")
