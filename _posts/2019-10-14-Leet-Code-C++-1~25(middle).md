---
layout: post
title: Leet Code C++ 1~25 (middle)
tags: C++ CS
categories: C++ 
---

### 2、两数相加

题目描述

> 给出两个 **非空** 的链表用来表示两个非负的整数。其中，它们各自的位数是按照 逆序 的方式存储的，并且它们的每个节点只能存储 一位 数字。
>
> 如果，我们将这两个数相加起来，则会返回一个新的链表来表示它们的和。
>
> 您可以假设除了数字 0 之外，这两个数都不会以 0 开头。
>

**示例：**

```
输入：(2 -> 4 -> 3) + (5 -> 6 -> 4)
输出：7 -> 0 -> 8
原因：342 + 465 = 807
```

c++ code

```c++
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode(int x) : val(x), next(NULL) {}
 * };
 */
class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        int tempVal = 0;
        ListNode *temp, *head = l1;
        ListNode *end = new ListNode(0);
        
        while (l1 != NULL && l2 != NULL)
        {
            l1->val = l1->val + l2->val;
            temp = l1;
            l1 = l1->next;
            l2 = l2->next;
        }
        
        if (l1 == NULL && l2 != NULL)
            temp->next = l2;
        
        l1 = head;
        for (; l1->next != NULL;)
        {
            if (l1->val >= 10)
            {
                tempVal = l1->val;
                l1->val = l1->val % 10;
                l1->next->val = tempVal / 10 + l1->next->val;
                l1 = l1->next;
            }
            else
            {
                l1 = l1->next;
            }
        }
        
        if (l1->val >= 10)
        {
            tempVal = l1->val;
            l1->val = l1->val % 10;
            end->val = tempVal / 10;
            l1->next = end;
        }
        
        return head;
    }
};
```

<br/>



### 3、无重复字符的最长子串

题目描述

> 给定一个字符串，请你找出其中不含有重复字符的 **最长子串** 的长度。

**示例 1:**

```
输入: "abcabcbb"
输出: 3 
解释: 因为无重复字符的最长子串是 "abc"，所以其长度为 3。
```

**示例 2:**

```
输入: "bbbbb"
输出: 1
解释: 因为无重复字符的最长子串是 "b"，所以其长度为 1。
```

**示例 3:**

```
输入: "pwwkew"
输出: 3
解释: 因为无重复字符的最长子串是 "wke"，所以其长度为 3。
	请注意，你的答案必须是 子串 的长度，"pwke" 是一个子序列，不是子串。
```

c++ code

```

```

