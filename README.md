## Launch
Start the python environment

`source env/bin/activate`

Add your optimal schedule to the appData.json using format:

```JSON
"tuesday": {
    "start": "3:30pm",
    "numSeats": 4
}
```

Run the automated scheduler

`python roomScheduler.py`