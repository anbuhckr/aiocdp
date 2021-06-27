#! /usr/bin/env python3

import errno
import os
import platform
import asyncio
import socket
from tempfile import TemporaryDirectory

DEFAULT_ARGS = [
    'about:blank',
    '--disable-background-networking',
    '--disable-background-timer-throttling',
    '--disable-breakpad',
    '--disable-browser-side-navigation',
    '--disable-client-side-phishing-detection',
    '--disable-default-apps',
    '--disable-infobars',
    '--disable-dev-shm-usage',
    '--disable-extensions',
    '--disable-features=site-per-process',
    '--disable-hang-monitor',
    '--disable-popup-blocking',
    '--disable-prompt-on-repost',
    '--disable-sync',
    '--disable-translate',
    '--metrics-recording-only',
    '--no-first-run',
    '--safebrowsing-disable-auto-update',    
    '--password-store=basic',
    '--use-mock-keychain',
    '--ignore-ssl-errors',
    '--ignore-certificate-errors',
]

class Service(object):
    def __init__(self, opts=[]):
        self.tmpdir = TemporaryDirectory()
        self.path = None                    
        self.port = None
        self.service_args = DEFAULT_ARGS
        self.service_args += opts      
        self.service_args += [f'--user-data-dir={self.tmpdir.name}']        
        self.env = os.environ
        self.url = None
        self.start_error_message = ""
        self.process = None
        if 'nt' in os.name:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        self.loop = asyncio.get_event_loop()
        
    def find(self):        
        name = 'chrome.exe'
        for root, dirs, files in os.walk('C:/'):
            if name in files:
                return os.path.join(root, name).replace('\\', '/')

    def free_port(self):
        free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        free_socket.bind(('0.0.0.0', 0))
        free_socket.listen(5)
        port = free_socket.getsockname()[1]
        free_socket.close()
        return port

    async def start(self):
        self.path = 'google-chrome'
        if 'nt' in os.name:
            self.path = await self.loop.run_in_executor(None, self.find)
        self.port = await self.loop.run_in_executor(None, self.free_port)
        self.service_args += [f'--remote-debugging-port={self.port}']
        self.url = f"http://localhost:{self.port}"
        try:
            cmd = [self.path]
            cmd.extend(self.service_args)
            self.process = await asyncio.create_subprocess_exec(*cmd, env=self.env, close_fds=platform.system() != 'Windows', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE)
        except TypeError:
            raise
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise ChromeException(f"'{os.path.basename(self.path)}' executable needs to be in PATH. {self.start_error_message}")
            elif err.errno == errno.EACCES:
                raise ChromeException(f"'{os.path.basename(self.path)}' executable may have wrong permissions. {self.start_error_message}")
            else:
                raise
        except Exception as e:
            raise ChromeException(f"The executable {os.path.basename(self.path)} needs to be available in the path. {self.start_error_message}\n{e}")
        count = 0
        while True:
            await self.assert_process_still_running()
            if await self.is_connectable():
                break
            count += 1
            await asyncio.sleep(1)
            if count == 30:
                raise ChromeException("Can not connect to the Service %s" % self.path)

    async def assert_process_still_running(self):        
        if self.process.returncode is not None:
            outs, errs = await self.process.communicate()
            print("\nChrome STDOUT:\n" + outs.encode() + "\n\n")
            print("\nChrome STDERR:\n" + errs.encode() + "\n\n")
            raise ChromeException(f'Service {self.path} unexpectedly exited. Status code was: {self.process.returncode}')

    async def is_connectable(self):
        socket_ = None        
        try:            
            reader, socket_ = await asyncio.open_connection('localhost', self.port)
            result = True
        except Exception as e:            
            result = False
        finally:
            if socket_:
                socket_.close()
        return result

    async def stop(self):        
        if self.process is None:
            return
        try:
            if self.process:                
                self.process.terminate()
                await self.process.wait()
                self.process.kill()
                self.process = None
                await asyncio.sleep(0.5)                
                try:
                    await self.loop.run_in_executor(None, self.tmpdir.cleanup)                   
                except Exception:
                    pass
        except OSError:
            pass

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.stop()

class ChromeException(Exception):
    def __init__(self, msg=None, screen=None, stacktrace=None):
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        exception_msg = f"Message: {self.msg}\n" 
        if self.screen is not None:
            exception_msg += "Screenshot: available via screen\n"
        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += f"Stacktrace:\n{stacktrace}"
        return exception_msg
