import os, sys, re

root = sys.argv[1] if len(sys.argv) > 1 else '.haxelib/openfl'
patched = []
for dirpath, dirs, files in os.walk(root):
    for fn in files:
        if not fn.endswith('.hx'):
            continue
        p = os.path.join(dirpath, fn)
        try:
            s = open(p, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        if "FunkinCrew's Fork" not in s:
            continue
        lines = s.split('\n')
        changed = False
        for i, ln in enumerate(lines):
            if "FunkinCrew's Fork" in ln:
                # 打印上下文供诊断
                print('>>>', p, 'line', i + 1, ':', ln.strip()[:120])
                # error(...) -> trace(...), throw -> trace 保持语法
                nln = ln.replace('error(', 'trace(').replace('throw ', 'trace ')
                if nln != ln:
                    lines[i] = nln
                    changed = True
        if changed:
            open(p, 'w', encoding='utf-8').write('\n'.join(lines))
            patched.append(p)
print('PATCHED_FILES:', patched)
