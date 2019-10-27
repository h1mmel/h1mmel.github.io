---
layout: post
title: StackOverFlow 之 Ret2ShellCode 详解
tags: bin CS vul stackoverflow
categories: stackoverflow 
---

***\*本文作者：h1mmel，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**



## **0×00 序言** 

**学习时常需要复习巩固仅以此文作为记录我的pwn学习历程的开篇吧。CTF中pwn题以难入门难提升而著称需要掌握的知识全面而且繁杂，学习时切记不要急躁。保持一个良好的心态对于pwn学习是很重要的。本文记录 栈溢出 中的简单 ret2shellcode 利用和最基础的栈知识，用例为 [pwnable.tw](https://pwnable.tw/) 中的第一道题 start 。**

