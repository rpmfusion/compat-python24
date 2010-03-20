%define unicode ucs4
%define tkinter compat-tkinter24

%define pybasever 2.4
%define jp_codecs 1.4.11
%define tools_dir %{_libdir}/python%{pybasever}/Tools
%define demo_dir %{_libdir}/python%{pybasever}/Demo
%define doc_tools_dir %{_libdir}/python%{pybasever}/Doc/tools

# added by knurd on 20080810 to get it running for RPM Fusion
%define _default_patch_fuzz 2

Summary: An interpreted, interactive, object-oriented programming language
Name: compat-python24
Version: %{pybasever}.6
Release: 1%{?dist}
License: Python Software Foundation License v2
Group: Development/Languages
Source: http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.bz2
Source5: http://www.python.jp/pub/JapaneseCodecs/JapaneseCodecs-%{jp_codecs}.tar.gz
Source6: http://gigue.peabody.jhu.edu/~mdboom/omi/source/shm_source/shmmodule.c
Source7: compat-python-2.3.4-optik.py

Patch0: compat-python-2.4.3-config.patch
Patch3: compat-Python-2.2.1-pydocnogui.patch
Patch7: compat-python-2.3.4-lib64-regex.patch
Patch8: compat-python-2.4.4-lib64.patch
Patch9: compat-japanese-codecs-lib64.patch
Patch13: compat-python-2.4-distutils-bdist-rpm.patch
Patch14: compat-python-2.3.4-pydocnodoc.patch
Patch15: compat-python-2.4.1-canonicalize.patch
Patch16: compat-python-2.4-gen-assert.patch
Patch17: compat-python-2.4-webbrowser.patch
Patch18: compat-python-2.4.3-cflags.patch
Patch19: compat-python-2.4.3-locale.patch
Patch20: compat-python-2.4.5-db47.patch
Patch21: compat-python-2.4-db48.patch
Patch22: compat-python-2.4-config-db48.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: readline-devel, libtermcap-devel, openssl-devel, gmp-devel
BuildRequires: ncurses-devel, gdbm-devel, zlib-devel, expat-devel
BuildRequires: libGL-devel tk tix gcc-c++ libX11-devel glibc-devel
BuildRequires: bzip2 tar /usr/bin/find pkgconfig tcl-devel tk-devel
BuildRequires: tix-devel bzip2-devel
BuildRequires: autoconf
# Make sure db4 4.8 is used if fedora >= 13
%if 0%{?fedora} >= 13
BuildRequires: db4-devel >= 4.8
%else
BuildRequires: db4-devel >= 4.3
%endif

URL: http://www.python.org/
Provides: python-abi = 2.4, python(abi) = 2.4

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that need
a programmable interface. This package contains most of the standard
Python modules, as well as modules for interfacing to the Tix widget
set for Tk and RPM.

Note that documentation for Python is provided in the python-docs
package.

%package devel
Summary: The libraries and header files needed for Python development
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install python-devel if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%package tools
Summary: A collection of development tools included with Python
Group: Development/Tools
Requires: %{name} = %{version}-%{release}
Requires: %{tkinter} = %{version}-%{release}

%description tools
The Python package includes several development tools that are used
to build python programs.

%package -n %{tkinter}
Summary: A graphical user interface for the Python scripting language
Group: Development/Languages
BuildRequires:  tcl, tk
Requires: %{name} = %{version}-%{release}

%description -n %{tkinter}

The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.

%prep
%setup -q -n Python-%{version} -a 5

%patch0 -p1 -b .rhconfig
%patch3 -p1 -b .no_gui
# disabled by knurd on 20080810, as it broken on rawhide
# (likely due to the new rpm)
#if %{_lib} == lib64
%ifarch x86_64 ppc64
%patch7 -p1 -b .lib64-regex
%patch8 -p1 -b .lib64
%patch9 -p0 -b .lib64-j
%endif
%patch13 -p1 -b .bdist-rpm
%patch14 -p1 -b .no-doc
%patch15 -p1 -b .canonicalize
%patch16 -p2 -b .gen-assert
%patch17 -p0 -b .web-browser
%patch18 -p1 -b .cflags
%patch19 -p2 -b .locale
%patch20 -p1 -b .db4
# Conditionally patch for db4 4.8
%if 0%{?fedora} >= 13
%patch21 -p1 -b .db48
%patch22 -p1 -b .db48
%endif


# This shouldn't be necesarry, but is right now (2.2a3)
find -name "*~" |xargs rm -f

# Temporary workaround to avoid confusing find-requires: don't ship the tests
# as executable files
chmod 0644 Lib/test/test_*.py

# shm module
cp %{SOURCE6} Modules
cat >> Modules/Setup.dist << EOF

# Shared memory module
shm shmmodule.c
EOF

# Backwards compatible optik
install -m 0644 %{SOURCE7} Lib/optik.py

%build
topdir=`pwd`
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC"
export LINKCC="gcc"
if pkg-config openssl ; then
    export CFLAGS="$CFLAGS `pkg-config --cflags openssl`"
    export LDFLAGS="$LDFLAGS `pkg-config --libs-only-L openssl`"
fi
# Force CC
export CC=gcc
# For patch 15, need to get a newer configure generated out of configure.in
autoconf
%configure --enable-ipv6 --enable-unicode=%{unicode} --enable-shared

make OPT="$CFLAGS" %{?_smp_mflags}
LD_LIBRARY_PATH=$topdir $topdir/python Tools/scripts/pathfix.py -i "%{_bindir}/env python%{pybasever}" .
make OPT="$CFLAGS" %{?_smp_mflags}

%install
[ -d $RPM_BUILD_ROOT ] && rm -fr $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr $RPM_BUILD_ROOT%{_mandir}

# Clean up patched .py files that are saved as .lib64
for f in distutils/command/install distutils/sysconfig; do
    rm -f Lib/$f.py.lib64
done

make install DESTDIR=$RPM_BUILD_ROOT
# Fix the interpreter path in binaries installed by distutils 
# (which changes them by itself)
# Make sure we preserve the file permissions
for fixed in $RPM_BUILD_ROOT%{_bindir}/pydoc; do
    sed 's,#!.*/python$,#!%{_bindir}/env python%{pybasever},' $fixed > $fixed- \
        && cat $fixed- > $fixed && rm -f $fixed-
done

# tools

mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages

#modulator
cat > ${RPM_BUILD_ROOT}%{_bindir}/modulator << EOF
#!/bin/bash
exec %{_libdir}/python%{pybasever}/site-packages/modulator/modulator.py
EOF
chmod 755 ${RPM_BUILD_ROOT}%{_bindir}/modulator
cp -r Tools/modulator \
  ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages/

#pynche
cat > ${RPM_BUILD_ROOT}%{_bindir}/pynche << EOF
#!/bin/bash
exec %{_libdir}/python%{pybasever}/site-packages/pynche/pynche
EOF
chmod 755 ${RPM_BUILD_ROOT}%{_bindir}/pynche
rm -f Tools/pynche/*.pyw
cp -r Tools/pynche \
  ${RPM_BUILD_ROOT}%{_libdir}/python%{pybasever}/site-packages/

mv Tools/modulator/README Tools/modulator/README.modulator
mv Tools/pynche/README Tools/pynche/README.pynche

#gettext
install -m755  Tools/i18n/pygettext.py $RPM_BUILD_ROOT%{_bindir}/
install -m755  Tools/i18n/msgfmt.py $RPM_BUILD_ROOT%{_bindir}/

# Useful development tools
install -m755 -d $RPM_BUILD_ROOT%{tools_dir}/scripts
install Tools/README $RPM_BUILD_ROOT%{tools_dir}/
install Tools/scripts/*py $RPM_BUILD_ROOT%{tools_dir}/scripts/

# Documentation tools
install -m755 -d $RPM_BUILD_ROOT%{doc_tools_dir}
install -m755 Doc/tools/mkhowto $RPM_BUILD_ROOT%{doc_tools_dir}

# Useful demo scripts
install -m755 -d $RPM_BUILD_ROOT%{demo_dir}
cp -ar Demo/* $RPM_BUILD_ROOT%{demo_dir}

# Get rid of crap
find $RPM_BUILD_ROOT/ -name "*~"|xargs rm -f
find $RPM_BUILD_ROOT/ -name ".cvsignore"|xargs rm -f
find . -name "*~"|xargs rm -f
find . -name ".cvsignore"|xargs rm -f
#zero length
rm -f $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/site-packages/modulator/Templates/copyright

# Clean up the testsuite - we don't need compiled files for it
find $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/test \
    -name "*.pyc" -o -name "*.pyo" | xargs rm -f
rm -f $RPM_BUILD_ROOT%{_libdir}/python2.2/LICENSE.txt


#make the binaries install side by side with the main python
pushd $RPM_BUILD_ROOT%{_bindir}
mv idle idle%{pybasever}
mv modulator modulator%{pybasever}
mv pynche pynche%{pybasever}
mv pygettext.py pygettext%{pybasever}.py
mv msgfmt.py msgfmt%{pybasever}.py
mv smtpd.py smtpd%{pybasever}.py
mv pydoc pydoc%{pybasever}
popd

# Japanese codecs
pushd JapaneseCodecs-%{jp_codecs}
# We need to set LD_LIBRARY_PATH since python is now compiled as shared, and
# we always want to use the currently compiled one
LD_LIBRARY_PATH=$RPM_BUILD_ROOT%{_libdir} \
    ../python setup.py install --root=$RPM_BUILD_ROOT
popd

find $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/lib-dynload -type d | sed "s|$RPM_BUILD_ROOT|%dir |" > dynfiles
find $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/lib-dynload -type f | grep -v "_tkinter.so$" | sed "s|$RPM_BUILD_ROOT||" >> dynfiles

# Fix for bug #136654
rm -f $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/email/test/data/audiotest.au $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/test/audiotest.au

# Fix bug #143667: python should own /usr/lib/python2.x on 64-bit machines
#if %{_lib} == lib64
%ifarch x86_64 ppc64
install -d $RPM_BUILD_ROOT/usr/lib/python%{pybasever}/site-packages
%endif

# Make python-devel multilib-ready (bug #192747, #139911)
%define _pyconfig32_h pyconfig-32.h
%define _pyconfig64_h pyconfig-64.h

%ifarch ppc64 s390x x86_64 ia64
%define _pyconfig_h %{_pyconfig64_h}
%else
%define _pyconfig_h %{_pyconfig32_h}
%endif
mv $RPM_BUILD_ROOT%{_includedir}/python%{pybasever}/pyconfig.h \
   $RPM_BUILD_ROOT%{_includedir}/python%{pybasever}/%{_pyconfig_h}
cat > $RPM_BUILD_ROOT%{_includedir}/python%{pybasever}/pyconfig.h << EOF
#include <bits/wordsize.h>

#if __WORDSIZE == 32
#include "%{_pyconfig32_h}"
#elif __WORDSIZE == 64
#include "%{_pyconfig64_h}"
#else
#error "Unkown word size"
#endif
EOF

# Fix for bug 201434: make sure distutils looks at the right pyconfig.h file
sed -i -e "s/'pyconfig.h'/'%{_pyconfig_h}'/" $RPM_BUILD_ROOT%{_libdir}/python%{pybasever}/distutils/sysconfig.py

# Remove conflicting files
rm -f $RPM_BUILD_ROOT%{_bindir}/pydoc*
rm -rf $RPM_BUILD_ROOT%{_mandir}/*/*
rm -f $RPM_BUILD_ROOT%{_bindir}/python 


%clean
rm -fr $RPM_BUILD_ROOT

%files -f dynfiles
%defattr(-, root, root)
%doc LICENSE README
#%{_bindir}/pydoc*
%{_bindir}/python2.4
#%{_mandir}/*/*
%{_libdir}/libpython%{pybasever}.so*

%dir %{_libdir}/python%{pybasever}
%{_libdir}/python%{pybasever}/site-packages/japanese.pth
%dir %{_libdir}/python%{pybasever}/site-packages
%{_libdir}/python%{pybasever}/site-packages/japanese
%{_libdir}/python%{pybasever}/site-packages/README
%{_libdir}/python%{pybasever}/LICENSE.txt
%{_libdir}/python%{pybasever}/*.py*
%{_libdir}/python%{pybasever}/*.doc
%{_libdir}/python%{pybasever}/bsddb
%dir %{_libdir}/python%{pybasever}/config
%{_libdir}/python%{pybasever}/config/Makefile
%{_libdir}/python%{pybasever}/curses
%{_libdir}/python%{pybasever}/distutils
%{_libdir}/python%{pybasever}/encodings
%{_libdir}/python%{pybasever}/idlelib
%{_libdir}/python%{pybasever}/lib-old
%{_libdir}/python%{pybasever}/logging
%{_libdir}/python%{pybasever}/xml
%{_libdir}/python%{pybasever}/email
%{_libdir}/python%{pybasever}/compiler
%{_libdir}/python%{pybasever}/plat-linux2
%{_libdir}/python%{pybasever}/hotshot
#if %{_lib} == lib64
%ifarch x86_64 ppc64
%attr(0755,root,root) %dir /usr/lib/python%{pybasever}
%attr(0755,root,root) %dir /usr/lib/python%{pybasever}/site-packages
%endif

%files devel
%defattr(-,root,root)
/usr/include/*
%{_libdir}/python%{pybasever}/config
%{_libdir}/python%{pybasever}/test

%files tools
%defattr(-,root,root,755)
%doc Tools/modulator/README.modulator
%doc Tools/pynche/README.pynche
%{_libdir}/python%{pybasever}/site-packages/modulator
%{_libdir}/python%{pybasever}/site-packages/pynche
%{_bindir}/smtpd*.py*
%{_bindir}/idle*
%{_bindir}/modulator*
%{_bindir}/pynche*
%{_bindir}/pygettext*.py*
%{_bindir}/msgfmt*.py*
%{tools_dir}
%{demo_dir}
%{_libdir}/python%{pybasever}/Doc

%files -n %{tkinter}
%defattr(-,root,root,755)
%{_libdir}/python%{pybasever}/lib-tk
%{_libdir}/python%{pybasever}/lib-dynload/_tkinter.so

%changelog
* Sat Mar 20 2010 Jonathan Steffan <jonathansteffan a gmail.com> - 2.4.6-1
- Update to 2.4.6
- Add a patch for bdb 4.8

* Sat Oct 10 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 2.4.5-7
- rebuilt

* Thu Apr  2 2009 Hans de Goede <j.w.r.degoede@hhs.nl> 2.4.5-6
- Link db4 module against db-4.7 not 4.6 (oops)

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 2.4.5-5
- rebuild for new F11 features

* Wed Feb 04 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 2.4.5-4
- rebuild for new ssl

* Sat Sep 27 2008 Hans de Goede <j.w.r.degoede@hhs.nl> 2.4.5-3
- Fix building with db4 4.7.x

* Sun Aug 10 2008 Thorsten Leemhuis <fedora at leemhuis.info> 2.4.5-2.1
- _default_patch_fuzz 2 for now

* Sun Aug 10 2008 Thorsten Leemhuis <fedora at leemhuis.info> 2.4.5-2
- rebuild for RPM Fusion
- apply 64bit patches on x86_64 and ppc64 only

* Thu Mar 27 2008 Jonathan Steffan <jonathansteffan a gmail.com> 2.4.5-1
- Update to 2.4.5

* Fri Nov 30 2007 Jonathan Steffan <jonathansteffan a gmail.com> 2.4.4-3
- Update patch for db46
- Added patch to turn on debug printing for db detection
- Updated config patch for DB 4.6, this is not downstream compatible 

* Fri Aug 17 2007 Jonathan Steffan <jonathansteffan a gmail.com> 2.4.4-2
- Updated tkinter to be compat-tkinter

* Mon Jun 18 2007 Jonathan Steffan <jonathansteffan a gmail.com> 2.4.4-1
- Initial package based on fc6 srpm
