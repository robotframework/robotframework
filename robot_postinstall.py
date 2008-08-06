import os
import sys


def egg_preinstall(package_path, scripts):
    """Updates platform specific startup scripts.
    
    Run as part of the easy_install egg creation procedure. This is the only way 
    to get the scripts updated when the easy_install is used. Updates the 
    scripts before the egg is created and therefore the created egg cannot be
    used at any other machine unless the Python and Jython installations are 
    exactly equal.
    """
    robot_dir = _get_robot_target_dir(os.path.basename(package_path))
    if robot_dir is None: 
        print """Could not find site-packages from PYTHONPATH! 
Robot Framework start-up scripts needs to be updated manually."""
    else:
        _update_scripts(scripts, package_path, robot_dir)


def generic_install(script_names, script_dir, robot_dir):
    """Updates given startup scripts.
    
    Run as part of the generic installation procedure from 'setup.py' after 
    running 'python setyp.py install'.
    """
    _update_scripts(script_names, script_dir, robot_dir)


def windows_binary_install():
    """Updates start-up scripts.
    
    Executed as the last part of Windows binary installation started by 
    running 'robot-<version>.win32.exe'.
    """
    scripts = ['pybot.bat','jybot.bat', 'rebot.bat']
    script_dir = os.path.join(sys.prefix, 'Scripts')
    python_exe = os.path.join(sys.prefix, 'python.exe')  # sys.executable doesn't work here
    try:
        _update_scripts(scripts, script_dir, _get_robot_location(), python_exe)
        print '\nInstallation was successful. Happy Roboting!'
    except Exception, err:
        print '\nRunning post-install script failed: %s' % err
        print 'Robot Framework start-up scripts may not work correctly.'


def windows_binary_uninstall():
    """Deletes Jython compiled files ('*$py.class')
    
    This function is executed as part of the Windows binary uninstallation
    started from 'Add/Remove Programs'.
    
    Uninstaller deletes files only if installer has created them and also
    deletes directories only if they are empty. Thus compiled files created
    by Jython must be deleted separately.
    """
    for base, dirs, files in os.walk(_get_robot_location()):
        for name in files:
            if name.endswith('$py.class'):
                path = os.path.join(base, name)
                try:
                    os.remove(path)
                except Exception, err:
                    print "Failed to remove Jython compiled file '%s': %s" \
                            % (path, str(err))


def _get_robot_target_dir(version):
    site_packages = _get_site_packages()
    if site_packages is None:
        return None
    major, minor = sys.version_info[0:2]
    version = version.replace('-', '_').replace('_', '-', 1)
    egg_name = '%s-py%s.%s.egg' % (version, major, minor)
    return os.path.join(site_packages, egg_name, 'robot')
    
def _get_site_packages():
    for path in sys.path:
        path = os.path.normpath(path)
        if os.path.basename(path) == 'site-packages':
            return path
    return None


def _get_robot_location():
    try:
        import robot
        return os.path.dirname(os.path.abspath(robot.__file__))
    except:
        return os.path.join(sys.prefix, 'Lib', 'site-packages', 'robot')

def _update_scripts(scripts, script_dir, robot_dir, python_exe=sys.executable):
    jython_exe, how_found = _find_jython()
    print 'Creating Robot Framework start-up scripts...'
    print 'Installation directory:', robot_dir
    print 'Python executable:', python_exe
    print 'Jython executable: %s (%s)' % (jython_exe, how_found)
    for script in scripts:
        path = os.path.join(script_dir, script)
        content = _read(path)
        for pattern, replace in [ ('[ROBOT_DIR]', robot_dir),
                                  ('[PYTHON_EXECUTABLE]', python_exe),
                                  ('[JYTHON_EXECUTABLE]', jython_exe) ]:
            content = content.replace(pattern, replace)
        _write(path, content)
        name = os.path.splitext(os.path.basename(script))[0].capitalize()
        print '%s script: %s' % (name, path)

    
def _read(path):
    reader = open(path)
    content = reader.read()
    reader.close()
    return content


def _write(path, content):
    os.chmod(path, 0755)
    writer = open(path, 'w')
    writer.write(content)
    writer.close()

    
def _find_jython():
    """Tries to find path to Jython and returns it and how it was found.
    
    First Jython is searched from PATH, then checked is JYTHON_HOME set and
    finally Jython installation directory is searched from the system.
    """
    jyexe, search_dirs = _get_platform_jython_search_items()
    env1, env2 = os.sep == '/' and ('$','') or ('%','%')
    if _jython_in_path(jyexe):
        return jyexe, 'in %sPATH%s' % (env1, env2)
    elif _is_jython_dir(os.environ.get('JYTHON_HOME','notset'), jyexe):
        jyexe = os.path.join(os.environ['JYTHON_HOME'], jyexe)
        return jyexe, 'from %sJYTHON_HOME%s' % (env1, env2)
    return _search_jython_from_dirs(search_dirs, jyexe)

def _get_platform_jython_search_items():
    """Returns Jython executable and a list of dirs where to search it"""
    if os.name == 'nt':
        return 'jython.bat', ['C:\\', 'D:\\']
    elif  sys.platform.count('cygwin'):
        return 'jython.bat', ['/cygdrive/c', '/cygdrive/d']
    else:
        return 'jython', ['/usr/local','/opt']

def _jython_in_path(jyexe):
    out = os.popen('%s --version 2>&1' % jyexe )
    found = out.read().startswith('Jython 2.')
    out.close()
    return found

def _search_jython_from_dirs(search_dirs, jyexe, recursions=1,
                             raise_unless_found=False):
    excl_dirs = ['WINNT','RECYCLER']  # no need to search from these
    for dir in search_dirs:
        try:
            dirs = [ os.path.join(dir,item) for item in os.listdir(dir)
                     if item not in excl_dirs ]
        except:     # may not have rights to read the dir etc.
            continue
        dirs = [ item for item in dirs if os.path.isdir(item) ]
        matches = [ item for item in dirs if _is_jython_dir(item, jyexe) ]
        if len(matches) > 0:
            # if multiple matches, the last one probably the latest version
            return os.path.join(dir, matches[-1], jyexe), 'found from system'
        if recursions > 0:
            try:
                return _search_jython_from_dirs(dirs, jyexe, recursions-1, True)
            except ValueError:
                pass
    if raise_unless_found:
        raise ValueError, 'not found'
    return jyexe, 'default value'
    
def _is_jython_dir(dir, jyexe):
    if not os.path.basename(os.path.normpath(dir)).lower().startswith('jython'):
        return False
    try:
        items = os.listdir(dir)
    except:   # may not have rights to read the dir etc.
        return False
    return jyexe in items and 'jython.jar' in items
    

if __name__ == '__main__':
    # This is executed when run as a post-install script for Windows binary
    # distribution. Executed both when installed and when uninstalled from
    # Add/Remove Programs. For more details see 
    # 5.3 Creating Windows Installers
    # http://docs.python.org/dist/postinstallation-script.html
    #
    # If installation is done using 'easy_install', this script is not run
    # automatically. It is possible to run this script manually without 
    # arguments to update start-up scripts in that case.
    if len(sys.argv) < 2 or sys.argv[1] == '-install':
        windows_binary_install()
    elif sys.argv[1] == '-remove':
        windows_binary_uninstall()
