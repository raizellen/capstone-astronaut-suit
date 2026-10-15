## sensor link: test server for the AdaptiveHUD telemetry endpoint

stand-in for the adaptive HUD backend's telemetry endpoint, use it to test a sensor against the same request the real backend accepts, without installing anything. you only need python. it accepts the same request as the real backend, so if your sensor works here it'll work against the real thing.

run:
`py backend.py`

it should print every reading it receives, and warns about anything unusual (wrong type, unknown field, value outside the expected range)

for actual connection, send readings to:
  `POST http://<backend-machine-ip>:8080/telemetry`


## request

send a http post with a json body:

```
POST http://<machine-ip>:8080/telemetry
Content-Type: application/json

{ "bpm": 75, "spo2": 98, "battery": 90, "temperature": 22.5 }
```

| Field        | Unit  | Expected range |
|--------------|-------|----------------|
| `bpm`        | bpm   | 20 to 250      |
| `spo2`       | %     | 50 to 100      |
| `battery`    | %     | 0 to 100       |
| `temperature`| deg C | -100 to 100    |

- values must be json numbers, not strings
- you can send only some fields, e.g. `{"bpm": 75, "spo2": 98}`, the rest keep their last value
- if your sensor uses other units or raw values, convert them before sending
- about one reading per second would be good

the server replies with `{"ok": true, "telemetry": {...}, "warnings": [...]}`.
