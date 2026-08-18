import os, sys, subprocess

root = sys.argv[1] if len(sys.argv) > 1 else '.haxelib'
kw = "Lime has to be"
hits = []
for dirpath, dirs, files in os.walk(root):
    for fn in files:
        p = os.path.join(dirpath, fn)
        # 文本文件直接 grep
        if fn.endswith(('.hx', '.hxp', '.json', '.xml', '.hxml', '.txt', '.md')):
            try:
                s = open(p, encoding='utf-8', errors='ignore').read()
            except Exception:
                continue
            if kw in s:
                hits.append(p)
                for i, ln in enumerate(s.split('\n')):
                    if kw in ln:
                        print('TEXT', p, i + 1, ln.strip()[:160])
        # 二进制用 strings
        elif fn.endswith(('.n', '.ndll', '.dll', '.so', '.dylib')) or '.' not in fn:
            try:
                out = subprocess.run(['strings', p], capture_output=True, text=True, timeout=20).stdout
            except Exception:
                continue
            if kw in out:
                hits.append(p)
                for ln in out.split('\n'):
                    if kw in ln:
                        print('BIN ', p, ln.strip()[:160])
print('HITS:', hits)
