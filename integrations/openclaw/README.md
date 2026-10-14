# OpenClaw integration status

This directory currently defines the **high-level CineFactory contract**, not a claim that an OpenClaw plugin has already been installed.

The intended integration is deliberately thin: OpenClaw may create projects, submit structured creative artifacts, enqueue governed jobs and inspect audit/job state. It must not call ComfyUI or media-generation providers directly, mutate rights/cost policy, install arbitrary plugins/models, or bypass the CineFactory state machine.

The next integration milestone is to expose these high-level operations through the OpenClaw tool mechanism supported by the pinned OpenClaw version chosen for deployment.
