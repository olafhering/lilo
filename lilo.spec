#
# spec file for package lilo (Version 0.0.15)
#
# Copyright (c) 2004 SUSE LINUX AG, Nuernberg, Germany.
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://www.suse.de/feedback/
#

# norootforbuild
# neededforbuild  

BuildRequires: aaa_base acl attr bash bind-utils bison bzip2 coreutils cpio cpp cracklib cvs cyrus-sasl db devs diffutils e2fsprogs file filesystem fillup findutils flex gawk gdbm-devel glibc glibc-devel glibc-locale gpm grep groff gzip info insserv less libacl libattr libgcc libnscd libselinux libstdc++ libxcrypt libzio m4 make man mktemp module-init-tools ncurses ncurses-devel net-tools netcfg openldap2-client openssl pam pam-modules patch permissions popt procinfo procps psmisc pwdutils rcs readline sed strace syslogd sysvinit tar tcpd texinfo timezone unzip util-linux vim zlib zlib-devel autoconf automake binutils gcc gdbm gettext libtool perl rpm

Name:         lilo
#%%define     bootheader 0.0.5
%define lilo_vers  0.1.1
%define yaboot_vers 1.3.11
Group:        System/Boot
License:      BSD, Other License(s), see package
Obsoletes:    yaboot activate quik 
Requires:     hfsutils
Requires:     dosfstools
Requires:     /bin/awk /usr/bin/od /bin/sed /usr/bin/stat /bin/pwd /bin/ls
Summary:      The LInux LOader, a boot menu
Requires:     binutils
Version:      0.0.15
Release:      41
Source0:      lilo-%{lilo_vers}.tar.bz2
Source1:      http://penguinppc.org/projects/yaboot/yaboot-%{yaboot_vers}.tar.gz
Patch5:       yaboot-1.3.6.dif
Patch6:       yaboot-1.3.11-fat.dif
Patch7:       yaboot-hole_data-journal.diff
BuildRoot:    %{_tmppath}/%{name}-%{version}-build
# get rid of /usr/lib/rpm/brp-strip-debug 
# it kills the zImage.chrp-rs6k 
%define __os_install_post %{nil}

%description
The LInux-LOader: LILO boots Linux from your hard drive. It can also
boot other operating systems such as MS-DOS and OS/2, and can even boot
DOS from the second hard drive. The configuration file is in
/etc/lilo.conf.

The PowerPC variant can be used on new PowerMacs and CHRP machines.

The ix86 variant comes with Memtest86, offering an image that can be
booted to perform a memory test.



Authors:
--------
    John Coffman <JohnInSD@san.rr.com>
    Werner Almesberger <Werner.Almesberger@epfl.ch>
    PowerPC part:
    Paul Mackeras <paulus@samba.org>
    Cort Dougan <cort@fsmlabs.com>
    Benjamin Herrenschmidt <benh@kernel.crashing.org>

%prep
%setup -q -T -c -a 0 -a 1
mv lilo-%{lilo_vers} lilo.ppc
mv yaboot-%{yaboot_vers} yaboot
cd yaboot
%patch5
%patch7 -p1
cp second/yaboot.c second/yaboot_fat.c
%patch6 -p1
cd ..
find lilo.ppc/lib -name "*.sh" | xargs -r chmod 755
find lilo.ppc/lib -name addnote | xargs -r chmod 755
find lilo.ppc/lib -name hack-coff | xargs -r chmod 755
find lilo.ppc/lib -name mkprep | xargs -r chmod 755

%build
cd yaboot
make clean
make DEBUG=1 VERSION=1.3.11.SuSE yaboot
mv second/yaboot yaboot.debug
make clean
make DEBUG=0 VERSION=1.3.11.SuSE yaboot
mv second/yaboot yaboot
make clean
make DEBUG=1 VERSION=1.3.11.SuSE yaboot.chrp
mv second/yaboot.chrp yaboot.chrp.debug
make clean
make DEBUG=0 VERSION=1.3.11.SuSE yaboot.chrp
mv second/yaboot.chrp yaboot.chrp
make clean
make DEBUG=0 VERSION=1.3.11.SuSE yaboot.fat
mv second/yaboot.fat yaboot.fat
cd ..
#cd lilo
#make activate
#cd ..
cd lilo.ppc
gcc -Wall $RPM_OPT_FLAGS -s -o iseries-addRamDisk lilo-addRamDisk.c
gcc -Wall $RPM_OPT_FLAGS -s -o iseries-addSystemMap lilo-addSystemMap.c
gcc -Wall $RPM_OPT_FLAGS -s -o mkzimage_cmdline mkzimage_cmdline.c

%install
rm -rfv $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/lib/lilo/chrp
mkdir -p $RPM_BUILD_ROOT/lib/lilo/iseries
mkdir -p $RPM_BUILD_ROOT/lib/lilo/pmac
mkdir -p $RPM_BUILD_ROOT/sbin
mkdir -p $RPM_BUILD_ROOT/bin
mkdir -p $RPM_BUILD_ROOT/%{_docdir}/lilo/activate
cd lilo.ppc
cp -a iseries-* $RPM_BUILD_ROOT/lib/lilo/iseries
cp -a mkzimage_cmdline $RPM_BUILD_ROOT/lib/lilo/chrp
cp -a lib/* $RPM_BUILD_ROOT/lib/lilo
chmod 755 show_of_path.sh
chmod 754 lilo.{old,new}
cp -av lilo.old $RPM_BUILD_ROOT/sbin/lilo.old
cp -av lilo.new $RPM_BUILD_ROOT/sbin/lilo
cp -av lilo-pmac.lib $RPM_BUILD_ROOT/lib/lilo/lilo-pmac.lib
cp -av show_of_path.sh $RPM_BUILD_ROOT/bin
cp -av Finder.bin $RPM_BUILD_ROOT/lib/lilo/pmac
cp -av System.bin $RPM_BUILD_ROOT/lib/lilo/pmac
cp -av os-badge-icon $RPM_BUILD_ROOT/lib/lilo/pmac
cp -av README* $RPM_BUILD_ROOT%{_docdir}/lilo/
cp -av COPYING $RPM_BUILD_ROOT%{_docdir}/lilo/
cd ..
cd yaboot
cp -av yaboot yaboot.debug $RPM_BUILD_ROOT/lib/lilo/pmac
cp -av yaboot.chrp* yaboot.fat $RPM_BUILD_ROOT/lib/lilo/chrp
cd ..
#cd lilo
#install activate $RPM_BUILD_ROOT/sbin
#install -d -m 755 $RPM_BUILD_ROOT%{_docdir}/lilo/activate
#install -m 644 CHANGES COPYING INCOMPAT README $RPM_BUILD_ROOT%{_docdir}/lilo/activate
#find $RPM_BUILD_ROOT/lib/lilo -type f -print0 | xargs -0 chmod a-x

%triggerpostun  -- lilo < 0.0.10
# for manual updates
if [ -f /etc/lilo.conf.rpmsave -a ! -f /etc/lilo.conf ] ; then
mv -v /etc/lilo.conf.rpmsave /etc/lilo.conf
fi
exit 0

%files
%defattr (-,root,root)
/lib/lilo
#/sbin/activate
/sbin/lilo*
/bin/show_of_path.sh
%doc %{_docdir}/lilo

%changelog -n lilo
* Fri Oct 29 2004 - jplack@suse.de
- added fix for #47765
* Wed Oct 20 2004 - jplack@suse.de
- added a tested fix for #45565 at least for emulex FC cards
* Mon Oct 18 2004 - jplack@suse.de
- added some more fixes for #45565
* Thu Oct 07 2004 - jplack@suse.de
- remove OF path to partition if same as for the config file itself
* Thu Oct 07 2004 - jplack@suse.de
- check for all relevant files beeing on primary partitions, firmware
  has problems else ...
- added 'force_fat' option for some hopeless configurations
* Thu Oct 07 2004 - jplack@suse.de
- delete ambiguous PReP boot partitions (#42903)
* Thu Jul 08 2004 - jplack@suse.de
- fixed problem with leading zeros (#42854)
* Tue Jun 29 2004 - jplack@suse.de
- workaround an OF bug documented in #42517
* Wed Jun 23 2004 - jplack@suse.de
- fixed blocker bug #41772 - LTC9179-SLES9: Installation of RAID 1 failed
* Fri Jun 18 2004 - jplack@suse.de
- fixed critical bug #42207 - lilo does not handle /dev/root in /proc/mounts
* Thu Jun 17 2004 - jplack@suse.de
- use TMPDIR if set
* Thu Jun 17 2004 - jplack@suse.de
- fixed #42148, lilo cannot handle more than 10 partitions
* Wed Jun 16 2004 - olh@suse.de
- remove hardcoded /boot/System.map path on iseries (#42000)
  use prep binary boot header from current kernel-source package
  do not call /sbin/activate on prep anymore, its gone
  disable debug output in makezimage.sh scripts
* Thu Jun 03 2004 - jplack@suse.de
- entries without initrd have been errornously ignored
* Tue Jun 01 2004 - jplack@suse.de
- fixed #41333, do of screen init
* Fri May 28 2004 - jplack@suse.de
- fixed #41331, parser error
* Wed May 26 2004 - jplack@suse.de
- prevent parted from going interactive
* Tue May 25 2004 - jplack@suse.de
- ugly typo fixed / lilo stopped execution
* Tue May 25 2004 - jplack@suse.de
- remove moint point from OF path in show_of_path.sh (#40999)
* Mon May 24 2004 - jplack@suse.de
- fix yet another parser bug
* Wed May 19 2004 - jplack@suse.de
- merged lilo&bootheader tar balls, implemented smart PReP
  partition handling including expansion/shrinking on the fly.
* Thu May 13 2004 - jplack@suse.de
- follow symlinks to get file size, umount boot on clean up, clear
  LANG and LC_CTYPE on startup
* Wed May 12 2004 - jplack@suse.de
- better error handling, work around YaST bugs (e.g. boot="" bug),
  some smaller glitches
* Mon May 10 2004 - jplack@suse.de
- fixed typos for PowerMac G5s
* Fri May 07 2004 - jplack@suse.de
- create bootinfo object, more error checking, type conversion for
  PReP Boot partition
* Fri May 07 2004 - jplack@suse.de
- vscsi detection, #40002
* Wed May 05 2004 - jplack@suse.de
- fixed guessing of boot partition, various cleanups, fixed custom
  error handling.
* Mon May 03 2004 - jplack@suse.de
- fixed various pmac bugs/cleanup of pmac handling
* Mon May 03 2004 - jplack@suse.de
- fixed typo in lilo triggering bash bug, implemented booting from
  non standard file systems though a FAT boot file system (#34556)
  and others.
* Mon Apr 26 2004 - jplack@suse.de
- fixed show_of_path.sh: support for IPR controller and such #39033
  mounts /sys if needed, #39380
* Fri Apr 02 2004 - jplack@suse.de
- fixed show_of_path.sh: scsi_id and scsi_lun are given in hex
  instead of decimal
* Wed Mar 31 2004 - jplack@suse.de
- set OF variable boot-device to point to your boot device
* Tue Mar 30 2004 - jplack@suse.de
- fixes #37294: fixed command line handling, and #37291
* Fri Mar 26 2004 - jplack@suse.de
- workaround for possible bug in yaboot, avoid initrd option by
  using addRamdisk.sh, use fullpath for fdisk (path not set with
  init=/bin/bash)
* Wed Mar 24 2004 - jplack@suse.de
- fixed type, bug with device detection, lots of clean ups
* Tue Mar 23 2004 - jplack@suse.de
- update to bootheader-0.0.5, mac fix
* Tue Mar 23 2004 - jplack@suse.de
- update to version lilo-0.0.8, support of multiple boot= lines for
  iSeries, more clean ups
* Tue Mar 02 2004 - olh@suse.de
- make zImage helpers exectable, copy dummy .o file on chrp
* Sun Feb 22 2004 - olh@suse.de
- add make_zimage*.sh for pseries and iseries, fix prep script
* Mon Feb 16 2004 - olh@suse.de
- run /sbin/activate unconditionally
  handle devspec sysfs property for sata
* Thu Feb 12 2004 - olh@suse.de
- add make_zimage*.sh scripts for pmac coff and new pmac, prep
* Tue Feb 10 2004 - olh@suse.de
- add /lib/lilo/iseries/iseries-addRamDisk,
  from kernel-iseries64-tools
* Sat Jan 31 2004 - olh@suse.de
- update to yaboot-1.3.11
  update show_of_path.sh to use sysfs
  update lilo to use MacRISC* instead of compatible_machines.txt
  move files from /boot to /lib/lilo/
  preserve lilo.conf in postinstall
* Tue Dec 02 2003 - olh@suse.de
- move /boot/lib/chrp/* to /lib/lilo
* Wed Nov 13 2002 - olh@suse.de
- requires: binutils for linking the kernel on pseries
* Tue Nov 12 2002 - olh@suse.de
- support initrd on pseries
* Sat Nov 09 2002 - olh@suse.de
- add yaboot-hole_data-journal.diff
  fix loading of files with holes on reiserfs
* Thu Oct 17 2002 - olh@suse.de
- activate a kernel slot with the 'activate' config option
  zero cmdline in kernel slot
* Tue Aug 27 2002 - olh@suse.de
- remove some unwanted debug output on iSeries
* Tue Aug 27 2002 - olh@suse.de
- fix append= handling from last change
* Sun Aug 25 2002 - olh@suse.de
- better handling of iSeries specific options
  write kernel to kernel slot or stream file or prep boot partition
* Sun Aug 11 2002 - olh@suse.de
- check for empty image= line on newworld, avoids warning
* Sat Aug 03 2002 - olh@suse.de
- load system.map on new pmacs, for debugger
  unset boot-file on new pmacs, breaks yaboot
* Wed Jul 03 2002 - olh@suse.de
- use MacRISC as compatible string on pmac
* Sat Jun 29 2002 - olh@suse.de
- add yaboot-symlink-fix.diff (#16742), allow symlinks on reiserfs
* Mon Jan 14 2002 - olh@suse.de
- remove exit 0, no quoting for lilo.conf variables
* Fri Jan 11 2002 - olh@suse.de
- build a boot image with initrd=  on iSeries, when specified
* Thu Jan 10 2002 - olh@suse.de
- do not write to slot C on iSeries
* Wed Jan 09 2002 - olh@suse.de
- do not write to slot A on iSeries
* Wed Jan 09 2002 - olh@suse.de
- add root= option on iseries
* Tue Jan 08 2002 - olh@suse.de
- do not honor the boot-file/bootargs content in yaboot
* Tue Jan 08 2002 - olh@suse.de
- run lilo on iSeries
* Thu Dec 20 2001 - olh@suse.de
- do not call rpm postinstall
* Thu Dec 13 2001 - olh@suse.de
- update to yaboot 1.3.6, remove some partition type braindamage
* Tue Dec 04 2001 - olh@suse.de
- add new PowerBook
* Tue Dec 04 2001 - olh@suse.de
- running lilo on iSeries
* Tue Nov 13 2001 - olh@suse.de
- double MAX_TOKEN size to allow large init-message
* Thu Nov 08 2001 - olh@suse.de
- the last yaboot patch screwed the older changes, apply them again
* Thu Nov 08 2001 - olh@suse.de
- add patch to allow loading for zImage.initrd on ppc64
* Mon Oct 15 2001 - olh@suse.de
- fix yaboot.conf creation, sysmap= was wrong
* Mon Oct 15 2001 - olh@suse.de
- add patch from jeffm to fix image loading on chrp+reiserfs
* Mon Oct 08 2001 - olh@suse.de
- do nothing on oldworld when called with --lilo-rootdrive
  might be bad for your MacOS partition
* Wed Oct 03 2001 - olh@suse.de
- use --lilo-rootdrive when df / produce bogus output
  needed for installer
* Mon Sep 24 2001 - olh@suse.de
- do not exit when sysmap can not be loaded
* Sat Sep 22 2001 - olh@suse.de
- fix spacebar message
* Fri Sep 21 2001 - olh@suse.de
- change type of Mac OS Rom and install
* Fri Sep 21 2001 - olh@suse.de
- update yaboot to 1.2.5, fixes for ppc64
* Thu Sep 20 2001 - olh@suse.de
- fix sysmap for pmac
* Wed Sep 19 2001 - olh@suse.de
- fix sysmap path for chrp
* Sat Sep 15 2001 - olh@suse.de
- make spacebar useage more clear
* Fri Sep 14 2001 - olh@suse.de
- improve handling of spacebar in os-chooser
* Wed Sep 05 2001 - olh@suse.de
- fix specfile
* Wed Sep 05 2001 - olh@suse.de
- update yaboot to 1.2.3, use new os-chooser version per default
* Tue Aug 14 2001 - olh@suse.de
- fix filelist
* Mon Aug 13 2001 - olh@suse.de
- update compatible_machines.txt comment
* Mon Aug 13 2001 - olh@suse.de
- update lilo.sh, fix handling of HFSBOOTFOLDER
  use a different way to query keys in os-chooser script
  fix yaboot, netboot was broken in last update
* Wed Aug 08 2001 - olh@suse.de
- update compatible_machines.txt
* Wed Aug 08 2001 - olh@suse.de
- move compatible_machines.txt
  dont force copy on new Macs until yaboot is fixed
* Thu Aug 02 2001 - olh@suse.de
- fix birec calculation, needs still work for HFS load ...
* Wed Aug 01 2001 - olh@suse.de
- set sysmap_base to 0
* Tue Jul 31 2001 - olh@suse.de
- add yaboot-fix.diff for reiserfs mount
* Tue Jul 31 2001 - olh@suse.de
- update default lilo.conf
* Tue Jul 31 2001 - olh@suse.de
- update to current yaboot patch for reiserfs (jeffm)
  add sysmap loading patch and update version to 1.2.2
* Mon Jul 23 2001 - olh@suse.de
- fix the default= option when it is macos, use first kernel label
* Mon Jul 02 2001 - olh@suse.de
- bring back some modifications
  always copy the files on the new MacRISC2 machines
* Thu Jun 28 2001 - olh@suse.de
- fix yaboot.c  file_close
* Thu Jun 28 2001 - olh@suse.de
- miboot can read a config file now
* Mon Jun 18 2001 - olh@suse.de
- honor default= line in lilo.conf for macos booting
* Sat Jun 02 2001 - olh@suse.de
- update yaboot to 1.2.1, add reiserfs patches
* Fri Mar 09 2001 - olh@suse.de
- rename os-chooser to Mac OS Rom
  add some support for Mac OS X to lilo.conf
* Mon Mar 05 2001 - olh@suse.de
- add PowerMac4,1 for new flower power iMacs
* Tue Feb 27 2001 - olh@suse.de
- add PowerMac3,4 for new G4/466
* Tue Feb 27 2001 - olh@suse.de
- enable initrd creation again, loop-6 fix most problems
* Tue Feb 27 2001 - olh@suse.de
- update to 0.0.7
  update yaboot to 1.1.1, obsoletes chrp64 binary
  change /sbin/lilo to handle the new files
* Thu Feb 15 2001 - olh@suse.de
- disable misleading debug printf in yaboot
* Wed Feb 14 2001 - olh@suse.de
- handle first generation iMac in lilo
* Sun Feb 11 2001 - olh@suse.de
- handle /dev/hde in show_of_path.sh
* Sun Feb 11 2001 - olh@suse.de
- skip initrd creation with 2.4 kernel and old pmacs
  until the loop device is fixed
* Sun Feb 11 2001 - olh@suse.de
- add small fixes for chrp to yaboot
* Wed Jan 31 2001 - olh@suse.de
- add " screen" output to lilo itself
* Tue Jan 30 2001 - olh@suse.de
- activate partitions via nvsetenv on new PowerMacs
* Tue Jan 30 2001 - olh@suse.de
- avoid screen garbage on chrp serial console
* Tue Jan 30 2001 - olh@suse.de
- disable " screen" output, doesnt work anyway
* Sun Dec 17 2000 - olh@suse.de
- use yaboot 0.9 on pmac and chrp
* Sun Dec 17 2000 - olh@suse.de
- add support for System.map loading (sysmap=)
* Fri Dec 01 2000 - olh@suse.de
- remove quik, build debug binaries on CHRP
* Tue Oct 24 2000 - olh@suse.de
- clear BSS on chrp, fix typo in /sbin/lilo, use always yaboot.conf
* Thu Oct 12 2000 - olaf@suse.de
- update to yaboot 0.9 for chrp only, allows bootable CDs
* Mon Oct 09 2000 - olh@suse.de
- add POWER3 support to install yaboot.chrp{,.64}
* Fri Sep 29 2000 - olh@suse.de
- disable debug on chrp
* Wed Sep 27 2000 - olh@suse.de
- exit when no boot= is specified
* Wed Sep 27 2000 - olh@suse.de
- disable debug in yaboot.chrp, fix <NULL> output in defaultimage
* Thu Sep 21 2000 - olh@suse.de
- fix show_of_path, lilo.sh and yaboot.c at once
* Thu Sep 21 2000 - olh@suse.de
- update yaboot for chrp, update lilo to handle chrp
* Mon Sep 11 2000 - olh@suse.de
- add video=platinumfb:cmode:8 to System.bin, prevents garbage
* Sun Sep 10 2000 - olh@suse.de
- update to 0.0.6, update yaboot to 0.8
* Thu Jul 20 2000 - olh@suse.de
- update lilo to 0.0.3
* Wed Jul 19 2000 - olh@suse.de
- update lilo to 0.0.2, adapt quik
* Thu Jul 13 2000 - olh@suse.de
- update README and System.bin
* Wed Jul 12 2000 - olh@suse.de
- initial ppc release
