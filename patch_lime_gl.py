import os, sys

# Patch lime fork OpenGLBindings.cpp: stub desktop-GL-only funcs when building for GLES2 (iPhone)
root = sys.argv[1] if len(sys.argv) > 1 else '.haxelib/lime/git/project'
target = os.path.join(root, 'src/bindings/opengl/OpenGLBindings.cpp')
if not os.path.exists(target):
    print('NOT_FOUND', target)
    sys.exit(0)

s = open(target, encoding='utf-8', errors='ignore').read()
if 'LIME_OPENGL_GLES2' in s and 'STUB_GLES2_DELETE_HELPERS' in s:
    print('ALREADY_PATCHED')
    sys.exit(0)

stub = '''
#if defined(LIME_OPENGL_GLES2)
/* STUB_GLES2_DELETE_HELPERS - GLES2 headers lack these desktop/GLES3 symbols; GC deletes are no-ops on iOS */
#define glIsRenderbuffer(x) 0
#define glDeleteRenderbuffers(n, x) ((void)0)
#define glIsShader(x) 0
#define glDeleteShader(x) ((void)0)
#define glIsSampler(x) 0
#define glDeleteSamplers(n, x) ((void)0)
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
#define glIsTexture(x) 0
#define glDeleteTextures(n, x) ((void)0)
#define glIsBuffer(x) 0
#define glDeleteBuffers(n, x) ((void)0)
#define glIsFramebuffer(x) 0
#define glDeleteFramebuffers(n, x) ((void)0)
#endif
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
