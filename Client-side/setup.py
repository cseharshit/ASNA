from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['PySimpleGUI','socket','pathlib','hashlib','datetime','platform','subprocess','os','csv','fpdf','sys','re'], excludes = [])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('ASNA.py', base=base, targetName = 'WindowsScorer-GUI', icon='ASNA.png')
]

setup(name='Automated Systems & Network Auditor (ASNA)',
      version = '1.1',
      description = 'ASNA (Created By: Praman Kasliwal)',
      options = dict(build_exe = buildOptions),
      executables = executables)
