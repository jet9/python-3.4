##########################
#  User-modifiable configs
##########################

#  Is the resulting package and the installed binary named "python" or
#  "python2"?
#WARNING: Commenting out doesn't work.  Last line is what's used.
%define config_binsuffix none
%define config_binsuffix 3.4

#  Build tkinter?  "auto" enables it if /usr/bin/wish exists.
#WARNING: Commenting out doesn't work.  Last line is what's used.
%define config_tkinter no
%define config_tkinter yes
%define config_tkinter auto

#  Use pymalloc?  The last line (commented or not) determines wether
#  pymalloc is used.
#WARNING: Commenting out doesn't work.  Last line is what's used.
%define config_pymalloc no
%define config_pymalloc yes

#  Enable IPV6?
#WARNING: Commenting out doesn't work.  Last line is what's used.
%define config_ipv6 yes
%define config_ipv6 no

#  Build shared libraries or .a library?
#WARNING: Commenting out doesn't work.  Last line is what's used.
%define config_sharedlib no
%define config_sharedlib yes

#  Location of the HTML directory.
%define config_htmldir /var/www/html/python

#################################
#  End of user-modifiable configs
#################################

%define name python
#--start constants--
%define version 3.4.0
%define libvers 3.4
#--end constants--
%define release 1.el6
%define __prefix /usr

#  kludge to get around rpm <percent>define weirdness
%define ipv6 %(if [ "%{config_ipv6}" = yes ]; then echo --enable-ipv6; else echo --disable-ipv6; fi)
%define pymalloc %(if [ "%{config_pymalloc}" = yes ]; then echo --with-pymalloc; else echo --without-pymalloc; fi)
%define binsuffix %(if [ "%{config_binsuffix}" = none ]; then echo ; else echo "%{config_binsuffix}"; fi)
%define include_tkinter %(if [ \\( "%{config_tkinter}" = auto -a -f /usr/bin/wish \\) -o "%{config_tkinter}" = yes ]; then echo 1; else echo 0; fi)
%define libdirname %(( uname -m | egrep -q '_64$' && [ -d /usr/lib64 ] && echo lib64 ) || echo lib)
%define sharedlib %(if [ "%{config_sharedlib}" = yes ]; then echo --enable-shared; else echo ; fi)
%define include_sharedlib %(if [ "%{config_sharedlib}" = yes ]; then echo 1; else echo 0; fi)

#  detect if documentation is available
%define include_docs %(if [ -f "%{_sourcedir}/html-%{version}.tar.bz2" ]; then echo 1; else echo 0; fi)

Summary: An interpreted, interactive, object-oriented programming language.
Name: %{name}34-%{name}
Version: %{version}
Release: %{release}
License: PSF
Group: Development/Languages
Source: Python-%{version}.tgz
%if %{include_docs}
Source1: html-%{version}.tar.bz2
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: expat-devel
BuildRequires: db4-devel
BuildRequires: gdbm-devel
BuildRequires: sqlite-devel
Prefix: %{__prefix}
Packager: Dmitry Kurbatov <dk@dimcha.ru>
#AutoReqProv: no
Provides: python(abi) = %{binsuffix}
Provides: libpython%{binsuffix}m.so.1.0


%description
Python is an interpreted, interactive, object-oriented programming
language.  It incorporates modules, exceptions, dynamic typing, very high
level dynamic data types, and classes. Python combines remarkable power
with very clear syntax. It has interfaces to many system calls and
libraries, as well as to various window systems, and is extensible in C or
C++. It is also usable as an extension language for applications that need
a programmable interface.  Finally, Python is portable: it runs on many
brands of UNIX, on PCs under Windows, MS-DOS, and on the Mac.

%package devel
Summary: The libraries and header files needed for Python extension development.
Requires: python34-python = %{version}
Group: Development/Libraries

%description devel
The Python programming language's interpreter can be extended with
dynamically loaded extensions and can be embedded in other programs.
This package contains the header files and libraries needed to do
these types of tasks.

Install python-devel if you want to develop Python extensions.  The
python package will also need to be installed.  You'll probably also
want to install the python-docs package, which contains Python
documentation.

%if %{include_tkinter}
%package tkinter
Summary: A graphical user interface for the Python scripting language.
Group: Development/Languages
#Requires: python%{binsuffix} = %{version}-%{release}
Requires: python34-python = %{version}-%{release}

%description tkinter
The Tkinter (Tk interface) program is an graphical user interface for
the Python scripting language.

You should install the tkinter package if you'd like to use a graphical
user interface for Python programming.
%endif

%package tools
Summary: A collection of development tools included with Python.
Group: Development/Tools
Requires: python34-python = %{version}-%{release}

%description tools
The Python package includes several development tools that are used
to build python programs.  This package contains a selection of those
tools, including the IDLE Python IDE.

Install python-tools if you want to use these tools to develop
Python programs.  You will also need to install the python and
tkinter packages.

%if %{include_docs}
%package docs
Summary: Python-related documentation.
Group: Development/Documentation

%description docs
Documentation relating to the Python programming language in HTML and info
formats.
%endif

%changelog
* Wed Apr 16 2014 Dmitry Kurbatov <dk@dimcha.ru> 3.4.0-1.el6
- Added spec for CentOS/RHEL 6.5

#######
#  PREP
#######
%prep
%setup -n Python-%{version}

########
#  BUILD
########
%build
echo "Setting for ipv6: %{ipv6}"
echo "Setting for pymalloc: %{pymalloc}"
echo "Setting for binsuffix: %{binsuffix}"
echo "Setting for include_tkinter: %{include_tkinter}"
echo "Setting for libdirname: %{libdirname}"
echo "Setting for sharedlib: %{sharedlib}"
echo "Setting for include_sharedlib: %{include_sharedlib}"
./configure --enable-unicode=ucs4 %{sharedlib} %{ipv6} %{pymalloc} --prefix=%{__prefix}
make

##########
#  INSTALL
##########
%install
#  set the install path
echo '[install_scripts]' >setup.cfg
echo 'install_dir='"${RPM_BUILD_ROOT}%{__prefix}/bin" >>setup.cfg

[ -d "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}/lib-dynload
make prefix=$RPM_BUILD_ROOT%{__prefix} install

#  REPLACE PATH IN PYDOC
if [ ! -z "%{binsuffix}" ]
then
   (
      cd $RPM_BUILD_ROOT%{__prefix}/bin
      mv pydoc%{binsuffix} pydoc.old
      sed 's|#!.*|#!%{__prefix}/bin/env python'%{binsuffix}'|' \
            pydoc.old >pydoc
      chmod 755 pydoc
      rm -f pydoc.old
   )
fi

#  add the binsuffix
if [ ! -z "%{binsuffix}" ]
then
   mv $RPM_BUILD_ROOT%{__prefix}/bin/python%{binsuffix} $RPM_BUILD_ROOT%{__prefix}/bin/python
   rm -f $RPM_BUILD_ROOT%{__prefix}/bin/python[0-9a-zA-Z]*
   ( cd $RPM_BUILD_ROOT%{__prefix}/bin; 
      for file in *; do mv "$file" "$file"%{binsuffix}; done )
   #( cd $RPM_BUILD_ROOT%{_mandir}/man1; mv python.1 python%{binsuffix}.1 )
   ln -s python%{binsuffix} $RPM_BUILD_ROOT%{__prefix}/bin/python%{binsuffix}m
fi

########
#  Tools
echo '#!%{__prefix}/bin/env python%{binsuffix}' >${RPM_BUILD_ROOT}%{__prefix}/bin/idle%{binsuffix}
echo 'import os, sys' >>${RPM_BUILD_ROOT}%{__prefix}/bin/idle%{binsuffix}
echo 'os.execvp("%{__prefix}/bin/python%{binsuffix}", ["%{__prefix}/bin/python%{binsuffix}", "%{__prefix}/lib/python%{libvers}/idlelib/idle.py"] + sys.argv[1:])' >>${RPM_BUILD_ROOT}%{__prefix}/bin/idle%{binsuffix}
echo 'print "Failed to exec Idle"' >>${RPM_BUILD_ROOT}%{__prefix}/bin/idle%{binsuffix}
echo 'sys.exit(1)' >>${RPM_BUILD_ROOT}%{__prefix}/bin/idle%{binsuffix}
chmod 755 $RPM_BUILD_ROOT%{__prefix}/bin/idle%{binsuffix}
cp -a Tools $RPM_BUILD_ROOT%{__prefix}/%{libdirname}/python%{libvers}

#  MAKE FILE LISTS
rm -f mainpkg.files
#find "$RPM_BUILD_ROOT""%{__prefix}"/%{libdirname}/python%{libvers} -type f |
find "$RPM_BUILD_ROOT""%{__prefix}"/ -type f -o -type l |
	sed "s|^${RPM_BUILD_ROOT}|/|" |
	grep -v -e '/python%{libvers}/config$' -e '_tkinter.so$' -e '/man1/' -e '/python%{libvers}/Tools' >mainpkg.files
find "$RPM_BUILD_ROOT""%{__prefix}"/bin -type f -o -type l |
	sed "s|^${RPM_BUILD_ROOT}|/|" |
	grep -v -e '/bin/2to3%{binsuffix}$' |
	grep -v -e '/bin/pydoc%{binsuffix}$' |
	grep -v -e '/bin/smtpd.py%{binsuffix}$' |
	grep -v -e '/bin/idle%{binsuffix}$' >>mainpkg.files

rm -f tools.files
find "$RPM_BUILD_ROOT""%{__prefix}"/%{libdirname}/python%{libvers}/idlelib \
      "$RPM_BUILD_ROOT""%{__prefix}"/%{libdirname}/python%{libvers}/Tools -type f |
      sed "s|^${RPM_BUILD_ROOT}|/|" >tools.files
echo "%{__prefix}"/bin/2to3%{binsuffix} >>tools.files
echo "%{__prefix}"/bin/pydoc%{binsuffix} >>tools.files
#echo "%{__prefix}"/bin/smtpd.py%{binsuffix} >>tools.files
echo "%{__prefix}"/bin/idle%{binsuffix} >>tools.files

######
# Docs
%if %{include_docs}
mkdir -p "$RPM_BUILD_ROOT"%{config_htmldir}
(
   cd "$RPM_BUILD_ROOT"%{config_htmldir}
   bunzip2 < %{SOURCE1} | tar x
)
%endif

#  fix the #! line in installed files
find "$RPM_BUILD_ROOT" -type f -print0 |
      xargs -0 grep -l /usr/local/bin/python | while read file
do
   FIXFILE="$file"
   sed 's|^#!.*python|#!%{__prefix}/bin/env python'"%{binsuffix}"'|' \
         "$FIXFILE" >/tmp/fix-python-path.$$
   cat /tmp/fix-python-path.$$ >"$FIXFILE"
   rm -f /tmp/fix-python-path.$$
done

#  check to see if there are any straggling #! lines
find "$RPM_BUILD_ROOT" -type f | xargs egrep -n '^#! */usr/local/bin/python' \
      | grep ':1:#!' >/tmp/python-rpm-files.$$ || true
if [ -s /tmp/python-rpm-files.$$ ]
then
   echo '*****************************************************'
   cat /tmp/python-rpm-files.$$
   cat <<@EOF
   *****************************************************
     There are still files referencing /usr/local/bin/python in the
     install directory.  They are listed above.  Please fix the .spec
     file and try again.  If you are an end-user, you probably want
     to report this to jafo-rpms@tummy.com as well.
   *****************************************************
@EOF
   rm -f /tmp/python-rpm-files.$$
   exit 1
fi
rm -f /tmp/python-rpm-files.$$

########
#  CLEAN
########
%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT
rm -f mainpkg.files tools.files

########
#  FILES
########
%files -f mainpkg.files
%defattr(-,root,root)
%doc Misc/README Misc/Porting
%doc LICENSE Misc/ACKS Misc/HISTORY Misc/NEWS
%{_mandir}/man1/python*

%attr(755,root,root) %dir %{__prefix}/include/python%{libvers}m
%attr(755,root,root) %dir %{__prefix}/%{libdirname}/python%{libvers}/
%if %{include_sharedlib}
%{__prefix}/%{libdirname}/python*
%endif

%files devel
%defattr(-,root,root)
%{__prefix}/include/python%{libvers}m/*.h
#%{__prefix}/%{libdirname}/python%{libvers}/config

%files -f tools.files tools
%defattr(-,root,root)

%if %{include_tkinter}
%files tkinter
%defattr(-,root,root)
%{__prefix}/%{libdirname}/python%{libvers}/tkinter
%{__prefix}/%{libdirname}/python%{libvers}/lib-dynload/_tkinter.so*
%endif

%if %{include_docs}
%files docs
%defattr(-,root,root)
%{config_htmldir}/*
%endif

%post
/sbin/ldconfig
