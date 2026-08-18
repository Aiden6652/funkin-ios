import os, sys

root = sys.argv[1] if len(sys.argv) > 1 else '.haxelib'
keywords = ["to be compiling", "got Lime", "Lime has to be"]
found = []
for dirpath, dirs, files in os.walk(root):
    for fn in files:
        if not fn.endswith(('.hx', '.hxp')):
            continue
        p = os.path.join(dirpath, fn)
        try:
            s = open(p, encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        for kw in keywords:
            if kw in s:
                lines = s.split('\n')
                for i, ln in enumerate(lines):
                    if kw in ln:
                        found.append((p, i + 1, ln.strip()[:200]))
                        # 打印前后 3 行上下文
                        ctx = lines[max(0, i - 3):i + 3]
                        for c in ctx:
                            print('CTX', p, '=>', c.strip()[:200])
                        print('---')
                break

# patch: error/trace/Log.error -> trace（对含关键词行）
changed = {}
for p, ln, txt in found:
    if p not in changed:
        changed[p] = open(p, encoding='utf-8', errors='ignore').read().split('\n')
for p, ln, txt in found:
    lines = changed[p]
    line = lines[ln - 1]
    nline = line.replace('Log.error', 'trace').replace('error(', 'trace(').replace('throw ', 'trace ')
    if nline != line:
        lines[ln - 1] = nline
        print('PATCHED', p, ln, '=>', nline.strip()[:150])
for p, lines in changed.items():
    open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('TOTAL_FOUND:', len(found))
