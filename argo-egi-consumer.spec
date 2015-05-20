Name: argo-egi-consumer
Summary: A/R Comp Engine message consumer
Version: 1.4.0
Release: 7%{?dist}
License: ASL 2.0
Buildroot: %{_tmppath}/%{name}-buildroot
Group:     EGI/SA4
BuildArch: noarch
Source0:   %{name}-%{version}.tar.gz
Requires: stomppy >= 3.1.6
Obsoletes: ar-consumer

%description
Installs the service for consuming SAM monitoring results
from the EGI message broker infrastructure.

%build
python setup.py build

%prep
%setup -n %{name}-%{version}

%install 
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install --directory %{buildroot}/etc/init.d
install --directory %{buildroot}/etc/argo-egi-consumer/
install --directory %{buildroot}/%{_sharedstatedir}/argo-egi-consumer/

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%attr(0755,root,root) /usr/bin/argo-egi-consumer.py
%attr(0755,root,root) /etc/init.d/argo-egi-consumer
%attr(0750,arstats,arstats) %{_sharedstatedir}/argo-egi-consumer

%post
/sbin/chkconfig --add argo-egi-consumer

%pre
getent group arstats > /dev/null || groupadd -r arstats
getent passwd arstats > /dev/null || \
    useradd -r -g arstats -d /var/lib/argo-egi-consumer -s /sbin/nologin \
    -c "AR Comp Engine user" arstats

%preun
if [ "$1" = 0 ] ; then
   /sbin/service argo-egi-consumer --stop
   /sbin/chkconfig --del argo-egi-consumer
fi

%changelog
* Wed May 20 2015 Daniel Vrcic <dvrcic@srce.hr> - 1.4.0-7%{?dist}
- load selectively StreamHandler logger
* Tue May 19 2015 Daniel Vrcic <dvrcic@srce.hr> - 1.4.0-6%{?dist}
- subscribe to new destinations after config reload 
* Tue May 19 2015 Daniel Vrcic <dvrcic@srce.hr> - 1.4.0-5%{?dist}
- renamed package obsoletes old named one
* Tue May 19 2015 Daniel Vrcic <dvrcic@srce.hr> - 1.4.0-4%{?dist}
- prevent multiple threads reporting number of writmsgs
* Tue May 19 2015 Daniel Vrcic <dvrcic@srce.hr> - 1.4.0-3%{?dist}
- reference github issues 
* Tue May 19 2015 Daniel Vrcic <dvrcic@srce.hr> - 1.4.0-2%{?dist}
- remove autogenerated MANIFEST
- added VO topic
* Tue May 19 2015 Daniel Vrcic <dvrcic@srce.hr> - 1.4.0-1%{?dist}
- package and components renamed
- refactored source code 
  https://github.com/ARGOeu/ARGO/issues/129
- simplified configuration with case insensitive sections and options
- logging via syslog; report number of written messages
  https://github.com/ARGOeu/ARGO/issues/100
- daemon process privileges dropped via os sys interface
- added SIGHUP, SIGTERM handlers
- fixed bug with messages with paired service types
- setup.py with automatic version catch from spec 
* Fri Jan 30 2015 Luko Gjenero <lgjenero@gmail.com> - 1.3.2-0%{?dist}
- Fixed avro schema typo
* Thu Jan 15 2015 Luko Gjenero <lgjenero@gmail.com> - 1.3.2-0%{?dist}
- Added configs to rpm
* Thu Jan 15 2015 Luko Gjenero <lgjenero@gmail.com> - 1.3.1-0%{?dist}
- Fixes for Avro format + fix for reconneect
* Fri Nov 28 2014 Luko Gjerneo <lgjenero@gmail.com> - 1.3.0-0%{?dist}
- Added Avro format
* Thu Sep 4 2014 Emir Imamagic <eimamagi@srce.hr> - 1.2.1-1%{?dist}
- Consumer detailed files contain messages that split to multiple lines
* Tue Jul 22 2014 Emir Imamagic <eimamagi@srce.hr> - 1.2.0-1%{?dist}
- Add support for multiple file writters
- Add detailed probe results to the output
- Timestamps @ consumer error log file
* Fri Mar 14 2014 Luko Gjenero <lgjenero@srce.hr> - 1.1.1-0%{?dist}
- SSL broker connection
* Mon Nov 4 2013 Paschalis Korosoglou <pkoro@grid.auth.gr> - 1.0.1-2%{?dist}
- Fixes for consumer
* Thu Oct 3 2013 Paschalis Korosoglou <pkoro@grid.auth.gr> - 1.0.1-1%{?dist}
- Updates and fixes for consumer
* Thu Aug 1 2013 Emir Imamagic <eimamagi@srce.hr> - 1.0.0-1%{?dist}
- Initial release
