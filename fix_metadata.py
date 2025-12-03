import zipfile
import tarfile
import gzip
import io
import os
import shutil

def fix_metadata_content(metadata):
    """Fix metadata by removing problematic fields"""
    lines = metadata.split('\n')
    new_lines = []
    for l in lines:
        l = l.rstrip('\r')
        if l.startswith('License-Expression:'):
            new_lines.append('License: Apache-2.0')
        elif l.startswith('Dynamic: license-file'):
            continue
        elif l.startswith('License-File:'):
            continue
        else:
            new_lines.append(l)
    
    new_metadata = '\n'.join(new_lines)
    if not new_metadata.endswith('\n'):
        new_metadata += '\n'
    return new_metadata

# Fix wheel
if os.path.exists('dist/deepharvest-1.0.0-py3-none-any.whl'):
    z = zipfile.ZipFile('dist/deepharvest-1.0.0-py3-none-any.whl', 'r')
    files = z.namelist()
    metadata_file = [f for f in files if 'METADATA' in f][0]
    metadata = z.read(metadata_file).decode('utf-8')
    new_metadata = fix_metadata_content(metadata)

    temp_whl = 'dist/deepharvest-1.0.0-py3-none-any.whl.tmp'
    z2 = zipfile.ZipFile(temp_whl, 'w', zipfile.ZIP_DEFLATED)
    for f in files:
        if f == metadata_file:
            z2.writestr(f, new_metadata.encode('utf-8'))
        else:
            z2.writestr(f, z.read(f))
    z2.close()
    z.close()
    os.replace(temp_whl, 'dist/deepharvest-1.0.0-py3-none-any.whl')
    print('Fixed wheel METADATA')
else:
    print('Wheel not found, skipping')

# Fix tar.gz
if os.path.exists('dist/deepharvest-1.0.0.tar.gz'):
    t = tarfile.open('dist/deepharvest-1.0.0.tar.gz', 'r:gz')
    members = t.getmembers()
    pkg_info = [m for m in members if 'PKG-INFO' in m.name][0]
    pkg_info_content = t.extractfile(pkg_info).read().decode('utf-8')
    new_pkg_info = fix_metadata_content(pkg_info_content)
    t.close()
    
    # Create new tar.gz
    temp_tar = 'dist/deepharvest-1.0.0.tar.gz.new'
    t2 = tarfile.open(temp_tar, 'w:gz')
    t = tarfile.open('dist/deepharvest-1.0.0.tar.gz', 'r:gz')
    for m in members:
        if m.name == pkg_info.name:
            info = tarfile.TarInfo(name=m.name)
            info.size = len(new_pkg_info.encode('utf-8'))
            info.mode = m.mode
            info.mtime = m.mtime
            t2.addfile(info, io.BytesIO(new_pkg_info.encode('utf-8')))
        else:
            t2.addfile(m, t.extractfile(m))
    t2.close()
    t.close()
    
    # Replace old file
    import time
    time.sleep(0.1)  # Brief pause to ensure file handles are closed
    if os.path.exists('dist/deepharvest-1.0.0.tar.gz'):
        os.remove('dist/deepharvest-1.0.0.tar.gz')
    os.rename(temp_tar, 'dist/deepharvest-1.0.0.tar.gz')
    print('Fixed tar.gz PKG-INFO')
else:
    print('tar.gz not found, skipping')

