#!/usr/bin/env python
###
# Version 1.0 - Alex Lindner/01.02.2023
# add OptionParser
# check_isam_board_availability
# check_isam_board_operational_status
###
# Version 1.1 - Alex Lindner/02.02.2023
# check_isam_auto_backup_status
# check_isam_pon_utilization
# check_isam_board_temperature
###
# Version 1.2 - Alex Lindner/07.02.2023
# check_isam_board_temperature
#  - added range to warning/critical perf-data
###
# Version 1.3 - Alex Lindner/06.10.2023
# check_isam_nt_redundancy
###
# Nagios Exit-Codes:
# 0 = OK
# 1 = WARNING
# 2 = CRITICAL
# 3 = UNKNOWN
###


import sys
from optparse import OptionParser
from easysnmp import snmp_get,snmp_walk


def get_board_actual_type(hostname,community):
#   query device and return actual board type

    return snmp_walk("1.3.6.1.4.1.637.61.1.23.3.1.3",hostname=hostname,community=community,version=2,timeout=10,retries=0)


def check_isam_board_availability(hostname,community,slot_mapping,verbose):
#   checks the availability status of all boards

    oid_availability_status = "1.3.6.1.4.1.637.61.1.23.3.1.8"
    dict_availability_status = {0:"unknown",1:"available",2:"selftest in progress",3:"failed",4:"powered off",5:"not installed",6:"offline",7:"dependency"}
    snmp_availability_status = ""
    snmp_actual_type = ""
    code_warning = 0
    code_critical = 0
    code_unknown = 0

    snmp_availability_status = snmp_walk(oid_availability_status,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_actual_type = get_board_actual_type(hostname,community)

    if snmp_availability_status and snmp_actual_type:
        if verbose:
            print("\nSNMP - board availability status:")
            for item in snmp_availability_status: print("%s" % item)
            print("\nSNMP - board actual type:")
            for item in snmp_actual_type: print("%s" % item)

#       walk through boards and set codes
#       ommit last board (-1) which is always unknown
        i = 0
        while(i < len(snmp_actual_type)-1):
            if verbose: print("board_type: %s - availability: %s" % (snmp_actual_type[i].value,dict_availability_status[int(snmp_availability_status[i].value)]))
            if int(snmp_availability_status[i].value) == 2: code_warning = 1
            elif int(snmp_availability_status[i].value) in [3,4,6,7]: code_critical = 1
            elif int(snmp_availability_status[i].value) == 0: code_unknown = 1
            i += 1

#       print plugin-output and generate performance-data
        if code_critical: print("ISAM Board Availability-Status is CRITICAL | availability=2;1;2;0;3\n")
        elif code_warning: print("ISAM Board Availability-Status is WARNING | availability=1;1;2;0;3\n")
        elif code_unknown: print("ISAM Board Availability-Status is UNKNOWN | availability=3;1;2;0;3\n")
        else: print("ISAM Board Availability-Status is OK | availability=0;1;2;0;3\n")

#       loop through boards backwards -> output from plugin should be equal to board-position in chassis
#       ommit the last board (-2) which is always unknown
        i = len(snmp_actual_type)-2
        while(i >= 0):
            print("%-*s: %-*s : %s" % (11,slot_mapping[int(snmp_actual_type[i].oid.rsplit('.',1)[-1])],6,snmp_actual_type[i].value,dict_availability_status[int(snmp_availability_status[i].value)]))
            i -= 1

        if code_critical: sys.exit(2)
        elif code_warning: sys.exit(1)
        elif code_unknown: sys.exit(3)
        else: sys.exit(0)

    else:
        print("UNKNOWN - An SNMP error occured")
        sys.exit(3)


def check_isam_board_operational_status(hostname,community,slot_mapping,verbose):
#   checks the operational status of all boards

    oid_operational_status = "1.3.6.1.4.1.637.61.1.23.3.1.7"
    dict_operational_status = {0:'unknown',1:'no-error',2:'type-mismatch',3:'board-missing',4:'board-installation-missing',5:'no-planned-board',6:'waiting-for-sw',7:'init-boot-failed',8:'init-download-failed',9:'init-connection-failed',10:'init-configuration-failed',11:'board-reset-protection',12:'invalid-parameter',13:'temperature-alarm',14:'temperature-shutdown',15:'defense',16:'board-not-licensed',17:'sem-power-fail',18:'sem-ups-fail',19:'board-in-incompatible-slot',20:'download-ongoing',255:'unknown-error'}
    list_warning = [5,6,16,19]
    list_critical = [2,3,4,7,8,9,10,11,12,13,14,15,17,18,20,255]
    snmp_operational_status = ""
    snmp_actual_type = ""
    code_warning = 0
    code_critical = 0
    code_unknown = 0

    snmp_operational_status = snmp_walk(oid_operational_status,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_actual_type = get_board_actual_type(hostname,community)

    if snmp_operational_status and snmp_actual_type:
        if verbose:
            print("\nSNMP - board operational status:")
            for item in snmp_operational_status: print("%s" % item)
            print("\nSNMP - board actual type:")
            for item in snmp_actual_type: print("%s" % item)

#       walk through boards and set codes
#       ommit last board (-1) which is always unknown
        i = 0
        while(i < len(snmp_actual_type)-1):
            if verbose: print("board_type: %s - operational_status: %s" % (snmp_actual_type[i].value,dict_operational_status[int(snmp_operational_status[i].value)]))
            if int(snmp_operational_status[i].value) in list_warning: code_warning = 1
            elif int(snmp_operational_status[i].value) in list_critical: code_critical = 1
            elif int(snmp_operational_status[i].value) == 0: code_unknown = 1
            i += 1

#       print plugin-output and generate performance-data
        if code_critical: print("ISAM Board Operational-Status is CRITICAL | operational_state=2;1;2;0;3\n")
        elif code_warning: print("ISAM Board Operational-Status is WARNING | operational_state=1;1;2;0;3\n")
        elif code_unknown: print("ISAM Board Operational-Status is UNKNOWN | operational_state=3;1;2;0;3\n")
        else: print("ISAM Board Operational-Status is OK | operational_state=0;1;2;0;3\n")

#       loop through boards backwards -> output from plugin should be equal to board-position in chassis
#       ommit the last board (-2) which is always unknown
        i = len(snmp_actual_type)-2
        while(i >= 0):
            print("%-*s: %-*s : %s" % (11,slot_mapping[int(snmp_actual_type[i].oid.rsplit('.',1)[-1])],6,snmp_actual_type[i].value,dict_operational_status[int(snmp_operational_status[i].value)]))
            i -= 1

        if code_critical: sys.exit(2)
        elif code_warning: sys.exit(1)
        elif code_unknown: sys.exit(3)
        else: sys.exit(0)

    else:
        print("UNKNOWN - An SNMP error occured")
        sys.exit(3)


def check_isam_auto_backup_status(hostname,community,verbose):
#   checks the status of the auto-backup feature

    oid_dn_progress = "1.3.6.1.4.1.637.61.1.24.2.4.0"
    oid_up_progress = "1.3.6.1.4.1.637.61.1.24.2.9.0"
    oid_dn_error = "1.3.6.1.4.1.637.61.1.24.2.5.0"
    oid_up_error = "1.3.6.1.4.1.637.61.1.24.2.10.0"
    dict_progress = {0:"unknown",1:"ongoing",2:"finished and successfull",3:"finished but failed"}
    dict_dn_error = {0:"unknown",1:"file not found",2:"access violation",3:"disk full - allocation needed",4:"illegal tftp-operation",5:"unknown transfer-id",6:"file already exists",7:"no such user",8:"corrupted database - incomplete database",9:"system restart",10:"no error",11:"corrupted iss-config",12:"corrupted iss-prot-config"}
    dict_up_error = {0:"unknown",1:"file not found",2:"access violation",3:"disk full - allocation needed",4:"illegal tftp-operation",5:"unknown transfer-id",6:"file already exists",7:"no such user",8:"selected database not available",9:"system restart",10:"no error",11:"another SWDB process is ongoing"}
    snmp_dn_progress = 0
    snmp_up_progress = 0
    snmp_dn_error = 0
    snmp_up_error = 0

    snmp_dn_progress = snmp_get(oid_dn_progress,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_up_progress = snmp_get(oid_up_progress,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_dn_error = snmp_get(oid_dn_error,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_up_error = snmp_get(oid_up_error,hostname=hostname,community=community,version=2,timeout=10,retries=0)

    if snmp_dn_progress and snmp_up_progress and snmp_dn_error and snmp_up_error:
        if verbose:
            print("\nSNMP - download progress: %s" % snmp_dn_progress)
            print("SNMP - upload progress: %s" % snmp_up_progress)
            print("SNMP - download error: %s" % snmp_dn_error)
            print("SNMP - upload error: %s" % snmp_up_error)

        if int(snmp_dn_progress.value) == 2 and int(snmp_up_progress.value) == 2 and int(snmp_dn_error.value) == 10 and int(snmp_up_error.value) == 10:
            print("ISAM Auto-Backup is OK\nDB Download: %s => %s\nDB Upload: %s => %s" % (dict_progress[int(snmp_dn_progress.value)],dict_dn_error[int(snmp_dn_error.value)],dict_progress[int(snmp_up_progress.value)],dict_up_error[int(snmp_up_error.value)]))
            print("| backup_status=0;1;2;0;3")
            sys.exit(0)

        elif int(snmp_dn_progress.value) == 0 or int(snmp_up_progress.value) == 0 or int(snmp_dn_error.value) == 0 or int(snmp_up_error.value) == 0:
            print("ISAM Auto-Backup is UNKNOWN\nDB Download: %s => %s\nDB Upload: %s => %s" % (dict_progress[int(snmp_dn_progress.value)],dict_dn_error[int(snmp_dn_error.value)],dict_progress[int(snmp_up_progress.value)],dict_up_error[int(snmp_up_error.value)]))
            print("| backup_status=3;1;2;0;3")
            sys.exit(3)

        elif int(snmp_dn_progress.value) == 1 or int(snmp_up_progress.value) == 1:
            print("ISAM Auto-Backup is WARNING\nDB Download: %s => %s\nDB Upload: %s => %s" % (dict_progress[int(snmp_dn_progress.value)],dict_dn_error[int(snmp_dn_error.value)],dict_progress[int(snmp_up_progress.value)],dict_up_error[int(snmp_up_error.value)]))
            print("| backup_status=1;1;2;0;3")
            sys.exit(1)

        else:
            print("ISAM Auto-Backup is CRITICAL\nDB Download: %s => %s\nDB Upload: %s => %s" % (dict_progress[int(snmp_dn_progress.value)],dict_dn_error[int(snmp_dn_error.value)],dict_progress[int(snmp_up_progress.value)],dict_up_error[int(snmp_up_error.value)]))
            print("| backup_status=2;1;2;0;3")
            sys.exit(2)

    else:
        print("UNKNOWN - An SNMP error occured")
        sys.exit(3)


def check_isam_pon_utilization(hostname,community,warning,critical,verbose):
#   checks the utilization of all pon interfaces

    oid_rx = "1.3.6.1.4.1.637.61.1.35.21.57.1.7"
    oid_tx = "1.3.6.1.4.1.637.61.1.35.21.57.1.6"
    snmp_rx = ""
    snmp_tx = ""
    code_warning = 0
    code_critical = 0

    snmp_rx = snmp_walk(oid_rx,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_tx = snmp_walk(oid_tx,hostname=hostname,community=community,version=2,timeout=10,retries=0)

    if snmp_rx and snmp_tx and len(snmp_rx) == len(snmp_tx):
        if verbose:
            print("\nSNMP - rx utilization:")
            for item in snmp_rx: print("%s" % item)
            print("\nSNMP - tx utilization:")
            for item in snmp_tx: print("%s" % item)

#       walk through values, cast them to float, create percentage and list
        snmp_rx = [float(item.value)/100 for item in snmp_rx]
        snmp_tx = [float(item.value)/100 for item in snmp_tx]
        if verbose: print("\nConverted rx values:\n%s\nConverted tx values:\n%s" % (snmp_rx,snmp_tx))

#       walk through boards and set codes
        i = 0
        while(i < len(snmp_rx)):
            if snmp_rx[i] >= critical or snmp_tx[i] >= critical: code_critical += 1
            elif snmp_rx[i] >= warning or snmp_tx[i] >= warning: code_warning += 1
            i += 1

#       print plugin-output
        if code_critical: print("%i/%i PON interfaces are reporting CRITICAL" % (code_critical,len(snmp_rx)))
        elif code_warning: print("%i/%i PON interfaces are reporting WARNING" % (code_warning,len(snmp_rx)))
        else: print("%i/%i PON interfaces are reporting OK" % (len(snmp_rx),len(snmp_rx)))

#       generate performance-data (hardcoded to 16-PON LTs)
        print("|")
        i = 0
        i_lt = 1
        i_pon = 1
        while i < len(snmp_rx):
            print("pon_1/1/%i/%i_rx=%3.2f%%;%i;%i;0;100" % (i_lt,i_pon,snmp_rx[i],warning,critical))
            print("pon_1/1/%i/%i_tx=%3.2f%%;%i;%i;0;100" % (i_lt,i_pon,snmp_tx[i],warning,critical))
            if i_pon == 16:
                i_pon = 0
                i_lt += 1
            i += 1
            i_pon += 1

        if code_critical: sys.exit(2)
        elif code_warning: sys.exit(1)
        else: sys.exit(0)

    else:
        print("UNKNOWN - An SNMP error occured")
        sys.exit(3)


def check_isam_board_temperature(hostname,community,slot_mapping,verbose):
#   checks the temperature sensors on all boards
#   high-temperature thresholds are tca-low (warning) and shut-low (critical) per sensor
#   low-temperature thresholds are hardcoded to 9°C (warning) and 5°C (critical) for all sensors

    oid_actual = "1.3.6.1.4.1.637.61.1.23.10.1.2"
    oid_tca_lo = "1.3.6.1.4.1.637.61.1.23.10.1.3"
    oid_shut_lo = "1.3.6.1.4.1.637.61.1.23.10.1.5"
    snmp_actual_temp = ""
    snmp_tca_lo = ""
    snmp_shut_lo = ""
    cold_warning = 9
    cold_critical = 5
    code_warning = 0
    code_critical = 0

    snmp_actual_temp = snmp_walk(oid_actual,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_tca_lo = snmp_walk(oid_tca_lo,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_shut_lo = snmp_walk(oid_shut_lo,hostname=hostname,community=community,version=2,timeout=10,retries=0)

    if snmp_actual_temp and snmp_tca_lo and snmp_shut_lo:
        if verbose:
            print("\nSNMP - actual temperature:")
            for item in snmp_actual_temp: print("%s" % item)
            print("\nSNMP - tca low:")
            for item in snmp_tca_lo: print("%s" % item)
            print("\nSNMP - shut low:")
            for item in snmp_shut_lo: print("%s" % item)

#       walk through sensors and set codes
        i = 0
        while(i < len(snmp_actual_temp)):
            if int(snmp_actual_temp[i].value) not in range(cold_critical,int(snmp_shut_lo[i].value)):
                code_critical += 1
            elif int(snmp_actual_temp[i].value) not in range(cold_warning,int(snmp_tca_lo[i].value)):
                code_warning += 1
            i += 1

#       print plugin-output
        if code_critical: print("%i/%i temperature sensorsare reporting CRITICAL" % (code_critical,len(snmp_actual_temp)))
        elif code_warning: print("%i/%i temperature sensors are reporting WARNING" % (code_warning,len(snmp_actual_temp)))
        else: print("%i/%i temperature sensors are reporting OK" % (len(snmp_actual_temp),len(snmp_actual_temp)))

#       generate performance-data
#       loop through sensors backwards -> output from plugin should be equal to board-position in chassis
        print(" |")
        i = len(snmp_actual_temp)-1
        while(i >= 0):
            print("%s.%i=%i°C;%i:%i;%i:%i;;" % (slot_mapping[int(snmp_actual_temp[i].oid.rsplit('.',2)[-2])],int(snmp_actual_temp[i].oid.rsplit('.',1)[-1]),int(snmp_actual_temp[i].value),cold_warning,int(snmp_tca_lo[i].value),cold_critical,int(snmp_shut_lo[i].value)))
            i -= 1

        if code_critical: sys.exit(2)
        elif code_warning: sys.exit(1)
        else: sys.exit(0)

    else:
        print("UNKNOWN - An SNMP error occured")
        sys.exit(3)


def check_isam_nt_redundancy(hostname,community,groupId,verbose):
#   checks the redundancy status of NT boards

    oid_admin_state = "1.3.6.1.4.1.637.61.1.23.5.2.1.8." + str(groupId)
    oid_group_row_state = "1.3.6.1.4.1.637.61.1.23.5.2.1.11." + str(groupId)
    oid_standby_state_nta = "1.3.6.1.4.1.637.61.1.23.5.3.1.3.4353"
    oid_standby_state_ntb = "1.3.6.1.4.1.637.61.1.23.5.3.1.3.4354"
    oid_last_switch_reason = "1.3.6.1.4.1.637.61.1.23.5.2.1.5." + str(groupId)
    dict_admin_state = {1:"unlock",2:"lock"}
    dict_group_row_state = {1:"active", 2:"not in service", 3:"not ready", 4:"create and go", 5:"create and wait", 6:"destroy"}
    dict_standby_state = {0:"not-supported",1:"providing-service",2:"hot-standby",3:"cold-standby",4:"idle"}
    dict_last_switch_reason = {1:"no switchover",2:"forced active",3:"board not present",4:"extender chain failure",5:"link failure",6:"watchdog timeout",7:"filesystem corrupt",8:"configuration mismatch",9:"board unplanned",10:"board locked",11:"shelf defense",12:"revertive switchover",13:"lanx failure",14:"lanx hw-failure",15:"lanx sdk failure",16:"dpoe app failure",17:"dpoe unreachable",18:"forced switchover"}

    snmp_admin_state = snmp_get(oid_admin_state,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_group_row_state = snmp_get(oid_group_row_state,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_standby_state_nta = snmp_get(oid_standby_state_nta,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_standby_state_ntb = snmp_get(oid_standby_state_ntb,hostname=hostname,community=community,version=2,timeout=10,retries=0)
    snmp_last_switch_reason = snmp_get(oid_last_switch_reason,hostname=hostname,community=community,version=2,timeout=10,retries=0)

    if snmp_admin_state and snmp_group_row_state and snmp_standby_state_nta and snmp_standby_state_ntb and snmp_last_switch_reason:
        if verbose:
            print("\nSNMP - admin state: %s" % snmp_admin_state)
            print("\nSNMP - group row state: %s" % snmp_group_row_state)
            print("\nSNMP - standby state nt-a: %s" % snmp_standby_state_nta)
            print("\nSNMP - standby state nt-b: %s" % snmp_standby_state_ntb)
            print("\nSNMP - last switchover reason: %s" % snmp_last_switch_reason)

        if int(snmp_group_row_state.value) == 1:
#       protection-group is in-service
            if int(snmp_admin_state.value) == 1 and int(snmp_group_row_state.value) == 1 and int(snmp_standby_state_nta.value) == 1 and int(snmp_standby_state_ntb.value) == 2:
                print("ISAM NT-Redundancy is OK\nProtection Group %i\nAdmin Status: %s\nRow Status: %s\nNT-A Status: %s\nNT-B Status: %s\nLast Switchover Reason: %s" % (groupId,dict_admin_state[int(snmp_admin_state.value)],dict_group_row_state[int(snmp_group_row_state.value)],dict_standby_state[int(snmp_standby_state_nta.value)],dict_standby_state[int(snmp_standby_state_ntb.value)],dict_last_switch_reason[int(snmp_last_switch_reason.value)]))
                print("| redundancy_status=0;1;2;0;3")
                sys.exit(0)

            else:
                print("ISAM NT-Redundancy is CRITICAL\nProtection Group %i\nAdmin Status: %s\nRow Status: %s\nNT-A Status: %s\nNT-B Status: %s\nLast Switchover Reason: %s" % (groupId,dict_admin_state[int(snmp_admin_state.value)],dict_group_row_state[int(snmp_group_row_state.value)],dict_standby_state[int(snmp_standby_state_nta.value)],dict_standby_state[int(snmp_standby_state_ntb.value)],dict_last_switch_reason[int(snmp_last_switch_reason.value)]))
                print("| redundancy_status=2;1;2;0;3")
                sys.exit(2)

        else:
#       protection-group is not in service
            print("ISAM NT-Redundancy is WARNING\nProtection Group %i\nAdmin Status: %s\nRow Status: %s\nNT-A Status: %s\nNT-B Status: %s\nLast Switchover Reason: %s" % (groupId,dict_admin_state[int(snmp_admin_state.value)],dict_group_row_state[int(snmp_group_row_state.value)],dict_standby_state[int(snmp_standby_state_nta.value)],dict_standby_state[int(snmp_standby_state_ntb.value)],dict_last_switch_reason[int(snmp_last_switch_reason.value)]))
            print("| redundancy_status=1;1;2;0;3")
            sys.exit(1)

    else:
        print("UNKNOWN - An SNMP error occured")
        sys.exit(3)


def main():

    slot_mapping = {4352:"acu:1/1",4353:"nt-a",4354:"nt-b",4355:"lt:1/1/1",4356:"lt:1/1/2",4357:"lt:1/1/3",4358:"lt:1/1/4",4359:"lt:1/1/5",4360:"lt:1/1/6",4361:"lt:1/1/7",4362:"lt:1/1/8",4417:"vlt:1/1/63",4418:"vlt:1/1/64"}
    msg_invalid_args = "Please check your arguments!"
    msg_thresholds = "Thresholds are not acceptable!"
    help_message = "\n Collection of Nokia ISAM Monitoring Plugins\n" \
                   "\n Use 'check_isam.py --help' for more information\n"
    usage = "\n %prog --board_availability -s <host> -c <community> -v [verbose]" \
            "\n %prog --board_oper_status  -s <host> -c <community> -v [verbose]" \
            "\n %prog --auto_backup_status -s <host> -c <community> -v [verbose]" \
            "\n %prog --pon_utilization    -s <host> -c <community> -W <warning (1-99)> -C <critical (2-100)> -v [verbose]" \
            "\n %prog --board_temperature  -s <host> -c <community> -v [verbose]" \
            "\n %prog --nt_redundancy      -s <host> -c <community> -g <groupId (1-5)> -v [verbose]" \


#   create parser
    parser = OptionParser(usage=usage,version="%prog 1.3")

#   add options to parser
    parser.add_option("--board_availability",
                      action="store_true",
                      dest="board_availability",
                      help="checks the availability status of all boards")

    parser.add_option("--board_oper_status",
                      action="store_true",
                      dest="board_oper_status",
                      help="checks the operational status of all boards")

    parser.add_option("--auto_backup_status",
                      action="store_true",
                      dest="auto_backup_status",
                      help="checks the status of the auto-backup feature")

    parser.add_option("--pon_utilization",
                      action="store_true",
                      dest="pon_utilization",
                      help="checks the utilization of all PON interfaces")

    parser.add_option("--board_temperature",
                      action="store_true",
                      dest="board_temperature",
                      help="checks the temperature sensors on all boards")

    parser.add_option("--nt_redundancy",
                      action="store_true",
                      dest="nt_redundancy",
                      help="checks the NT redundancy status of the given protection-group")

#   add general parameters
    parser.add_option("-s",
                      dest="hostname",
                      help="specify hostname")

    parser.add_option("-c",
                      dest="community",
                      help="specify SNMPv2 community")

    parser.add_option("-v",
                      action="store_true",
                      dest="verbose",
                      default=False,
                      help="turn on debug output")

    parser.add_option("-W",
                      dest="warning",
                      help="specify a warning threshold")

    parser.add_option("-C",
                      dest="critical",
                      help="specify a critical threshold")

    parser.add_option("-g",
                      dest="groupId",
                      help="specify a protection-group ID (1-5)")

    try:

#      parse options
        (options,args) = parser.parse_args()

        if options.board_availability:
            if options.hostname and options.community:
                hostname = options.hostname
                community = options.community
                verbose = options.verbose
                check_isam_board_availability(hostname,community,slot_mapping,verbose)
            else:
                print("%s" % msg_invalid_args)
                sys.exit(3)

        if options.board_oper_status:
            if options.hostname and options.community:
                hostname = options.hostname
                community = options.community
                verbose = options.verbose
                check_isam_board_operational_status(hostname,community,slot_mapping,verbose)
            else:
                print("%s" % msg_invalid_args)
                sys.exit(3)

        if options.auto_backup_status:
            if options.hostname and options.community:
                hostname = options.hostname
                community = options.community
                verbose = options.verbose
                check_isam_auto_backup_status(hostname,community,verbose)
            else:
                print("%s" % msg_invalid_args)
                sys.exit(3)

        if options.pon_utilization:
            if options.hostname and options.community and options.warning and options.critical:
                hostname = options.hostname
                community = options.community
                verbose = options.verbose
                warning = int(options.warning)
                critical = int(options.critical)
                if 1 <= warning <= 99 and 2 <= critical <= 100 and warning < critical:
                    check_isam_pon_utilization(hostname,community,warning,critical,verbose)
                else:
                    print("%s" % msg_thresholds)
                    sys.exit(3)
            else:
                print("%s" % msg_invalid_args)
                sys.exit(3)

        if options.board_temperature:
            if options.hostname and options.community:
                hostname = options.hostname
                community = options.community
                verbose = options.verbose
                check_isam_board_temperature(hostname,community,slot_mapping,verbose)
            else:
                print("%s" % msg_invalid_args)
                sys.exit(3)

        if options.nt_redundancy:
            if options.hostname and options.community and options.groupId:
                hostname = options.hostname
                community = options.community
                verbose = options.verbose
                groupId = int(options.groupId)
                if 1 <= groupId <= 5:
                    check_isam_nt_redundancy(hostname,community,groupId,verbose)
                else:
                    print("%s" % msg_thresholds)
                    sys.exit(3)
            else:
                print("%s" % msg_invalid_args)
                sys.exit(3)

        else:
            print("%s" % help_message)
            sys.exit(3)

#   catch exceptions
    except Exception as e:
        print("UNKNOWN - An error occured")
        print("%s" % e)
        sys.exit(3)


if __name__ == '__main__':

    main()
