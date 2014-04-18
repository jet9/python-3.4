python-3.4 rpm build tools
==========================

!!! USER AT YOUR OWN RISK !!!
It's not tested carefully

BUILD:
------

*Requirements:* mock(used for mock builds)

````
mkdir -p ~/rpmbuild/SOURCES/
cd ~/rpmbuild/SOURCES/
wget https://www.python.org/ftp/python/3.4.0/Python-3.4.0.tgz
rpmbuild -bs python-3.4.spec
/usr/bin/mock ~/rpmbuild/SRPMS/python34-python-3.4.0-1.el6.src.rpm

