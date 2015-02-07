#!/bin/bash
# ./unzip.sh /vagrant /usr/local user pass
greenplumZipFilePath=$1
installPath=$2
user=$3
password=$4
set -x
if [ ! -f "$greenplumZipFilePath" ]; then
	echo "Can't find $greenplumZipFilePath"
fi

if [ -z "$installPath" -o -z "$user" -o -z "$password" ]; then
	echo "Arguments can't be null"
fi

unzippedLocation=$(echo $greenplumZipFilePath | sed "s|/$(basename $greenplumZipFilePath)||g")

unzip -o $greenplumZipFilePath -d $unzippedLocation 
gpZippedDir=$(echo $greenplumZipFilePath | sed 's/.zip//g')
gpBinaryFile=$(find $gpZippedDir -name *.bin)
gpVersionName=$(echo $gpBinaryFile | egrep -o greenplum-db-[0-9.]+ | tail -1) 
escapedFileName=$(echo $gpBinaryFile | sed 's/\//\\\//g')

if [ ! -d $installPath/$gpVersionName ]; then
	mkdir -p $installPath/$gpVersionName
fi

echo "bla i made it here bla"
# Very very odd code. I'm grabbing a line in the bin file that begins with SKIP= with grep, then changing the $0 to the Greenplum
# Bin name, removing the SKIP= and removing the ticks, then evaluating that to get a line number and assigning that to the SKIP
# variable. This will be used below to untar the bin file.
SKIP=$(eval $(grep -a SKIP= $gpBinaryFile | sed -e "s/\$0/$escapedFileName/" -e 's/SKIP=//' -e 's/`//g'))
tail -n +${SKIP} $gpBinaryFile | tar zxf - -C $installPath/$gpVersionName

# do a check here if last command was successful if so  rm the directory that was used for the bin #FIXME
rm -rf $gpZippedDir

ln -s $installPath/$gpVersionName $installPath/greenplum-db

installPathEscaped=$(echo $installPath | sed 's/\//\\\//g')
sed -i "s/^GPHOME=.*$/GPHOME=$installPathEscaped\/$gpVersionName/g" $installPath/greenplum-db/greenplum_path.sh
source $installPath/greenplum-db/greenplum_path.sh

echo bla 2 i made it here
mv /tmp/hostfile_exkeys $installPath/greenplum-db/hostfile_exkeys

#FIXME
echo im calling gpseginstall here
#segReturn=$(gpseginstall -u ${user} -p ${password} -f $installPath/greenplum-db/hostfile_exkeys -c scelv)
gpseginstall -u ${user} -p ${password} -f $installPath/greenplum-db/hostfile_exkeys
segReturn=$?
if [ "$segReturn" != "0" ]; then
	echo "could not run gpseginstall correctly"
	exit 1
fi

#FIXME 
mv /tmp/gpinitsystem_config $installPath/greenplum-db/gpinitsystem_config
chown $user:$user $installPath/greenplum-db/gpinitsystem_config
su - $user -c "source $installPath/greenplum-db/greenplum_path.sh; gpinitsystem -c $installPath/greenplum-db/gpinitsystem_config -h $installPath/greenplum-db/hostfile_exkeys -a"
