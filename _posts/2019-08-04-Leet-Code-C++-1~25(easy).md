---
layout: post
title: Leet Code C++ 1~25 (easy)
tags: C++ CS
categories: C++ 
---

### 1、两数之和

题目描述

> 给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那 两个 整数，并返回他们的数组下标。
>
> 你可以假设每种输入只会对应一个答案。但是，你不能重复利用这个数组中同样的元素。
>

**示例**

> 给定 nums = [2, 7, 11, 15], target = 9
>
> 因为 nums[0] + nums[1] = 2 + 7 = 9
> 所以返回 [0, 1]

C++ code

```c++
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        vector<int> ret(2);
        for (int i = 0; i < nums.size() - 1; i++)
        {
            for (int j = i + 1; j < nums.size(); j++)
            {
                if (nums[i] + nums[j] == target)
                {
                    ret[0] = i;
                    ret[1] = j;
                }
            }
        }
        return ret;
    }
};
```

</br>

### 7、整数反转

题目描述

> 给出一个 32 位的有符号整数，你需要将这个整数中每位上的数字进行反转。

**示例 1:**

```
输入: 123
输出: 321
```

 **示例 2:**

```
输入: -123
输出: -321
```

**示例 3:**

```markdown
输入: 120
输出: 21
```

c++ code

```c++
class Solution {
public:
    int reverse(int x) {
        long result = 0;
        while (x != 0)
        {
            result = result * 10 + x % 10;
            x /= 10;
        }
        if (result > INT_MAX || result < INT_MIN)
            return 0;
        return result;
    }
};
```

</br>

### 9、回文数

题目描述

> 判断一个整数是否是回文数。回文数是指正序（从左向右）和倒序（从右向左）读都是一样的整数。

**示例 1:**

```markdown
输入: 121
输出: true
```

**示例 2:**

```markdown
输入: -121
输出: false
解释: 从左向右读, 为 -121 。 从右向左读, 为 121- 。因此它不是一个回文数。
```

**示例 3:**

```
输入: 10
输出: false
解释: 从右向左读, 为 01 。因此它不是一个回文数。
```

c++ code

```c++
class Solution {
public:
    bool isPalindrome(int x) {
        string str = to_string(x);
        for (int i = 0; i < str.size() / 2; i++)
        {
            if (str[i] == str[str.size() - 1 - i])
            {
                continue;
            }
            else
            {
                return false;
            }
        }
        return true;
    }
};
```

</br>

### 13、罗马数字转整数

题目描述

> ​	罗马数字包含以下七种字符: `I`， `V`， `X`， `L`，`C`，`D` 和 `M`。

```
字符          数值
I             1
V             5
X             10
L             50
C             100
D             500
M             1000
```

> 例如， 罗马数字 2 写做 `II` ，即为两个并列的 1。12 写做 `XII` ，即为 `X` + `II` 。 27 写做  `XXVII`, 即为 `XX` + `V` + `II` 。通常情况下，罗马数字中小的数字在大的数字的右边。但也存在特例，例如 4 不写做 `IIII`，而是 `IV`。数字 1 在数字 5 的左边，所表示的数等于大数 5 减小数 1 得到的数值 4 。同样地，数字 9 表示为 `IX`。这个特殊的规则只适用于以下六种情况：
>
> * `I` 可以放在 `V` (5) 和 `X` (10) 的左边，来表示 4 和 9。
> * `X` 可以放在 `L` (50) 和 `C` (100) 的左边，来表示 40 和 90。 
> * `C` 可以放在 `D` (500) 和 `M` (1000) 的左边，来表示 400 和 900。
>
> 给定一个罗马数字，将其转换成整数。输入确保在 1 到 3999 的范围内。

**示例 1:**

```
输入: "III"
输出: 3
```

**示例 2:**

```
输入: "IV"
输出: 4
```

**示例 3:**

```
输入: "IX"
输出: 9
```

**示例 4:**

```
输入: "LVIII"
输出: 58
解释: L = 50, V= 5, III = 3.
```

**示例 5:**

```
输入: "MCMXCIV"
输出: 1994
解释: M = 1000, CM = 900, XC = 90, IV = 4.
```

c++ code

```c++
class Solution {
public:
    int romanToInt(string s) {
        string str;
        int ret = 0, i, m, n;
        char roman[7] = {'I', 'V', 'X', 'L', 'C', 'D', 'M'};
        int india[7] = {1, 5, 10, 50, 100, 500, 1000};
        
        for (i = 0; i < s.size(); i++)
        {
            str += s[s.size() - i - 1];
        }
        for (i = 0; i < str.size(); i++)
        {
            for (m = 0; m < 7; m++)
            {
                if (roman[m] == str[i])
                    break;
            }
            if(i)
            {
                for (n = 0; n < 7; n++)
                {
                    if (roman[n] == str[i - 1])
                        break;
                }
                if (m >= n)
                    ret += india[m];
                else
                    ret -= india[m];
            }
            else
            {
                ret += india[m];
            }
        }
        return ret;
    }
};
```

