import os, sys, re

root = sys.argv[1] if len(sys.argv) > 1 else '.haxelib'
kw = "Lime has to be"
for dirpath, dirs, files in os.walk(root):
    for fn in files:
        if not fn.endswith('.xml'):
            continue
        p = os.path.join(dirpath, fn)
        try:
            s = open(p, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        if kw not in s:
            continue
        print('FOUND', p)
        # 删除含 "Lime has to be" 的 <log .../> 行
        lines = s.split('\n')
        out = []
        for ln in lines:
            if kw in ln and '<log' in ln:
                print('REMOVING:', ln.strip()[:160])
                continue  # 删掉这行
            out.append(ln)
        open(p, 'w', encoding='utf-8').write('\n'.join(out))
        print('PATCHED', p)
