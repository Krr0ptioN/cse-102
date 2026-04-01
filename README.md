# `CSE-102` Teacher-Student Project Assignment Manager

A Tkinter desktop app for managing student project roadmaps, approvals, and progress tracking.

All application code and tooling now live in the `app/` directory (project root for code). 
Docs and assets stay at the repository root.

## Getting Started

See `app/README.md` for setup, run, and test instructions (uv + Makefile flow). If you have
*make* installed, use `make -C app <target>` from the repo root if you prefer not to `cd`.

Otherwise you can follow the process defined within the application's [documentation](/app/README.md).

## Disclaimer

In this project, a lot of code-separation has been done, you'll see certain patterns similar to
**React.js** component driven development, since the Tkinter as a very surface level and non-industry standard,
we decided to re-write certain required utilities for proper composable component system which is really 
required for a complex application.

For more technical design decision that has been made you can refer to our [specification documentation](/docs/specifications/README.md).
