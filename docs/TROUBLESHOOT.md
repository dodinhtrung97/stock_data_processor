## Failure In Starting Data Collector Service

### Error

`Error starting service: The service did not respond to the start or control request in a timely fashion`

### Potential Explanations

`.dll` file is missing from python library

Environment variables are configured wrongly due to python attempting to install windows service from user whose environment variables aren't yet set

### Fix

Try running: `python C:\Python27\Scripts\pywin32_postinstall.py -install`

If the issue persists, try below: <br/>

Make sure that `pywintypes{python_version}.dll` (eg: `pywintypes37.dll`) exists in `/Python37/Lib/site-packages/win32`

If this `/win32/` doesn't contain this file, copy this file from:

`Python36\Lib\site-packages\pywin32_system32`

To: `Python36\Lib\site-packages\win32`

Configure `PATH` for `System Environment Variables` to include paths to Python's installation directiory:


```
C:\Users\DRD1HC\AppData\Local\Programs\Python\Python37-32\
C:\Users\DRD1HC\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\win32
C:\Users\DRD1HC\AppData\Local\Programs\Python\Python37-32\Lib\site-packages\pywin32_system32
C:\Users\DRD1HC\AppData\Local\Programs\Python\Python37-32\Lib\site-packages
```

Change directory prefixes relative to your working computer