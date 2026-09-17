#!/usr/bin/env python3
"""Repeatable Linux-to-Windows standalone build operations."""
import shutil
import subprocess
import sys
import hashlib
import json
import urllib.request
import zipfile
import os
import re
import struct
import math
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / 'build/windows-x64'
SDL_VERSION = '2.32.10'
SDL_SHA256 = 'f15cff5fca62ec9381a016ef1d42a95c638cd72d2f226ba5781c76fe43dbd1ac'

def prepare():
    BUILD.mkdir(parents=True, exist_ok=True)
    name = f'SDL2-devel-{SDL_VERSION}-mingw.zip'
    request = urllib.request.Request(f'https://api.github.com/repos/libsdl-org/SDL/releases/tags/release-{SDL_VERSION}', headers={'User-Agent': 'music-analyzer-build'})
    with urllib.request.urlopen(request, timeout=30) as response:
        release = json.load(response)
    asset = next(a for a in release['assets'] if a['name'] == name)
    archive = BUILD / name
    if not archive.exists():
        with urllib.request.urlopen(asset['browser_download_url'], timeout=60) as response:
            archive.write_bytes(response.read())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != SDL_SHA256 or asset.get('digest') != 'sha256:'+digest:
        raise RuntimeError('SDL archive did not match the published SHA256 digest')
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            target = (BUILD/item.filename).resolve()
            if not target.is_relative_to(BUILD.resolve()):
                raise RuntimeError('Unsafe archive path')
        z.extractall(BUILD)
    (BUILD/'sdl-provenance.json').write_text(json.dumps({'url':asset['browser_download_url'], 'sha256':digest}, indent=2))
    print('Verified and extracted SDL', SDL_VERSION, digest)

def build():
    sdl = BUILD / f'SDL2-{SDL_VERSION}' / 'x86_64-w64-mingw32'
    if not (sdl/'include/SDL2/SDL.h').exists():
        raise RuntimeError('Run make prepare-windows-standalone first')
    out = BUILD/'portable'
    out.mkdir(parents=True, exist_ok=True)
    cxx = shutil.which('x86_64-w64-mingw32-g++-posix') or 'x86_64-w64-mingw32-g++'
    cc = shutil.which('x86_64-w64-mingw32-gcc-posix') or 'x86_64-w64-mingw32-gcc'
    common = ['-O2', '-DNDEBUG', '-DNOMINMAX', '-I'+str(ROOT/'src'), '-I'+str(ROOT/'third_party/beat_and_tempo_tracking'), '-I'+str(sdl/'include/SDL2')]
    objects = []
    with (BUILD/'build.log').open('w') as log:
        def run(args):
            log.write(' '.join(map(str,args))+'\n'); log.flush()
            subprocess.run(list(map(str,args)), cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        sources = list((ROOT/'third_party/beat_and_tempo_tracking/src').glob('*.c'))
        sources += [ROOT/'src'/n for n in ['analyzer.cpp','visualizer_renderer.cpp','basic_pitch_onnx_runtime.cpp','basic_pitch_onnx_decoder.cpp','basic_pitch_onnx_worker.cpp','basic_pitch_pcm_history.cpp','fret_control.cpp','windows_hardware_control.cpp']]
        for src in sources:
            obj = BUILD/(src.stem+'.o')
            print('Compiling',src.name,flush=True)
            flags = ['-Drandom=rand'] if src.suffix=='.c' else ['-std=c++17', '-DMAO_NO_ONNX_RUNTIME=1']
            stamp = obj.with_suffix('.command')
            command = [cc if src.suffix=='.c' else cxx, *common, *flags, '-c',str(src),'-o',str(obj)]
            signature = json.dumps(command) + ''.join(hashlib.sha256(p.read_bytes()).hexdigest() for p in [src, *sorted((ROOT/'src').glob('*.hpp'))])
            if not obj.exists() or not stamp.exists() or stamp.read_text() != signature:
                run(command)
                stamp.write_text(signature)
            objects.append(obj)
        for name, compact in [('MusicAnalyzer',0),('HalfMusicAnalyzer',1)]:
            obj = BUILD/(name+'.o')
            run([cxx,*common,'-std=c++17','-DMAO_STANDALONE_WITH_SDL=1',*(['-DMAO_STANDALONE_BASS_GUITAR=1'] if compact else []),'-DMAO_STANDALONE_VERSION="windows-x64"','-c',ROOT/'src/standalone.cpp','-o',obj])
            run([cxx,*objects,obj,sdl/'lib/libSDL2.dll.a','-lpsapi','-lole32','-luuid','-lksuser','-lwinmm','-lsetupapi','-lbluetoothapis','-static','-Wl,--stack,16777216','-o',out/(name+'.exe')])
        shutil.copy2(sdl/'bin/SDL2.dll',out/'SDL2.dll')
    print('Built',out)

def verify():
    out = BUILD/'portable'
    system = {'kernel32.dll','msvcrt.dll','user32.dll','gdi32.dll','winmm.dll','imm32.dll','bluetoothapis.dll',
              'ole32.dll','oleaut32.dll','version.dll','setupapi.dll','advapi32.dll',
              'shell32.dll','psapi.dll','ws2_32.dll','ntdll.dll','rpcrt4.dll'}
    evidence = {}
    for binary in [out/'MusicAnalyzer.exe',out/'HalfMusicAnalyzer.exe',out/'SDL2.dll']:
        header = subprocess.check_output(['x86_64-w64-mingw32-objdump','-f',str(binary)], text=True)
        if 'pei-x86-64' not in header: raise RuntimeError('Not Windows x64: '+str(binary))
        table = subprocess.check_output(['x86_64-w64-mingw32-objdump','-p',str(binary)], text=True)
        imports = re.findall(r'DLL Name:\s*(\S+)',table)
        missing = [n for n in imports if n.lower() not in system and not (out/n).exists()]
        if missing: raise RuntimeError('Unbundled dependencies: '+str(missing))
        evidence[binary.name] = {'imports':imports,'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
    env = dict(os.environ, WINEPREFIX=str(BUILD/'wine-test-prefix'), WINEDEBUG='-all',
               SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
    for name in ['MusicAnalyzer','HalfMusicAnalyzer']:
        with (BUILD/(name+'-self-test.log')).open('w') as log:
            result = subprocess.run(['wine',str(out/(name+'.exe')),'--self-test'], env=env, stdout=log,stderr=subprocess.STDOUT,timeout=120)
        text = (BUILD/(name+'-self-test.log')).read_text()
        if result.returncode or 'standalone self-test: ok' not in text:
            raise RuntimeError(name+' self-test failed; see '+str(BUILD/(name+'-self-test.log')))
        evidence[name+'.exe']['wine_self_test'] = 'passed'
        with (BUILD/(name+'-hardware-list.log')).open('w') as log:
            result = subprocess.run(['wine',str(out/(name+'.exe')),'--list-hardware'], env=env, stdout=log,stderr=subprocess.STDOUT,timeout=120)
        if result.returncode:
            raise RuntimeError(name+' hardware enumeration failed; see '+str(BUILD/(name+'-hardware-list.log')))
        evidence[name+'.exe']['wine_hardware_enumeration'] = 'passed'
        print(name, 'Windows PE x64; imports resolved; Wine self-test passed')
    (BUILD/'verification.json').write_text(json.dumps(evidence,indent=2))

def smoke():
    # Recheck the untouched Linux path without rebuilding the large analyzer.
    local = ROOT/'build/deps/usr/include'
    if (local/'SDL2/SDL.h').exists():
        cflags = ['-I'+str(local/'SDL2'),'-I'+str(local/'x86_64-linux-gnu'),'-D_REENTRANT']
    else:
        cflags = shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))
    subprocess.run(['g++','-std=c++17','-DMAO_STANDALONE_WITH_SDL=1','-Isrc',*cflags,
                    '-fsyntax-only','src/standalone.cpp'],cwd=ROOT,check=True)
    fixture = BUILD/'smoke.f32'
    fixture.write_bytes(b''.join(struct.pack('<f',0.2*math.sin(2*math.pi*220*i/48000)) for i in range(48000)))
    env = dict(os.environ,WINEPREFIX=str(BUILD/'wine-test-prefix'),WINEDEBUG='-all',SDL_AUDIODRIVER='dummy')
    env.pop('SDL_VIDEODRIVER',None)
    for name in ['MusicAnalyzer','HalfMusicAnalyzer']:
        with (BUILD/(name+'-window-smoke.log')).open('w') as log:
            subprocess.run(['wine',str(BUILD/'portable'/(name+'.exe')),'--raw-f32le',str(fixture)],
                           env=env,stdout=log,stderr=subprocess.STDOUT,timeout=60,check=True)
        print(name,'Wine windowed raw-audio smoke passed')
    (BUILD/'window-smoke-passed.txt').write_text('Both Windows variants launched, processed fixture audio and exited successfully under Wine. Linux standalone syntax check passed.\n')

def package():
    verify()
    out = BUILD/'portable'
    shutil.copy2(ROOT/'docs/windows_standalone.md',out/'README.txt')
    shutil.copy2(BUILD/f'SDL2-{SDL_VERSION}'/'LICENSE.txt',out/'SDL-LICENSE.txt')
    beat = ROOT/'third_party/beat_and_tempo_tracking'
    for name in ['LICENSE','LICENSE.txt','COPYING']:
        if (beat/name).exists(): shutil.copy2(beat/name,out/'BEAT-TRACKER-LICENSE.txt'); break
    shutil.copy2(BUILD/'verification.json',out/'verification.json')
    provenance = {'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                  'working_tree_modified':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()),
                  'sdl':json.loads((BUILD/'sdl-provenance.json').read_text()),
                  'physical_windows_audio_tested':False}
    (out/'build-provenance.json').write_text(json.dumps(provenance,indent=2))
    archive = BUILD/'MusicAnalyzer-Windows11-x64.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.iterdir()):
            if p.is_file(): z.write(p,'MusicAnalyzer/'+p.name)
    print('Package:',archive)
    print('SHA256:',hashlib.sha256(archive.read_bytes()).hexdigest())
    subprocess.run(['notify-send','Windows Music Analyzer ready',str(archive)],check=False)

def inspect():
    for name in ['x86_64-w64-mingw32-g++', 'x86_64-w64-mingw32-gcc', 'cmake', 'ninja', 'wine', 'clang', 'zig']:
        print(name, shutil.which(name) or 'MISSING')
    result = subprocess.run(['git', 'status', '--short', '--', 'src/standalone.cpp', 'Makefile', 'CMakeLists.txt'], cwd=ROOT, capture_output=True, text=True)
    print(result.stdout)
    for directory in [ROOT/'build', Path('/usr/x86_64-w64-mingw32')]:
        if directory.exists():
            print(directory, [p.name for p in directory.iterdir() if any(s in p.name.lower() for s in ['sdl','mingw','windows','toolchain'])])

if __name__ == '__main__':
    if sys.argv[1] == 'inspect':
        inspect()
    elif sys.argv[1] == 'prepare':
        prepare()
    elif sys.argv[1] == 'build':
        build()
    elif sys.argv[1] == 'verify':
        verify()
    elif sys.argv[1] == 'package':
        package()
    elif sys.argv[1] == 'smoke':
        smoke()
