'''
test_ctrl_c.py

Copyright 2012 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
import signal
import subprocess
import time
import unittest

from nose.plugins.attrib import attr

from w3af import ROOT_PATH


@attr('moth')
class TestHandleCtrlC(unittest.TestCase):
    
    def test_scan_ctrl_c(self):
        
        script = '%s/core/ui/console/tests/data/spider_long.w3af' % ROOT_PATH
        cmd = ['python', 'w3af_console', '-s', script]

        process = subprocess.Popen(args=cmd,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=False,
                                   universal_newlines=True)
        
        # Let it run until the first new URL is found
        while True:
            w3af_output = process.stdout.readline()
            if 'New URL found by web_spider plugin' in w3af_output:
                time.sleep(1)
                break
            
        # Send Ctrl+C
        process.send_signal(signal.SIGINT)

        EXPECTED = (
                    'User pressed Ctrl+C, stopping scan',
                    'The user stopped the scan.',
                    'w3af>>> exit',
                    )

        # Wait for the process to finish
        process.poll()

        # set signal handler
        signal.signal(signal.SIGALRM, alarm_handler)
        # produce SIGALRM in X seconds
        signal.alarm(30)

        # In some cases process.stdout.read() simply hang for ever, so I want
        # to wait for 30 seconds (see signal.alarm) and then terminate the
        # process
        try:
            w3af_output = process.stdout.read()
            # cancel alarm
            signal.alarm(0)
        except Alarm:
            process.terminate()
            msg = 'w3af did not stop on Ctrl+C, read() timeout.'
            self.assertTrue(False, msg)
        
        for estr in EXPECTED:
            self.assertIn(estr, w3af_output)
            

        NOT_EXPECTED = ('The list of fuzzable requests is:',)

        for estr in NOT_EXPECTED:
            self.assertNotIn(estr, w3af_output)

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm