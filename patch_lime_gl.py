import os, sys

# Patch lime fork OpenGLBindings.cpp: stub GL symbols missing from the GL header
# actually included when building for iPhone (desktop GL2 header). Unconditional
# stubs are fine here - GC-delete helpers are no-ops and only affect cleanup.
root = sys.argv[1] if len(sys.argv) > 1 else '.haxelib/lime/git/project'
target = os.path.join(root, 'src/bindings/opengl/OpenGLBindings.cpp')
if not os.path.exists(target):
    print('NOT_FOUND', target)
    sys.exit(0)

s = open(target, encoding='utf-8', errors='ignore').read()
if 'STUB_GL_DELETE_HELPERS' in s:
    print('ALREADY_PATCHED')
    sys.exit(0)

stub = '''
/* STUB_GL_DELETE_HELPERS - missing GL symbols when building for iPhone */
#define glIsFramebuffer(x) 0
#define glDeleteFramebuffers(n, x) ((void)0)
#define glIsProgram(x) 0
#define glDeleteProgram(x) ((void)0)
#define glIsQuery(x) 0
#define glDeleteQueries(n, x) ((void)0)
#define glIsRenderbuffer(x) 0
#define glDeleteRenderbuffers(n, x) ((void)0)
#define glIsSampler(x) 0
#define glDeleteSamplers(n, x) ((void)0)
#define glIsShader(x) 0
#define glDeleteShader(x) ((void)0)
#define glIsTexture(x) 0
#define glDeleteTextures(n, x) ((void)0)
#define glIsBuffer(x) 0
#define glDeleteBuffers(n, x) ((void)0)
#define glIsSync(x) 0
#define glDeleteSync(x) ((void)0)
#define glFenceSync(a, b) ((void*)0)
#define glWaitSync(a, b, c) 0
#define glClientWaitSync(a, b, c, d) 0
#define glIsVertexArray(x) 0
#define glDeleteVertexArrays(n, x) ((void)0)
#define glIsProgramPipeline(x) 0
#define glDeleteProgramPipelines(n, x) ((void)0)
#define glIsTransformFeedback(x) 0
#define glDeleteTransformFeedbacks(n, x) ((void)0)
#define glGenFramebuffers(n, x) ((void)0)
#define glBindFramebuffer(t, x) ((void)0)
#define glCheckFramebufferStatus(t) 0
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
