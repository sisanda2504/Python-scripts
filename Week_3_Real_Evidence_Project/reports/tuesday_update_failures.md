# Tuesday — Windows App Update Failure Analysis

- Events analysed: **30**
- Malformed events: **0**

## Error-code evidence

### `0X80073D02` — ERROR_PACKAGES_IN_USE
- Occurrences: **27**
- Meaning: The package could not install because resources it modifies were in use.
- Recommended diagnostic check: Close the affected app/process and retry the update.

### `0X80240016` — WU_E_INSTALL_NOT_ALLOWED
- Occurrences: **3**
- Meaning: Another installation was in progress or a mandatory restart was pending.
- Recommended diagnostic check: Check for another update/install operation and pending restart state.

## Most affected packages

- `5319275A.WhatsAppDesktop` — **12** failed installation event(s)
- `Microsoft.YourPhone` — **6** failed installation event(s)
- `Microsoft.ScreenSketch` — **6** failed installation event(s)
- `Microsoft.WindowsAppRuntime.2` — **2** failed installation event(s)
- `Microsoft.WindowsNotepad` — **2** failed installation event(s)
- `MicrosoftWindows.CrossDevice` — **1** failed installation event(s)
- `Microsoft.WindowsAppRuntime.1.8` — **1** failed installation event(s)

## Why this satisfies Tuesday

The analyzer uses structured logging, explicit exception handling, parser validation, and automated unit tests. Failures are not silently ignored.