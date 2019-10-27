#include <stdio.h>

static int a;
extern int b;
extern void test();

int fun()
{
	a = 1;
	b = 2;
}

int main(int argc, char const *argv[])
{
	fun();
	test();
	printf("hey!");
	
	return 0;
}