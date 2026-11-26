# Code Signing Policy

Voxel is free and open source (MIT). Windows release builds are signed so Windows (SmartScreen / Smart App Control) can verify who published them and that the file was not altered.

> **Status: application pending.** Signing is not active yet. Until it is approved, Windows builds are unsigned and Windows may block them (see [docs/WINDOWS_STORE_GUIDE.md](docs/WINDOWS_STORE_GUIDE.md)).
> When approved, add this line to the README: *"Free code signing provided by [SignPath.io](https://signpath.io), certificate by [SignPath Foundation](https://signpath.org)."*

## What gets signed
- Only the Windows release executable `Voxel-v<version>.exe`, built by the public GitHub Actions workflow [`build.yml`](.github/workflows/build.yml) from this repository's source.
- Nothing is signed from a developer's own computer, and no proprietary or closed-source components are included.

## Roles
| Role | Who |
| :--- | :--- |
| Author / committer | Digimo (GitHub: [Digimo2020](https://github.com/Digimo2020)) |
| Reviewer | Digimo maintainers |
| Approver (signing requests) | Digimo owner(s) |

Release signing is requested only for version tags (`v*`) and must be approved by an approver. All team members use multi-factor authentication on GitHub and SignPath.

## Privacy
Voxel does not collect telemetry. See [docs/PRIVACY.md](docs/PRIVACY.md) for how text is handled when it is read aloud.

## Reporting a problem
If you believe a signed Voxel file is malicious or was tampered with, report it at <https://github.com/Digimo2020/Voxel-V01/security> (see [SECURITY.md](SECURITY.md)).
