#!/usr/bin/python
# Project Clearwater - IMS in the Cloud
# Copyright (C) 2016 Metaswitch Networks Ltd
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version, along with the "Special Exception" for use of
# the program along with SSL, set forth below. This program is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# The author can be reached by email at clearwater@metaswitch.com or by
# post at Metaswitch Networks Ltd, 100 Church St, Enfield EN2 6BQ, UK
#
# Special Exception
# Metaswitch Networks Ltd  grants you permission to copy, modify,
# propagate, and distribute a work formed by combining OpenSSL with The
# Software, or a work derivative of such a combination, even if such
# copying, modification, propagation, or distribution would otherwise
# violate the terms of the GPL. You must comply with the GPL in all
# respects for all of the code used other than OpenSSL.
# "OpenSSL" means OpenSSL toolkit software distributed by the OpenSSL
# Project and licensed under the OpenSSL Licenses, or a work based on such
# software and licensed under the OpenSSL Licenses.
# "OpenSSL Licenses" means the OpenSSL License and Original SSLeay License
# under which the OpenSSL Project distributes the OpenSSL toolkit software,
# as those licenses appear in the file LICENSE-OPENSSL.

from random import shuffle, random
from subprocess import Popen, check_output
from csv import DictReader, Dialect
from datetime import datetime
import csv
import argparse
from sys import exit
from time import sleep
from tempfile import NamedTemporaryFile
import os
import sys

# Set up a CSV Dialect subclass to handle the semicolon-separated stats files
# SIPp produces
class SIPpstats(csv.excel):
    def __init__(self):
        Dialect.__init__(self)
        self.quoting = csv.QUOTE_MINIMAL
        self.delimiter = ";"

# Constants - directories and load profile

SIPP_BIN = "/usr/share/clearwater/bin/sipp_coreonly"
SCRIPTS_DIR = "/usr/share/clearwater/sip-stress/"

BHCA = 1.3

# Call attempts are split 50/50 between originating calls and terminating
# calls, so divide by 2 to figure out how many calls we need to make. (Calls we
# make will terminate on-net, providing the other 50%).
OUTGOING_BHCA = BHCA/2.0
RE_REG_PER_HOUR = 2.0

# Get command-line arguments

parser = argparse.ArgumentParser(description='Run stress.')
parser.add_argument('domain', help="Deployment's home domain")
parser.add_argument('subscriber_count', help='Number of subscribers to emulate', type=int)
parser.add_argument('duration', help='Number of minutes to run stress for', type=int)
parser.add_argument('--multiplier', help='Multiplier for the VoLTE load profile (e.g. passing 2 here will mean 2.6 calls and 4 re-registers per sub per hour)', type=int, default=1)
parser.add_argument('--initial-reg-rate', help='Rate to send in initial, pre-test-run registrations (default: 80)', type=int, default=80)
parser.add_argument('--icscf-target', help='Domain/IP and port to target registration stress at. (default: sprout.{domain}:5054)')
parser.add_argument('--scscf-target', help='Domain/IP and port to target call stress at. (default: sprout.{domain}:5052)')
parser.add_argument('--call-length', help='Call length in seconds (default: 5)', type=int, default=5)
parser.add_argument('--sipp-output', help='Show SIPp output screen', action='store_const', const=True, default=False)
parser.add_argument('--aka', help='Use AKAv1 authentication, not SIP Digest', action='store_const', const=True, default=False)
parser.add_argument('--ignore-initial-reg-failures', help="Don't exit if some initial REGISTER messages fail", action='store_const', const=True, default=False)
parser.add_argument('--single', help="Make one REGISTER, pause for 2 minutes, then make one call. Ignores subscriber count and duration", action='store_const', const=True, default=False)
parser.add_argument('--base-number', help='First number in the number range for subscribers (default: 2010000000)', type=int, default=2010000000)
parser.add_argument('--with-redirection', help='Causes the callee to respond to the INVITE with a 302 Moved Temporarily message. See callee_redirection.xml for details', action='store_const', const=True, default=False)
parser.add_argument('--with-errors', help='10%% of calls should get error responses', action='store_const', const=True, default=False)
parser.add_argument('--messages', help='Use MESSAGE flows instead of INVITE flows', action='store_const', const=True, default=False)
parser.add_argument('--log-prefix', help='Prefix for log files (default: the process ID)', type=str, default=str(os.getpid()))
parser.add_argument('--target-latency', help='Target average latency.  The script will fail if the mean time from INVITE to 180 Ringing is higher than this.', type=int)
parser.add_argument('--target-call-success-rate', help='Target call success rate.  The script will fail if the actual rate is lower.', type=float, default=100.0)
parser.add_argument('--target-reg-success-rate', help='Target registration success rate.  The script will fail if the actual rate is lower.', type=float, default=100.0)
parser.add_argument('--ccf', help='IP or hostname of the CCF to use.', type=str, default="0.0.0.0")
parser.add_argument('--wildcards', help='Make the call flows involve wildcard IMPUs', action='store_const', const=True, default=False)
parser.add_argument('--ipv6', help="Send traffic to an IPv6 system", action='store_const', const=True, default=False)
parser.add_argument('--listen-port', help='P-CSCF port to include in path headers and listen on', type=str, default="5082")

args = parser.parse_args()

LOG_PREFIX = "/var/log/clearwater-sip-stress/{}_".format(args.log_prefix)

INITIAL_REG_ERRORS = LOG_PREFIX + "initial_reg_errors.log"
RE_REG_ERRORS = LOG_PREFIX + "re_reg_errors.log"
CALLER_ERRORS = LOG_PREFIX + "caller_errors.log"
CALLEE_ERRORS = LOG_PREFIX + "callee_errors.log"
RE_REG_STATS  = LOG_PREFIX + "re_reg_stats.log"
CALLER_STATS  = LOG_PREFIX + "caller_stats.log"


if args.icscf_target is None:
    args.icscf_target = "sprout.{}:5052".format(args.domain)

if args.scscf_target is None:
    args.scscf_target = "sprout.{}:5054".format(args.domain)

# Calculate calls/registers per second based on the input
RPS = RE_REG_PER_HOUR * args.subscriber_count * args.multiplier / 3600
CPS = OUTGOING_BHCA * args.subscriber_count * args.multiplier / 3600

# Given the duration, how many registers/calls do we need to make?
REG_MAX = int(args.duration * 60 * RPS)
CALL_MAX = int(args.duration * 60 * CPS)

# If all we want is a single call, override the settings to allow that.
if args.single:
    REG_MAX = 2
    CALL_MAX = 1
    args.subscriber_count = 2
    RPS = CPS = 1

SUB_START = args.base_number
SUB_END = SUB_START + args.subscriber_count

registers = range(SUB_START, SUB_END)
callers = range(SUB_START, SUB_END, 2)
callees = range(SUB_START + 1, SUB_END, 2)

# Convert the duration into seconds for a SIPp timeout, and add a safety factor
sipp_timeout = "{}s".format((args.duration * 60) + 120)

initial_reg_duration = args.subscriber_count/args.initial_reg_rate
initial_reg_timeout = "{}s".format(initial_reg_duration + 120)

# Randomly shuffle the order of registers and calls to reduce the risk of any cache issues
shuffle(registers)
shuffle(callers)
shuffle(callees)

# Generate the CSV input files - one for REGISTER messages with one user per
# line, one for INVITE flows with a caller/callee pair on each line
register_csv = NamedTemporaryFile(prefix="sipp_register")
invite_csv = NamedTemporaryFile(prefix="sipp_calls")

# For wildcard IMPU testing, we expect wildcarded IMPUs to prefix the
# wildcarded part with a specific character. This makes it easy to mock out
# HSSes and other components which recognise that these are wildcards.
# We assume that:
#   - PREFIX$000 will be a distinct IMPU that can be used for registrations
#   - PREFIX$!.*! is an implicitly-registered wildcard IMPU
WILDCARD_DELIMITER = "$"

register_csv.write("SEQUENTIAL\n")
for s in registers:
    if args.wildcards:
        register_csv.write("{}{}000\n".format(s, WILDCARD_DELIMITER))
    else:
        register_csv.write("{}\n".format(s))
register_csv.flush()

invite_csv.write("SEQUENTIAL\n")
for caller, callee in zip(callers, callees):
    if args.wildcards:
        wildcard_callee = "sip:{}{}!.*!@{}".format(callee, WILDCARD_DELIMITER, args.domain)
        caller = "{}{}45678".format(caller, WILDCARD_DELIMITER)
        callee = "{}{}9877654".format(callee, WILDCARD_DELIMITER)
        req_uri = "sip:{}@{}".format(callee, args.domain)

        # We want some calls to not include a P-Profile-Key
        # header, as that's a valid flow
        if random() > 0.5:
            header = "P-Profile-Key:  {}".format(wildcard_callee)
        else:
            header = "X-Dummy-Header: abcd"

        # Wildcard IMPU matching the caller's wildcard, wildcard IMPU matching
        # the callee's wildcard, and the caller's P-Profile-Key
        invite_csv.write("{};{};{};{}\n".format(caller, callee, header, req_uri))
    else:
        req_uri = "sip:{}@{};user=phone".format(callee, args.domain)
        invite_csv.write("{};{};X-Dummy-Header: abcd;{}\n".format(caller, callee, req_uri))
invite_csv.flush()

null = open("/dev/null", "w+")

ipv6_addr = check_output("ifconfig eth0 | grep inet6 | grep Global | grep -Eo \"[a-f0-9]{4}:[a-f0-9:]+\" | head -n 1", shell=True).strip()

common_args = ["-default_behaviors", "all,-bye",
               # Reconnect up to 2,000 times if we get disconnected (e.g. due
               # to Sprout connection recycling) - this was chosen as an
               # arbitrarily high number which we're unlikely to hit.
               "-max_reconnect", "2000",
               # Keep calls alive when we reconnect, and try and reconnect quickly.
               "-reconnect_close", "false",
               "-reconnect_sleep", "100",
               # If SIPp doesn't have standard input (e.g. when run through
               # Jenkins), it uses 100% CPU unless you pass the -nostdin flag.
               "-nostdin",
               "-recv_timeout", "20s",
               "-watchdog_reset", "1m",
               "-watchdog_minor_maxtriggers", "300",
               # Allow multiple parallel connections
               "-t", "tn",
               "-max_socket", "1000"]

if args.ipv6:
    # To send traffic to an IPv6 system, we need to pass SIPp the system's IPv6
    # address. There's no nice, portable way to do this, so parse ifconfig's
    # output.
    #
    # We could use https://pypi.python.org/pypi/netifaces here, but that would
    # introduce an extra dependency.
    ipv6_addr = check_output("ifconfig eth0 | grep inet6 | grep Global | grep -Eo \"[a-f0-9]{4}:[a-f0-9:]+\" | head -n 1", shell=True).strip()
    common_args += ["-i", ipv6_addr]

common_originating_args = common_args + ["-key", "home_domain", args.domain]

if args.aka:
    initial_reg_xml = "aka_initial_register.xml"
    re_reg_xml = "aka_re_register.xml"
else:
    initial_reg_xml = "digest_register.xml"
    re_reg_xml = "digest_register.xml"

initial_reg_cmd = [SIPP_BIN,
                   "-sf", SCRIPTS_DIR + initial_reg_xml,
                   "-inf", register_csv.name,
                   "-trace_err", "-error_file", INITIAL_REG_ERRORS,
                   "-timeout", initial_reg_timeout,
                   "-key", "pcscf_port", args.listen_port,
                   "-r", str(args.initial_reg_rate),
                   "-m", str(args.subscriber_count)] + common_originating_args + [args.icscf_target]

re_reg_cmd = [SIPP_BIN,
              "-sf", SCRIPTS_DIR + re_reg_xml,
              "-inf", register_csv.name,
              "-trace_err", "-error_file", RE_REG_ERRORS,
              "-trace_stat", "-stf", RE_REG_STATS,
              "-timeout", sipp_timeout,
              "-key", "pcscf_port", args.listen_port,
              "-r", str(RPS),
              "-m", str(REG_MAX)] + common_originating_args + [args.icscf_target]

if args.messages:
    caller_file = "message_sender.xml"
    callee_file = "error_message_receiver.xml" if args.with_errors else "message_receiver.xml"
else:
    caller_file = "caller.xml"
    callee_file = "error_callee.xml" if args.with_errors else "callee.xml"

caller_cmd = [SIPP_BIN,
              "-sf", SCRIPTS_DIR + caller_file,
              "-inf", invite_csv.name,
              "-trace_err", "-error_file", CALLER_ERRORS,
              "-trace_stat", "-stf", CALLER_STATS,
              "-timeout", sipp_timeout,
              "-key", "ccf_ip", args.ccf,
              "-r", str(CPS),
              "-d", str(args.call_length * 1000),
              "-m", str(CALL_MAX)] + common_originating_args + [args.scscf_target]

if args.with_redirection:
    callee_file = "callee_redirection.xml"

callee_cmd = [SIPP_BIN,
              "-sf", SCRIPTS_DIR + callee_file,
              "-trace_err", "-error_file", CALLEE_ERRORS,
              "-timeout", sipp_timeout,
              "-p", args.listen_port,
              "-m", str(CALL_MAX) * 3] + common_args

# Do initial registrations as quickly as possible for test setup - this is an
# unrealistic load profile, so no need for measurements yet.

print "Starting initial registration, will take {} seconds".format(initial_reg_duration)

if args.sipp_output:
    proc = Popen(initial_reg_cmd)
else:
    proc = Popen(initial_reg_cmd, stdout=null, stderr=null)

proc.wait()

if proc.returncode != 0:
    print "Initial registration failed - see {} for details of the errors".format(INITIAL_REG_ERRORS)
    if not args.ignore_initial_reg_failures:
        exit(proc.returncode)
else:
    print "Initial registration succeeded"

# If we want to make a pair of registrations then a single call, pause before
# the call in case the user wants to set anything up.
if args.single:
    print "Pausing for 2 minutes before making call"
    sleep(120)

# The test starts now
print "Starting test"
start_time = datetime.now()

# Redirect output from the re-register script and the callee script to
# /dev/null, but show the output of the caller script to allow the user to
# monitor progress.

# Get a SIPp process to do re-registrations, unless all we're making is a single call.
if not args.single:
    re_reg_proc = Popen(re_reg_cmd, stdout=null, stderr=null)

callee_proc = Popen(callee_cmd, stdout=null, stderr=null)

if args.sipp_output:
    caller_proc = Popen(caller_cmd)
else:
    caller_proc = Popen(caller_cmd, stdout=null, stderr=null)

# Wait for the appropriate number of calls and re-registrations to have been
# attempted (and either failed or completed)
caller_proc.wait()

if not args.single:
    re_reg_proc.wait()

# Kill the callee SIPp process - it might not naturally terminate (for example,
# if not all the attempted calls get through to it, so it never hits its call
# limit), and we know it's not doing anything now that caller_proc has
# completed.
callee_proc.kill()

print "Test complete"
end_time = datetime.now()

rc = 0

with open(CALLER_STATS) as f:
    r = DictReader(f, dialect=SIPpstats())
    # Iterate over the whole file so that `row` is set to the last row
    for row in r:
        pass

    call_success_rate = 100 * float(row['SuccessfulCall(C)']) / float(row['TotalCallCreated'])

    if not args.messages:
        hours, mins, secs, nanoseconds = map(int, row['ResponseTime1(C)'].split(":"))
        rtt = (nanoseconds / 1000.0) + (secs * 1000.0)
        print """
Elapsed time: {}
Start: {}
End: {}

Total calls: {}
Successful calls: {} ({}%)
Failed calls: {} ({}%)
Unfinished calls: {}

Retransmissions: {}

Average time from INVITE to 180 Ringing: {}ms
# of calls with 0-2ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 2-10ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 10-20ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 20-50ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 50-100ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 100-200ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 200-500ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 500-1000ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 1000-2000ms from INVITE to 180 Ringing: {} ({}%)
# of calls with 2000+ms from INVITE to 180 Ringing: {} ({}%)""".format(
        row['ElapsedTime(C)'],
        start_time,
        end_time,
        row['TotalCallCreated'],
        row['SuccessfulCall(C)'],
        call_success_rate,
        row['FailedCall(C)'],
        100* float(row['FailedCall(C)']) / float(row['TotalCallCreated']),
        int(row['TotalCallCreated']) - int(row['SuccessfulCall(C)']) - int(row['FailedCall(C)']),
        row['Retransmissions(C)'],
        rtt,
        row['ResponseTimeRepartition1_<2'],
        100* float(row['ResponseTimeRepartition1_<2']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_<10'],
        100* float(row['ResponseTimeRepartition1_<10']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_<20'],
        100* float(row['ResponseTimeRepartition1_<20']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_<50'],
        100* float(row['ResponseTimeRepartition1_<50']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_<100'],
        100* float(row['ResponseTimeRepartition1_<100']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_<200'],
        100* float(row['ResponseTimeRepartition1_<200']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_<500'],
        100* float(row['ResponseTimeRepartition1_<500']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_<1000'],
        100* float(row['ResponseTimeRepartition1_<1000']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_<2000'],
        100* float(row['ResponseTimeRepartition1_<2000']) / float(row['TotalCallCreated']),
        row['ResponseTimeRepartition1_>=2000'],
        100* float(row['ResponseTimeRepartition1_>=2000']) / float(row['TotalCallCreated']))

        if args.target_latency and rtt > args.target_latency:
            print("Failed: average latency {}ms exceeds target latency "
                  "{}ms!".format(rtt, args.target_latency))
            rc = 2

    else:
        print """
Elapsed time: {}
Start: {}
End: {}

Total MESSAGE flows: {}
Successful MESSAGE flows: {} ({}%)
Failed MESSAGE flows: {} ({}%)
""".format(
        row['ElapsedTime(C)'],
        start_time,
        end_time,
        row['TotalCallCreated'],
        row['SuccessfulCall(C)'],
        call_success_rate,
        row['FailedCall(C)'],
        100* float(row['FailedCall(C)']) / float(row['TotalCallCreated']))
 

    if args.target_call_success_rate > call_success_rate:
        print("Failed: call success rate {}% is lower than target "
              "{}%!".format(call_success_rate, args.target_call_success_rate))
        rc = 1

if not args.single: #  we didn't do re-registrations in this case, so won't have any stats
    with open(RE_REG_STATS) as f:
        r = DictReader(f, dialect=SIPpstats())
        # Iterate over the whole file so that `row` is set to the last row
        for row in r:
            pass

        reg_success_rate = 100 * float(row['SuccessfulCall(C)']) / float(row['TotalCallCreated'])
        hours, mins, secs, nanoseconds = map(int, row['ResponseTime1(C)'].split(":"))
        rtt = (nanoseconds / 1000.0) + (secs * 1000.0)
        print """
Total re-REGISTERs: {}
Successful re-REGISTERs: {} ({}%)
Failed re-REGISTERS: {} ({}%)

REGISTER retransmissions: {}

Average time from REGISTER to 200 OK: {}ms""".format(
        row['TotalCallCreated'],
        row['SuccessfulCall(C)'],
        reg_success_rate,
        row['FailedCall(C)'],
        100* float(row['FailedCall(C)']) / float(row['TotalCallCreated']),
        row['Retransmissions(C)'],
        rtt)

        if args.target_reg_success_rate > reg_success_rate:
            print("Failed: re-registration success rate {}% is lower than target "
                  "{}%!".format(reg_success_rate, args.target_reg_success_rate))
            rc = 3

print "\nLog files at {}*".format(LOG_PREFIX)

sys.exit(rc)
