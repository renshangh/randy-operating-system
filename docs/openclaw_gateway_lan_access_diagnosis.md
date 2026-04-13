# OpenClaw Gateway LAN Access Diagnosis

Related issue: `renshangh/randy-operating-system#192`

## Problem
On the MacBook, the normal OpenClaw exec/runtime path could not reach LAN hosts such as the Mac Mini (`192.168.1.4`), even though the user's interactive shell on the same machine could.

## Confirmed observations
### From the user's interactive shell on the MacBook
These worked:
- `ssh danielshan@192.168.1.4 'hostname; pwd'`
- `nc -vz 192.168.1.4 22`
- normal LAN route table showed `192.168.1.4` reachable on `en0`

### From OpenClaw exec/runtime
These failed:
- `ssh danielshan@192.168.1.4` → `No route to host`
- direct socket tests to `192.168.1.4:22` and `192.168.1.248:8000` failed

### Key experiment
When the LaunchAgent-backed gateway was stopped and the gateway was started in the foreground from the user's shell context, OpenClaw exec regained Mac Mini access immediately.

This strongly suggests the problem is not:
- bad SSH config
- bad Mac Mini IP
- broken MacBook LAN routing

It points instead to a **runtime/network-context difference** between the normal LaunchAgent-backed gateway and the shell-started gateway.

## Current hypothesis
The fault domain is likely one of:
- macOS background-process local network permission behavior
- LaunchAgent runtime/network context differences
- OpenClaw/Node network access behaving differently under launchd than under an interactive shell

## Why this matters
This breaks normal cross-machine orchestration from the default OpenClaw runtime, including:
- pulling files from the Mac Mini
- same-machine relay/verification workflows
- SSH-based ops tasks

## Controlled states to compare
1. **LaunchAgent-backed gateway** — known broken for LAN reachability
2. **Foreground shell-started gateway** — known working
3. **Background but shell-started gateway** — still needs explicit test

The third state is important because it would tell us whether the root cause is:
- specifically the LaunchAgent context
- or merely foreground vs background execution

## Likely fix directions
### Option A — replace/adjust LaunchAgent strategy
Use a shell-wrapper startup path that preserves the working network context.

### Option B — keep LaunchAgent but change how it is invoked
Potentially launch through an explicit shell wrapper instead of direct Node invocation.

### Option C — accept LaunchAgent limitation and use a different canonical startup mode
Document that the current LaunchAgent-backed gateway is not reliable for LAN access on this macOS setup and choose a different operational model.

## Next recommended test
Start the gateway from the user shell in the background (not LaunchAgent), then check whether OpenClaw exec still retains Mac Mini access. If yes, LaunchAgent itself is the likely culprit.
