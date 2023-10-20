#!/bin/bash
START_DATE=$(date +%Y%m%d-%H%M%S)

CPATH=$(/usr/bin/dirname $0)
BACKUP_PATH="$CPATH/backup"
echo $CPATH 
mkdir -p "$CPATH/log/"
mkdir -p "$BACKUP_PATH"

echo "Removing old backup"
find "$BACKUP_PATH"/* -ctime +1 -type d -exec rm -fr {} \;

CURRENT_BACKUP="$BACKUP_PATH/${START_DATE}"
LOG="$CPATH/log/backup_${START_DATE}.log"
BACKUP_SCRIPT=/home/sysop/existdb-client/exist-distribution-6.0.1/bin/backup.sh 
HOSTS=("station1.webfarm.ms.ingv.it" "station2.webfarm.ms.ingv.it")
PROXY="NONE"
EXIST="NONE"
BACKUP="NONE"
host="NONE"
PASS=""

check_status() {
    
    ssh sysop@$host docker  compose -f /home/sysop/gitwork/eidaws-station/compose.yaml top > top-file.txt
    if [ $(cat top-file.txt | grep proxy | wc | cut -f 7  -d ' ') == 1 ];
    	then PROXY="UP";
	else PROXY="DOWN";
    fi
    if [ $(cat top-file.txt | grep fdsn | wc | cut -f 7  -d ' ') == 1 ];
	    then EXIST="UP";
	    else EXIST="DOWN";
    fi
    if [ $(cat top-file.txt | grep backup | wc | cut -f 7  -d ' ') == 1 ];
	    then BACKUP="UP";
	    else BACKUP="DOWN";
    fi
    echo "PROXY: $PROXY EXIST: $EXIST BACKUP: $BACKUP">>$LOG;

}



date >> $LOG
#echo "Removing old backup"
#find $BACKUP_PATH/* -cmin +10 -type d -exec rm -fr {} \;
echo "Backup fdsn station data collection" >> $LOG
echo "$BACKUP_SCRIPT -u admin -p $PASS -b /db/apps/fdsn-station-data -d $CURRENT_BACKUP -ouri=xmldb:exist://10.140.0.248/exist/xmlrpc" >> $LOG
$BACKUP_SCRIPT -u admin -p $PASS -b /db/apps/fdsn-station-data -d $CURRENT_BACKUP -ouri=xmldb:exist://10.140.0.248/exist/xmlrpc
echo "Backup end" >> $LOG 
date >> $LOG
echo "Restoring" >> $LOG

for host in ${HOSTS[@]}; do
    check_status
    echo "PROXY: $PROXY EXIST: $EXIST BACKUP: $BACKUP";
    if [[ $PROXY=="UP" ]]  && [[ $BACKUP=="DOWN" ]] &&  [[ $EXIST=="UP" ]];
    then
      echo "Restoring on host: " $host >> $LOG
      echo "ssh sysop@$host docker compose -f /home/sysop/gitwork/eidaws-station/compose.yaml start backup" >> $LOG
      ssh sysop@$host docker compose -f /home/sysop/gitwork/eidaws-station/compose.yaml start backup >> $LOG
      echo "ssh sysop@$host docker compose -f /home/sysop/gitwork/eidaws-station/compose.yaml stop proxy" >> $LOG
      ssh sysop@$host docker compose -f /home/sysop/gitwork/eidaws-station/compose.yaml stop proxy >> $LOG


      check_status
      echo "PROXY: $PROXY EXIST: $EXIST BACKUP: $BACKUP";
    
      if [[ $PROXY=="DOWN" ]]  && [[ $BACKUP=="UP" ]] &&  [[ $EXIST=="UP" ]];
      then

        echo "Restoring on host: " $host >> $LOG
        echo "/home/sysop/existdb-client/exist-distribution-6.0.1/bin/backup.sh -u admin -p $PASS -r ${CURRENT_BACKUP}/db/apps/fdsn-station-data/__contents__.xml -ouri=xmldb:exist://$host:8080/exist/xmlrpc" >> $LOG
        /home/sysop/existdb-client/exist-distribution-6.0.1/bin/backup.sh -u admin -p $PASS -r ${CURRENT_BACKUP}/db/apps/fdsn-station-data/__contents__.xml -ouri=xmldb:exist://$host:8080/exist/xmlrpc >> $LOG
        
	if [[ $? -eq 0 ]]; then
		RESTORE="OK"
	else
		RESTORE="FAIL"
	fi

        echo "ssh sysop@$host docker compose -f /home/sysop/gitwork/eidaws-station/compose.yaml stop backup" >> $LOG
        ssh sysop@$host docker compose -f /home/sysop/gitwork/eidaws-station/compose.yaml stop backup >> $LOG
        echo "ssh sysop@$host docker compose -f /home/sysop/gitwork/eidaws-station/compose.yaml start proxy" >> $LOG
        ssh sysop@$host docker compose -f /home/sysop/gitwork/eidaws-station/compose.yaml start proxy >> $LOG
      fi
    
      check_status
      echo "PROXY: $PROXY EXIST: $EXIST BACKUP: $BACKUP";
    
      if [[ $RESTORE=="OK" ]] && [[ $PROXY=="UP" ]]  && [[ $BACKUP=="DOWN" ]] &&  [[ $EXIST=="UP" ]];
        then
	  echo "SUCCESS" >> $LOG
        else
          echo "SYNC FAILED"
      fi

    date >> $LOG
    fi
done
