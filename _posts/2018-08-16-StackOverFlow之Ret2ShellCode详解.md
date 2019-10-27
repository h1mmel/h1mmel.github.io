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

![push_pop](/images/2018-08-16-StackOverFlow之Ret2ShellCode详解/push_pop.png)

 上图表示 push 和 pop 操作栈中数值的变化**注意栈的生长方向是高地址到低地址** push eax 第一步将 esp – 4 中使 esp 重新指向栈顶 一个单位栈空间占据4字节第二步将 eax 中的值放入栈顶同理 push ebx 第一步使 esp 继续减 4 中使 esp 指向新的栈顶 第二步将 ebx 中的值放入栈顶 。pop ebx 第一步将栈顶的值传入 ebx 中第二步使 esp + 4 使其指向新的栈顶。push 和 pop 操作动作相反。 

<br/>

## **0×05 函数调用时栈中的变化** 

```
示例代码:test.c

#include <stdio.h>

int fun(int a,int b)
{
	return a + b;
}

int main(int argc, char const *argv[])
{
	int a = 1,b = 2;
	fun(a,b);
	return 0;
}
```

编译程序

```
 gcc test.c -m32 -fno-stack-protector -z execstack -no-pie -o test
```

关闭掉 DEP/NX 、栈保护、pie保护 并编译成 32 位程序查看反汇编代码:

```
08049172 <fun>:
 8049172:	55                   	push   ebp
 8049173:	89 e5                	mov    ebp,esp
 8049175:	e8 42 00 00 00       	call   80491bc <__x86.get_pc_thunk.ax>
 804917a:	05 86 2e 00 00       	add    eax,0x2e86
 804917f:	8b 55 08             	mov    edx,DWORD PTR [ebp+0x8]
 8049182:	8b 45 0c             	mov    eax,DWORD PTR [ebp+0xc]
 8049185:	01 d0                	add    eax,edx
 8049187:	5d                   	pop    ebp
 8049188:	c3                   	ret    

08049189 <main>:
 8049189:	55                   	push   ebp
 804918a:	89 e5                	mov    ebp,esp
 804918c:	83 ec 10             	sub    esp,0x10
 804918f:	e8 28 00 00 00       	call   80491bc <__x86.get_pc_thunk.ax>
 8049194:	05 6c 2e 00 00       	add    eax,0x2e6c
 8049199:	c7 45 fc 01 00 00 00 	mov    DWORD PTR [ebp-0x4],0x1
 80491a0:	c7 45 f8 02 00 00 00 	mov    DWORD PTR [ebp-0x8],0x2
 80491a7:	ff 75 f8             	push   DWORD PTR [ebp-0x8]
 80491aa:	ff 75 fc             	push   DWORD PTR [ebp-0x4]
 80491ad:	e8 c0 ff ff ff       	call   8049172 <fun>
 80491b2:	83 c4 08             	add    esp,0x8
 80491b5:	b8 00 00 00 00       	mov    eax,0x0
 80491ba:	c9                   	leave  
 80491bb:	c3                   	ret    
```

如上所示:

```
push  ebp
mov   ebp,esp
...
pop   ebp
ret    
```

这段代码代表着一个函数的生到死上面四句指令是函数开辟 栈帧就是一块被ebp 和 esp 夹住的区域的开始和结尾标志性语句。

main()函数中调用fun()函数并传值a、b汇编指令对应如下:

```
 8049199:	c7 45 fc 01 00 00 00 	mov    DWORD PTR [ebp-0x4],0x1          ;给ebp - 0x4 区域传值 0x1 ==> a = 1
 80491a0:	c7 45 f8 02 00 00 00 	mov    DWORD PTR [ebp-0x8],0x2          ;给ebp - 0x8 区域传值 0x2 ==> b = 2
 80491a7:	ff 75 f8             	push   DWORD PTR [ebp-0x8]              ;参数入栈 ebp - 0x8 区域的值 
 80491aa:	ff 75 fc             	push   DWORD PTR [ebp-0x4]              ;参数入栈 ebp - 0x4 区域的值 
 80491ad:	e8 c0 ff ff ff       	call   8049172 <fun>                    ;调用函数 fun()                  
```

从上面可以看出函数参数入栈的顺序和我们正常C语言的调用顺序是反着的即**参数逆序入栈。**这里还有一点就是在调用一个函数前都是先压入参数(没有参数就不用)然后再调用函数汇编表现为 push xxx ; push xxx; push xxx; call xxx的形式。当然这根据不同的**调用约定**有关参考 [这里](http://www.cnblogs.com/clover-toeic/p/3755401.html)。什么是调用约定这关系到另外一个问题当一个函数被调用完时它之前所开辟的栈空间到底怎么处理有两种方式第一种就是掉用者清理这种方式成为 **cdecl 调用约定**此约定也是 c/c++ 缺省的调用方式第二种就是被调用者清理栈空间这种称为 **stdcall 调用约定** windows程序开发时大多使用这种调用方式。**stdcall** 调用约定还有个升级版 **fastcall** 调用约定与 **stdcall** **调用约定** 不同的是如果被调用者只有至多两个参数则通过寄存器传参超过两个参数的部分则还是以栈的形式传参。不管他们哪种调用约定参数都是以逆序的方式入栈。接下来就是图解栈的调用



