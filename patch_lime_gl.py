import os, sys

# Patch lime fork OpenGLBindings.cpp for iPhone (GLES2) builds:
# stub only GLES3-only symbols (sampler/sync/VAO/TFO/pipeline/GLintptr).
# GLES2 functions (glBindTexture etc.) must NOT be stubbed.
root = sys.argv[1] if len(sys.argv) > 1 else '.haxelib/lime/git/project'
target = os.path.join(root, 'src/bindings/opengl/OpenGLBindings.cpp')
if not os.path.exists(target):
    print('NOT_FOUND', target)
    sys.exit(0)

s = open(target, encoding='utf-8', errors='ignore').read()
# remove any previous broad stub block
import re
s = re.sub(r'/\* STUB_GL_DELETE_HELPERS[^*]*\*/\n', '', s)

if 'STUB_GLES3_ONLY_HELPERS' in s:
    print('ALREADY_PATCHED')
    sys.exit(0)

stub = '''
/* STUB_GLES3_ONLY_HELPERS - GLES3-only symbols missing from GLES2 headers */
#define GLintptr intptr_t
#define glIsSampler(x) 0
#define glDeleteSamplers(n, x) ((void)0)
#define glBindSampler(u, x) ((void)0)
#define glIsSync(x) 0
#define glDeleteSync(x) ((void)0)
#define glFenceSync(a, b) ((void*)0)
#define glWaitSync(a, b, c) 0
#define glClientWaitSync(a, b, c, d) 0
#define glIsVertexArray(x) 0
#define glDeleteVertexArrays(n, x) ((void)0)
#define glBindVertexArray(x) ((void)0)
#define glIsProgramPipeline(x) 0
#define glDeleteProgramPipelines(n, x) ((void)0)
#define glIsTransformFeedback(x) 0
#define glDeleteTransformFeedbacks(n, x) ((void)0)
#define glBeginTransformFeedback(m) ((void)0)
#define glEndTransformFeedback() ((void)0)
#define glBindTransformFeedback(t, x) ((void)0)
'''

anchor = '#include <vector>\n'
if anchor not in s:
    anchor = '#include "OpenGLBindings.h"\n'
if anchor in s:
    s = s.replace(anchor, anchor + stub, 1)
    open(target, 'w', encoding='utf-8', newline='').write(s)
    print('PATCHED', target)
else:
    print('ANCHOR_NOT_FOUND', target)
