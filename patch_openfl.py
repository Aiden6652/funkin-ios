import os, sys

root = sys.argv[1] if len(sys.argv) > 1 else '.haxelib'
keywords = ["Lime has to be", "FunkinCrew's Fork", "FunkinCrew"]
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
                for i, ln in enumerate(s.split('\n')):
                    if kw in ln:
                        found.append((p, i + 1, ln.strip()[:160]))
                        print('MATCH', p, ':', i + 1, '=>', ln.strip()[:160])
                break

print('---')
for p, ln, txt in found:
    pass

# 尝试 patch: 把含关键词的行的 error/throw/Log.error 换成 trace
changed = {}
for p, ln, txt in found:
    if p not in changed:
        changed[p] = open(p, encoding='utf-8', errors='ignore').read().split('\n')

for p, ln, txt in found:
    lines = changed[p]
    line = lines[ln - 1]
    nline = line.replace('error(', 'trace(').replace('throw ', 'trace ').replace('Log.error', 'trace')
    if nline != line:
        lines[ln - 1] = nline
        print('PATCHED', p, ln, '=>', nline.strip()[:120])

for p, lines in changed.items():
    open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print('TOTAL_FOUND:', len(found))
