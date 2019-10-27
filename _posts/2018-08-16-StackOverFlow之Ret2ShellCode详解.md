---
layout: post
title: StackOverFlow 之 Ret2ShellCode 详解
tags: bin vul stackoverflow CS 
categories: stackoverflow
---

首发于 **freebuf**  [StackOverFlow 之 Ret2ShellCode 详解](https://www.freebuf.com/vuls/179724.html)

## **0×00 序言** 

**学习时常需要复习巩固仅以此文作为记录我的pwn学习历程的开篇吧。CTF中pwn题以难入门难提升而著称需要掌握的知识全面而且繁杂，学习时切记不要急躁。保持一个良好的心态对于pwn学习是很重要的。本文记录 栈溢出 中的简单 ret2shellcode 利用和最基础的栈知识，用例为 [pwnable.tw](https://pwnable.tw/) 中的第一道题 start 。**

<br/>

## **0×01 环境准备**

[kali linux 2018.2](https://www.kali.org/downloads/) 用kali的原因是里面有很多的工具可以很节省时间

[pwndbg](https://github.com/pwndbg/pwndbg) 是 gdb 的一个插件类似的插件还有[peda](https://github.com/longld/peda)[pwngdb](https://github.com/scwuaptx/Pwngdb) 插件的功能大同小异不用纠结。用插件的原因是原生的 gdb 没有高亮显示且观察寄存器、堆栈等必要信息不方便 。gdb 已经在 kali 中内置好了不需要自行安装

objdump 也是可以快速查看二进制文件信息的工具可以很方便的获取二进制文件的很多信息诸如反汇编调用的函数信息等

<br/>

## **0×02 必要工具安装**

编写exp的利器 [pwntools](https://github.com/Gallopsled/pwntools) 这个 python 模块是用来加快和简单化 exploitation 的编写用法可以查看 [官方文档](https://docs.pwntools.com/en/stable/) 安装

> pip install –upgrade pip
>
> pip install –upgrade pwntools

一些必要的库文件

> apt install gcc-multilib libcapstone3 python-capstone binutils

gdb 反汇编语法设置默认为 AT&T 语法改为 Intel 语法

> set disassembly-flavor intel > ~/.gdbinit

<br/>

## **0×03 名词解释**

> **exp**  通常指漏洞利用的脚本
>
> **shellcode** 指能打开shell的一段代码通常用汇编编写
>
> **payload (有效载荷)** 漏洞利用过程中需要构造的攻击代码**shellcode** 属于 payload 的一部分

<br/>

## **0×04 栈相关知识和汇编指令**

### **基本 Intel 32 位汇编知识**

几个寄存器

8个通用寄存器**eax,ebx,ecx,edx,edi,esi,esp,ebp** 寄存器可以简单的理解为高级语言中的变量。

**eax**  (累加器) 默认保存着加法乘法结果函数返回值

**esi/edi**   (源/目标索引寄存器) 通常用于字符串操作esi 保存着源字符串的首地址edi 保存着目标字符串的首地址

**esp** 扩展栈指针寄存器指向当前栈顶即保存着当前栈顶的地址

**ebp**  (扩展基址指针寄存器) 指向当前栈底即保存着当前栈底的地址

除此之外还有 **eip**指令指针寄存器) 该寄存器存放着**将要**执行的代码的地址当一个程序开始运行时系统自动将 eip 清零每取入一条指令eip 自动增加取入cpu的字节数在控制程序流程时控制 eip寄存器 的值显得尤为关键决定着是否可以驰骋内存。

还有个跟运算息息相关的 **EFLAGS** 标志寄存器这里面装着很多标志位标志着运算状态等信息。

几个简单指令

> **mov** eax,ebx 将 ebx 中的值复制给 eax
>
> **add** eax,ebx  将 eax 和 ebx 相加后的值传入 eax 中
>
> **sub** eax,ebx  将 eax 和 ebx 相减后的值传入 eax 中
>
> **lea** eax, dword ptr ds:[ebx] 将 ebx 传给 eax 。dword ptr ds:[0x12345678] 表示 存储类型为 dword 双字 4 个字节数据段 偏移为 0×12345678 的内存区域[0x12345678]表示内存编号即地址 为 0×12345678
>
> **mov** eax,dword ptr ds:[ebx] **注意** 这里是将 ebx 代表的内存地址的中的内容传给 eax 上一条指令是将这块内存区域的**地址**传给 eax
>
> **xor** eax,eax 寄存器清零

### **栈**

这里说的栈与数据结构的栈略微有些区别这里的栈是指程序在运行时在内存中开辟的一块区域称为运行时栈数据存储规则同样为 FILO(First in Last out 先进后出)。操作简单只有push压栈和 pop 弹栈。例如push eax代表将 eax 寄存器中的值压入栈顶寄存器 -> 内存pop eax代表将栈顶的值取出放到 eax 寄存器中 内存 -> 寄存器。