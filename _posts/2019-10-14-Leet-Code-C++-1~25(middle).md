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

<br/>



### 8、字符串转换整数（atoi）

题目描述

> 请你来实现一个 atoi 函数，使其能将字符串转换成整数。
>
> 首先，该函数会根据需要丢弃无用的开头空格字符，直到寻找到第一个非空格的字符为止。
>
> 当我们寻找到的第一个非空字符为正或者负号时，则将该符号与之后面尽可能多的连续数字组合起来，作为该整数的正负号；假如第一个非空字符是数字，则直接将其与之后连续的数字字符组合起来，形成整数。
>
> 该字符串除了有效的整数部分之后也可能会存在多余的字符，这些字符可以被忽略，它们对于函数不应该造成影响。
>
> 注意：假如该字符串中的第一个非空格字符不是一个有效整数字符、字符串为空或字符串仅包含空白字符时，则你的函数不需要进行转换。
>
> 在任何情况下，若函数不能进行有效的转换时，请返回 0。
>

**说明：**

假设我们的环境只能存储 32 位大小的有符号整数，那么其数值范围为 [−231,  231 − 1]。如果数值超过这个范围，请返回  INT_MAX (231 − 1) 或 INT_MIN (−231) 。

**示例 1:**

```
输入: "42"
输出: 42
```

**示例 2:**

```
输入: "   -42"
输出: -42
解释: 第一个非空白字符为 '-', 它是一个负号。
     我们尽可能将负号与后面所有连续出现的数字组合起来，最后得到 -42 。
```

**示例 3:**

```
输入: "4193 with words"
输出: 4193
解释: 转换截止于数字 '3' ，因为它的下一个字符不为数字。
```

**示例 4:**

```
输入: "words and 987"
输出: 0
解释: 第一个非空字符是 'w', 但它不是数字或正、负号。
     因此无法执行有效的转换。
```

**示例 5:**

```
输入: "-91283472332"
输出: -2147483648
解释: 数字 "-91283472332" 超过 32 位有符号整数范围。 
     因此返回 INT_MIN (−231) 。
```

c++ code

```c++
class Solution {
public:
    int myAtoi(string str) {
        int i = 0, flag = 0;
        long ret = 0;
        
        if (str.empty())
            return 0;
        
        for (i = 0; i < str.size(); i++)
        {         
            if (str[i] == ' ' || str[i] == '\t')
                continue;
            
            if (str[i] == ' ' || str[i] == '\t')
                continue;
            
            if ((str[i] == '+' || str[i] == '-') && !isdigit(str[i + 1]))
                return ret;
            
            if (str[i] == '+')
                flag = 0;
            else if (str[i] == '-')
                flag = 1;
            else if (isdigit(str[i]) && isdigit(str[i + 1]))
            {
                if (!flag)
                {
                    ret = 10 * ret + (str[i] - 48);
                    if (ret >= INT_MAX)
                        return INT_MAX;
                }
                else
                {
                    ret = 10 * ret - (str[i] - 48);
                    if (ret <= INT_MIN)
                        return INT_MIN;
                }
            }
            else if (isdigit(str[i]) && !isdigit(str[i + 1]))
            {
                if (!flag)
                {
                    ret = 10 * ret + (str[i] - 48);
                    if (ret >= INT_MAX)
                        return INT_MAX;
                }
                else
                {
                    ret = 10 * ret - (str[i] - 48);
                    if (ret <= INT_MIN)
                        return INT_MIN;
                }
                return ret;
            }
            else
                return ret;
        }
        return ret;
    }
};
```

<br/>