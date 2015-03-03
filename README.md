libbiopacndt_py
===============

What is this?
-------------
This is a Python client for the libbiopacndt library put together by [godbyk](https://github.com/godbyk).

Requirements
------------
Python 2.7.

Usage
-----
Consult ``app.py`` for an example application. Generally, create the ``Client`` with the names of the channels you want and the server information, then use ``connect`` to begin collecting data:

```python
client = Client(["A1"], server='localhost', port=9999)
client.connect()
```

It's important to call ``disconnect`` in order to merge the threads and close sockets down. I guess you don't *have* to do it, but it's good practice.

The client will create `biopacndt_py.log` in the current directory.

* `connect` -- Connects the client, creating the socket threads. If `ignore_missing_channels` is `True` (default), any channel names that can't be found in the manifest will be ignored and added to the log file. Otherwise, throws a `ChannelNotFound` exception.

* `disconnect` -- Merges threads and closes the sockets.

* `poll` -- A generator that allows access to the buffer. Calling `poll` will ask all the socket threads to give up their data and clear their buffers. If you just want all the data in the buffer, use:

```python
for data in client.poll():
	print data
```

If you want a specific number of items:

```python
for i in range(10):
	print client.poll().next()
```

Examples for a continuous stream of data can be found in ``app.py``.

Changes
-------
### v1.0

* Initial version.

License
-------
**Author**: Andrew Lilja

The MIT License

Copyright (c) 2010-2015 Google, Inc. http://angularjs.org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
