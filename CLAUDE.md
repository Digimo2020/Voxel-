# Voxel: working rules

## Always
- Follow `VERSIONING_RULES.md` for every release (version file, CHANGELOG, README links, tag).
- Every download must carry its version (e.g. `Voxel-v1.1.23.exe`); never publish unversioned `Voxel.exe`/`Voxel.dmg`. After each release run `python scripts/update_download_links.py`, then check each link returns HTTP 200.
- Keep the README short and visual; put long detail in `docs/DETAILS.md`.

## End of every reply / session: always finish with this block
Keep it short and simple (the owner wants it easy to follow, no jargon):
1. **Summary**: what was done, what failed or is unverified, what is next.
2. **Version**: the current version number (e.g. `v1.1.23`) and what changed.
3. **GitHub links**: repository, latest release, and any file/page that changed.
4. **Download link**: versioned file(s), e.g. `Voxel-v1.1.23.exe` / `.dmg`, plus the versioned source zip. Say if Windows may block the exe (unsigned) and what to do instead (`run.bat`).
5. Tell them if their PC copy was updated and how to start it.
