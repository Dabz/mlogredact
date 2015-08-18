## [mlogredact](https://github.com/Dabz/mlogredact)
***********
*Tool for redacting mongodb log file*

Scripts removing potential sensitive information from a MongoDB log file without affecting the shape or the length of the data.
Currently obfuscating the JSON Data and the IP adresses.

#### Usage
````python
python mlogredact.py -f [mongod_log_file] [-d]
````

#### Example
mongod.log:

```python
   36 2015-08-17T16:19:59.189+0100 [conn1] insert m.test query: { _id: ObjectId('55d1fb9e4e7119b18bb4fd22'), a: 4810.0 } ninserted:1 keyUpdates:0 numYields:0 locks(micros) w:417684 417ms
   2015-08-17T16:20:27.171+0100 [conn2] end connection 10.02.0.5:59307 (1 connection now open)
````

````python
python mlogredact.py -f mongod.log

2015-08-17T16:19:59.189+0100 [conn1]  insert m.test query: {"_id":"8E1G926ESENKPXUJ89QBVEGZ","a":"SYVTOY"} ninserted:1 keyUpdates:0 numYields:0 locks(micros) w:417684 417ms
2015-08-17T16:20:27.171+0100 [conn2]  end connection 73.162.78.5:59307 (1 connection now open)
````
