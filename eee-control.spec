%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Summary: Asus Eee PC hardware control and configuration tool
Name: eee-control
Version: 0.9.6
Release: 1%{?dist}
URL: http://greg.geekmind.org/eee-control/
Group: Applications/System
#Source0: http://greg.geekmind.org/eee-control/src/%{name}-%{version}.tar.gz
# git clone git://greg.geekmind.org/eee-control.git && cd eee-control && git checkout 0.9.6
Source0: %{name}-%{version}.tar.gz
Source1: eee-control-daemon
Patch0: %{name}-desktop.patch
License: ISC
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch: i686
BuildRequires: desktop-file-utils
BuildRequires: gettext
BuildRequires: python-devel
BuildRequires: python-setuptools-devel
Requires(post): chkconfig
Requires(post): GConf2
Requires(postun): /sbin/service
Requires(pre): GConf2
Requires(preun): chkconfig
Requires(preun): GConf2
Requires(preun): /sbin/service
Requires: dbus-python
Requires: notify-python
Requires: pygtk2
Requires: gnome-python2-gconf

%description
eee-control is an easy-to-use utility that aims to be a one-stop solution
for all special Linux Eee PC needs. It allows you to configure hardware and
hotkeys, switch between performance levels (very much like Asus' Super
Hybrid Engine) and more.

Currently the models 701, 900, 900A, 901 and 1000/1000H are supported.

%prep
%setup -q
%patch0 -p1 -b .d
chmod -x eee-control-setup.sh

%build
CFLAGS="%{optflags}" %{__python} setup.py build
sh locale/update.sh

%install
rm -rf %{buildroot}
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

%{__install} -Dpm755 %{SOURCE1} %{buildroot}%{_initddir}/eee-control-daemon

desktop-file-validate %{buildroot}%{_datadir}/applications/eee-control-tray.desktop
desktop-file-validate %{buildroot}%{_sysconfdir}/xdg/autostart/eee-control-tray.desktop

rm %{buildroot}%{_bindir}/eee-{control-{setup.sh,query},dispswitch.sh}

%find_lang %{name}

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add eee-control-daemon
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
%{_datadir}/gconf/schemas/eee-control.schemas > /dev/null || :

%postun
if [ $1 -ge 1 ] ; then
    /sbin/service eee-control-daemon condrestart >/dev/null 2>&1 || :
fi

%pre
if [ $1 -gt 1 ] ; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
    %{_datadir}/gconf/schemas/eee-control.schemas >/dev/null || :
fi


%preun
if [ $1 -eq 0 ] ; then
    /sbin/service eee-control-daemon stop >/dev/null 2>&1
    /sbin/chkconfig --del eee-control-daemon
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
    %{_datadir}/gconf/schemas/eee-control.schemas > /dev/null || :
fi

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc doc/901-ACPI.txt doc/NOTES doc/README
%doc eee-control-query eee-control-setup.sh eee-dispswitch.sh
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/%{name}-daemon.conf
%{_sysconfdir}/xdg/autostart/eee-control-tray.desktop
%{_initddir}/eee-control-daemon
%{_bindir}/eee-control-daemon
%{_bindir}/eee-control-tray
%{python_sitelib}/EeeControl
%{python_sitelib}/eee_control-*.egg-info
%{_datadir}/%{name}
%{_datadir}/applications/eee-control-tray.desktop
%{_datadir}/gconf/schemas/%{name}.schemas

%changelog
* Fri Oct 08 2010 Dominik Mierzejewski <rpm@greysector.net> 0.9.6-1
- update to 0.9.6
- add missing BuildRequires
- generate translations

* Wed Jan 06 2010 Dominik Mierzejewski <rpm@greysector.net> 0.9.4-1
- update to 0.9.4
- fix python-gconf dependency name
- fix startup order
- add gconf schema scriptlets

* Mon Feb 23 2009 Dominik Mierzejewski <rpm@greysector.net> 0.6-2
- add missing dependency on python-gconf
- patch not to fail when fsb settings are not available

* Thu Oct 23 2008 Dominik Mierzejewski <rpm@greysector.net> 0.6-1
- initial build
- add Fedora-specific initscript
