#!/bin/bash
#
# find a OF bootpath on Apple PowerMacs Newworld machines
# olh@suse.de (2000)
#
# When booting via BootX then all symlinks are gone ...
# The MacOS removes them and BenH didn't find (yet) a way to
# bring them back.
# If it looks like a hack then you don't need fielmann.de
#
# Changes
#
# 2000-04-26  get rid of strings
# 2000-04-13  get rid of awk, no success
# 2000-03-28  fix scsi on new macs when boot via bootx
# 2000-02-21  giving up and guess it all from aliases ;-)
# 2000-02-20  finish scsi host, works only with one host for now ...
# 2000-02-01  find ide hosts
# 2000-01-30  first try with scsi hosts
#


# argument must be a file
FILENAME="$1"
if [ ! "$1" ]; then FILENAME="/" ; fi
#echo try to figure out the OpenFirmware path to $FILENAME

# cut /dev/
FILEDEVICE=$(df "$FILENAME"|grep "^/dev/"|cut -d "/" -f 3|sed 's/ .*$//')

# cut  a-z and 0-9
FILEPARTITION=$(echo $FILEDEVICE | sed 's/[a-z]*//')
FILE_HOST_DEVICE=$(echo $FILEDEVICE | sed 's/[0-9].*//')
#echo $FILEDEVICE $FILE_HOST_DEVICE

# sd* scsi disks , hd* ide disks , sr* cdroms
case "$FILE_HOST_DEVICE" in
	sd*)
#		echo $FILENAME is on SCSI drive $FILEDEVICE
		PROC_DEVICETREE_BROKEN="0"
		PROC_DEVICETREE_SYMLINKS=$(find /proc/device-tree/ -maxdepth 1 -type l)
		if [ ! "$PROC_DEVICETREE_SYMLINKS" ] ; then
			PROC_DEVICETREE_PCIENTRY=$(find /proc/device-tree/ -name pci -maxdepth 1|wc -l)
			if [ "$PROC_DEVICETREE_PCIENTRY" -gt 1 ] ; then
				echo "There is no symlink in /proc/device-tree/ and"
				echo "there is more than one pci directory in /proc/device-tree/."
				echo "Booting via BootX removes them and I can't figure out SCSI disks "
				echo "I will try /proc/device-tree/chosen/bootpath"
				PROC_DEVICETREE_BROKEN="$(cat /proc/device-tree/chosen/bootpath|grep -v ata|sed 's/.:.*$//')"
				if [ ! "$PROC_DEVICETREE_BROKEN" ] ; then
					echo "There is 'ata' in /proc/device-tree/chosen/bootpath"
					echo "Seems not to be a SCSI boot drive"
					echo -n "ERROR ... "
				fi
			fi
		fi

	if [ "$PROC_DEVICETREE_BROKEN" = "0" ] ; then 
		FILE_HOST_SUBDEVICE=${FILE_HOST_DEVICE##sd}
		FILE_HOST_SUBDEVICE_NUMBER=$[$(echo $FILE_HOST_SUBDEVICE | tr a-z 0-9)+1]
#		echo looking for $FILE_HOST_SUBDEVICE_NUMBER. scsi disk

# find the attached scsi disks = "Direct-Access" and stop at sda=1 sdb=2 or whatever
# count in 3 lines steps 
		xcount=0
		for i in $( seq 1 $[ $( grep -v ^Attach /proc/scsi/scsi | wc -l ) /3] ) ; do
			x=$(grep -v ^Attach /proc/scsi/scsi |head -n $[$i*3]|tail -n 3)
			xtype=$(echo $x|sed 's/^.*Type://'|awk '$1 { print $1}')
			xid=$(echo $x|sed 's/^.*Id: //'|awk '$1 ~ /[0-9]*/ { print $1 }'|sed 's/^0//')
			xhost=$(echo $x|sed 's/^.*Host: //'|awk '$1 { print $1 }'|sed 's/^[a-z]*//')
#			echo x $x 
#			echo xtype $xtype xid $xid xhost $xhost i $i
#			echo xcount $xcount
			if [ "$xtype" = "Direct-Access" ] ; then 
				xcount=$[$xcount+1]				
				if [ "$FILE_HOST_SUBDEVICE_NUMBER" = "$xcount" ] ; then
					break 2
				fi
			fi
		done
#		echo $xcount xcount $xhost xhost
		SCSI_HOSTS=$(/sbin/lspci -n|grep "\(Class 0100:\|Class 0000:\)"|wc -l)
# echo $SCSI_HOSTS SCSI_HOSTS
		for i in $(seq 1 $SCSI_HOSTS);do
			SCSI_HOST_TMP=$(/sbin/lspci -n|grep "\(Class 0100:\|Class 0000:\)"|cut -d " " -f 4) 
			SCSI_HOST_VENDOR_[$i]=$(echo $SCSI_HOST_TMP|cut -d ":" -f 1)
			SCSI_HOST_DEVICE_["$i"]=$(echo $SCSI_HOST_TMP|cut -d ":" -f 2)
#			echo ${SCSI_HOST_DEVICE_[$i]} ${SCSI_HOST_VENDOR_[$i]} $SCSI_HOST_TMP
		done

		xcount=1
		for i in `find /proc/device-tree -name vendor-id` ; do
			i=`dirname $i`
#			echo i $i
			for x in $( seq 1 $SCSI_HOSTS) ; do
			VENDOR_ID_TMP=$(hexdump -n 4 -s 2 $i/vendor-id|head -n 1|awk '$2 { print $2 }')
			DEVICE_ID_TMP=$(hexdump -n 4 -s 2 $i/device-id|head -n 1|awk '$2 { print $2 }')
#			echo DEVICE_ID_TMP $DEVICE_ID_TMP VENDOR_ID_TMP $VENDOR_ID_TMP
			if [ "$VENDOR_ID_TMP" = "${SCSI_HOST_VENDOR_[$x]}" -a "$DEVICE_ID_TMP" = "${SCSI_HOST_DEVICE_[$x]}" ] ; then
			OF_DEVICE_[$xcount]=$(echo $i|sed 's/^\/.*device-tree//'|sed 's/\@[0-9a-z]*\//\//g'|sed 's/\@[0-9a-z]*$//')
#				echo i $i   blah --------------------------
#				echo OF_DEVICE ${OF_DEVICE_[$xcount]}
				xcount=$[$xcount+1]
				break 2
			fi
			done
		done
#		echo $xcount
	fi
#echo $FILENAME
#echo $FILEDEVICE
#echo $FILEPARTITION
#echo $FILE_HOST_DEVICE
#echo $FILE_HOST_SUBDEVICE
#echo $FILE_HOST_SUBDEVICE_NUMBER

# echo possible blubb is:
for i in $(seq 1 $SCSI_HOSTS) ; do
	echo "${OF_DEVICE_[$i]}"/@"$xid":"$FILEPARTITION","$FILENAME"
done

	;;
	hda)
#		echo trying hda
		PATH_IS_CDROM=$(grep "^drive name:" /proc/sys/dev/cdrom/info|grep hda)
#		echo $PATH_IS_CDROM
		if [ -z "$PATH_IS_CDROM" ] ; then
#			echo blubb hda
			HDA_PATH=$(cat /proc/device-tree/aliases/ultra0)
			echo "ultra0":"$FILEPARTITION","$FILENAME"
		else
#			echo blah hda
			HDA_PATH=$(cat /proc/device-tree/aliases/cd)
			echo "cd":"$FILEPARTITION","$FILENAME"
		fi
	;;
	hdb)
#		echo trying hdb
		PATH_IS_CDROM=$(grep "^drive name:" /proc/sys/dev/cdrom/info|grep hdb)
#		echo $PATH_IS_CDROM
		if [ -z "$PATH_IS_CDROM" ] ; then
#			echo blubb hda
			HDA_PATH=$(cat /proc/device-tree/aliases/ultra1)
			echo "ultra1":"$FILEPARTITION","$FILENAME"
		else
#			echo blah hda
			HDA_PATH=$(cat /proc/device-tree/aliases/cd)
			echo "cd":"$FILEPARTITION","$FILENAME"
		fi
	;;
	scd*|sr)
		echo SCSI CDROM $FILE_HOST_DEVICE
		echo not yet implemented
		exit 1
	;;
esac

# echo waiting for the patch.
