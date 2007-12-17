# Copyright (c) 2000-2006, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section        free

Name:           tanukiwrapper
Version:        3.2.3
Release:        %mkrel 0.0.4
Summary:        Java Service Wrapper
Epoch:          0
License:        BSD
URL:            http://wrapper.tanukisoftware.org/
Source0:        http://download.sourceforge.net/wrapper/wrapper_3.2.3_src.tar.gz
Patch1:         %{name}-build.patch
Patch2:         %{name}-crosslink.patch
Patch3:         %{name}-makefile-linux-x86-32.patch
#Add Makefiles so package builds for all FC architectures.
Patch4:         %{name}-Makefile-s390-s390x-ppc.patch
# The following patch is only needed for GCJ.
Patch5:         %{name}-nosun-jvm-64.patch
Group:          Development/Java
BuildRequires:  java-rpmbuild >= 0:1.6
BuildRequires:  ant >= 0:1.6.1
BuildRequires:  ant-nodeps >= 0:1.6.1
BuildRequires:  ant-junit
BuildRequires:  xerces-j2
BuildRequires:  xml-commons-apis
Requires:       jpackage-utils >= 0:1.6
Obsoletes:      %{name}-demo < 0:3.1.2-2jpp
%if %{gcj_support}
BuildRequires:   java-gcj-compat-devel
%else
BuildRequires:   java-devel
BuildRequires:   java-javadoc
%endif

%description
The Java Service Wrapper is an application which has 
evolved out of a desire to solve a number of problems 
common to many Java applications: 

- Run as a Windows Service or Unix Daemon
- Application Reliability
- Standard, Out of the Box Scripting
- On Demand Restarts
- Flexible Configuration
- Ease Application installations
- Logging

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.

%prep
%setup -q -n wrapper_%{version}_src
%patch1
%patch2
%patch3
%patch4
# The following patch is only needed for GCJ.
%if %{gcj_support}
%patch5
%endif
find . -name "*.jar" -exec %__rm -f {} \;
%__perl -p -i -e 's/\r//' doc/AUTHORS
%__perl -p -i -e 's|-O3|%optflags|' src/c/Makefile*
%__perl -p -e \
  's|=\.\./lib/wrapper\.jar$|=%{_javadir}/%{name}.jar| ;
   s|=\.\./lib$|=%{_libdir}|' \
  src/conf/wrapper.conf.in > wrapper.conf.sample
%__perl -p -e \
  's|"\./wrapper"|"%{_sbindir}/%{name}"| ;
   s|"\.\./conf/wrapper\.conf"|"/path/to/wrapper.conf"|' \
  src/bin/sh.script.in > script.sh.sample

%build
export OPT_JAR_LIST="ant/ant-junit ant/ant-nodeps"
export CLASSPATH=$(build-classpath ant junit xerces-j2 xml-commons-apis)
%ifarch x86_64 ia64 ppc64 sparc64 s390x
bits=64
%else
bits=32
%endif
%ant -Dbuild.sysclasspath=first -Djdk.api=%{_javadocdir}/java -Dbits=$bits \
  main jdoc

%install
%__rm -rf %{buildroot}

# jar
%__mkdir_p %{buildroot}%{_javadir}
%__install -p -m 0644 lib/wrapper.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; do %{__ln_s}f ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# jni
%__install -d -m 755 %{buildroot}%{_libdir}
%__install -p -m 755 lib/libwrapper.so %{buildroot}%{_libdir}

# commands
%__install -d -m 755 %{buildroot}%{_sbindir}
%__install -p -m 755 bin/wrapper %{buildroot}%{_sbindir}/%{name}

# javadoc
%__install -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
%__cp -a jdoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
%__ln_s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
%__rm -rf %{buildroot}

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc doc/license.txt *.sample
%attr(0755,root,root) %{_sbindir}/%{name}
%attr(0755,root,root) %{_libdir}/libwrapper.so
%{_javadir}/%{name}*.jar
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/tanukiwrapper-%{version}.jar.*
%endif

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%doc doc/*
