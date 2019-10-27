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

![stackframe](/images/2018-08-16-StackOverFlow之Ret2ShellCode详解/stackfram.png)

被忽略掉的五条指令中前两条不用管后面三条就是

```
 804917f:	8b 55 08             	mov    edx,DWORD PTR [ebp+0x8]   ; ebp + 0x8 ==> edx = 1
 8049182:	8b 45 0c             	mov    eax,DWORD PTR [ebp+0xc]   ; ebp + 0xc ==> eax = 2	               	       
 8049185:	01 d0                	add    eax,edx                   ; eax = 3
```

第一条和第二条指令代表着在调用 fun() 函数之前保存的参数因为是逆序存储所以现在取值的时候就是按照我们C语言的调用顺序读取了第三条指令在前面说寄存器的时候就说了 eax 用来保存函数返回值所以返回最后的值为 3。现在函数调用和栈帧变化也了解了可以试着做一下题了。

<br/>

## **0×06 栈溢出**

### 什么是**栈溢出？**

栈溢出其实就是指程序向变量中写入了超过自身实际大小的内容造成改变栈中相邻变量的值的情况。实现栈溢出要保证两个基本条件第一要程序必须向栈上写入数据第二程序并未对输入内容的大小进行控制。

**ret2shellcode**是什么意思？

在栈溢出的攻击技术中通常是要控制函数的返回地址到自己想要的地方执行自己想要执行的代码。ret2shellcode代表返回到shellcode中即控制函数的返回地址到预先设定好的shellcode区域中去执行shellcode代码这是非常危险的。

## **0×07 start**

此题源程序可以从 [pwnable.tw](https://pwnable.tw/) 中获取

拿到一个程序首先对它的基本信息进行获取

```
⚡ root@kali  ~/Desktop/pwnabletw/start  file start
start: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, not stripped
```

可以看到基本信息为 32 位的 ELF linux 下的可执行程序程序静态链接接下来对安全机制进行检查安装好 pwndbg 后 gdb 中就有了 **checksec** 这个命令

```
pwndbg> checksec 
[*] '/root/Desktop/pwnabletw/start/start'
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
```

所有安全机制全部关闭适合新手入门当然也并不是所有的都关了还有个 ASLR 内存地址空间布局随机化保护机制是现代操作系统默认打开的该保护机制会使每次程序运行时堆栈地址都不固定加大漏洞利用的难度如何查看

```
⚡ root@kali  ~/Desktop/pwnabletw/start  cat /proc/sys/kernel/randomize_va_space 
2
```

如果是 2 就代表开着可用如下命令关闭掉

```
echo 0 > /proc/sys/kernel/randomize_va_space
```

现在就是看题目是什么意思了运行程序默认情况下是没有执行权限的

```
 ✘ ⚡ root@kali  ~/Desktop  ls -al start 
-rw------- 1 root root 564 Aug  3 13:35 start
 ⚡ root@kali  ~/Desktop  chmod a+x start 
 ⚡ root@kali  ~/Desktop  ls -al start   
-rwx--x--x 1 root root 564 Aug  3 13:35 start
```

执行程序

```
 ✘ ⚡ root@kali  ~/Desktop  ./start
Let's start the CTF:12345
```

程序向终端输出一段字符串提示你进行输入随意输入一段字符串后程序停止

查看反汇编代码看看程序的功能是什么

```
 ⚡ root@kali  ~/Desktop  objdump -d start -Mintel  #-d参数代表反汇编-Mintel 表示用Intel语法

start:     file format elf32-i386


Disassembly of section .text:

08048060 <_start>:
 8048060:	54                   	push   esp
 8048061:	68 9d 80 04 08       	push   0x804809d
 8048066:	31 c0                	xor    eax,eax
 8048068:	31 db                	xor    ebx,ebx
 804806a:	31 c9                	xor    ecx,ecx
 804806c:	31 d2                	xor    edx,edx
 804806e:	68 43 54 46 3a       	push   0x3a465443
 8048073:	68 74 68 65 20       	push   0x20656874
 8048078:	68 61 72 74 20       	push   0x20747261
 804807d:	68 73 20 73 74       	push   0x74732073
 8048082:	68 4c 65 74 27       	push   0x2774654c
 8048087:	89 e1                	mov    ecx,esp
 8048089:	b2 14                	mov    dl,0x14
 804808b:	b3 01                	mov    bl,0x1
 804808d:	b0 04                	mov    al,0x4
 804808f:	cd 80                	int    0x80
 8048091:	31 db                	xor    ebx,ebx
 8048093:	b2 3c                	mov    dl,0x3c
 8048095:	b0 03                	mov    al,0x3
 8048097:	cd 80                	int    0x80
 8048099:	83 c4 14             	add    esp,0x14
 804809c:	c3                   	ret    

0804809d <_exit>:
 804809d:	5c                   	pop    esp
 804809e:	31 c0                	xor    eax,eax
 80480a0:	40                   	inc    eax
 80480a1:	cd 80                	int    0x80
```

可以看出整个程序就只有 _start 和 _exit 函数。看代码应该是出题者可以构造的因为按照正常的栈首先因该是 push ebp而不是esp这个先不管看程序功能。这里有一个新的知识点就是 **int 0×80 ;** 这代表着系统中断也就是调用系统函数类似于之前所说的call xxxx; 结构不同的是这里面的参数都是寄存器传参。关于系统调用可以看 [这里](http://syscalls.kernelgrok.com/)。所以第一个 int 0×80 调用的是 sys_write() 第二个int  0×80 调用的是 sys_read()根据系统调用号判断(eax 中存放的就是调用号)。

sys_write(fd,&buf,len)ebx 存放的是 fd(文件描述符有0、1、2三个值0代表标准输入1代表标准输出2代表标准错误输出)ecx 中存放的是 buf 的地址也就是将要输出的字符串的首地址edx 存放的是输出字符串的长度。此时 mov ecx,esp因为 esp 指向栈顶且根据实际程序输出ecx 就是存放着 Let’s start the CTF: 这段字符串的首地址。翻译成C代码如下:

```
#include<stdio.h>
int main()
{
  char buf[20] = "Let's start the CTF:";
  sys_write(1,buf,20);
  sys_read(0,buf,60);
  exit(1);
}
```

流程分析清楚了发现明显的栈溢出缓冲区只有20个字节却可以读入60个字节大小的内容现在可以开始构造攻击流程了。

在调用 sys_write() 之前栈帧情况

![stack1](/images/2018-08-16-StackOverFlow之Ret2ShellCode详解/stack1.png)

蓝色就是buf部分执行sys_read函数时esp 还是指向此地 输入的内容重新覆盖这块缓冲区超出的部分继续向下覆盖。因为ret_addr保存的是exit函数的地址正常返回的话是直接退出程序现在需要控制这个地址使其返回到我们想要去的地方。利用 **mov  ecx,esp** 指令可以得到此时栈的地址。sys_read() 后 add esp,0×14 执行完后栈帧情况

![stack2](/images/2018-08-16-StackOverFlow之Ret2ShellCode详解/stack2.png)

 紧接着就要执行 ret 指令eip 就被修改为 0x804809d而esp – 4指向了程序最开始保存的 esp值也就是栈的基址如图 

![stack3](/images/2018-08-16-StackOverFlow之Ret2ShellCode详解/stack3.png)

试想如果此时将 ret_addr 改成了刚刚所说的 mov ecx,esp 指令处程序就又会继续执行sys_write() 而此时的参数为 sys_write(1,esp,20) 这样一来程序就会输出 esp 指向的地址处的内容而此内存区域刚好存放着保存的 esp 值。这就泄露出了栈的地址有了栈的地址才能在栈上布置 shellcode。

程序继续执行到了 sys_read() 这时便是构造 payload 的时候了只不过此时 esp 指向的是栈底输入的内容机会从现在的位置开始覆盖输入最大为60字节。如图:

![stack4](/images/2018-08-16-StackOverFlow之Ret2ShellCode详解/stack4.png)

 执行完sys_read()函数之后还需执行 add esp,0×14 所以 shellcode 能放的地方也只有剩下的40字节但也足够了。 

![stack5](/images/2018-08-16-StackOverFlow之Ret2ShellCode详解/stack5.png)

