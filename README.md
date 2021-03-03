# aiocdp

[![GitHub issues](https://img.shields.io/github/issues/anbuhckr/aiocdp)](https://github.com/anbuhckr/aiocdp/issues)
[![GitHub forks](https://img.shields.io/github/forks/anbuhckr/aiocdp)](https://github.com/anbuhckr/aiocdp/network)
[![GitHub stars](https://img.shields.io/github/stars/anbuhckr/aiocdp)](https://github.com/anbuhckr/aiocdp/stargazers)
[![GitHub license](https://img.shields.io/github/license/anbuhckr/aiocdp)](https://github.com/anbuhckr/aiocdp/blob/main/LICENSE)
![PyPI - Python Version](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue)

Asynchronous Chrome DevTools Protocol Package for access lower level methods in Chrome.

## Table of Contents

* [Installation](#installation)
* [Getting Started](#getting-started)
* [Ref](#ref)


## Installation

To install aiochrome, simply:

```
$ pip install -U git+https://github.com/anbuhckr/aiocdp.git
```

or from source:

```
$ python setup.py install
```

## Getting Started

``` python
#! /usr/bin/env python3

import asyncio
from aiocdp import Browser

async def request_will_be_sent(**kwargs):
    print(f"loading: {kwargs.get('request').get('url')}")

async def main():
    # chrome options
    options = [
        "--disable-gpu",
        "--no-sandbox",
        "--disable-setuid-sandbox",
    ]
    
    # create browser instance with custom options
    browser = Browser(opts=options)

    # register callback if you want
    browser.on('Network.requestWillBeSent', request_will_be_sent)
    
    # start browser with custom method
    try:
        await browser.start() 
        await browser.send('Network.enable')
        await browser.send('Page.enable')
        await browser.send('Page.navigate', url="https://github.com/anbuhckr/aiocdp")
        
        # wait for loading
        await asyncio.sleep(10)
        
    # handle exception
    except Exception as e:
        print(e)
        pass
        
    # close browser
    await browser.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()        
```

more methods or events could be found in
[Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)


## Ref

* [aiochrome](https://github.com/fate0/aiochrome/)
* [pyppeteer](https://github.com/pyppeteer/pyppeteer/)
* [selenium](https://github.com/SeleniumHQ/selenium/tree/trunk/py/)
* [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
