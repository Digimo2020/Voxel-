# Voxel: working rules

## Always
- Follow `VERSIONING_RULES.md` for every release (version file, CHANGELOG, README links, tag).
- Every download must carry its version (e.g. `Voxel-v1.1.23.exe`); never publish unversioned `Voxel.exe`/`Voxel.dmg`. After each release run `python scripts/update_download_links.py`, then check each link returns HTTP 200.
- Keep the README short and visual; put long detail in `docs/DETAILS.md`.

## End of every session: summary
Finish each session with a very short summary in this format:
1. **Technology**: what is being built and with what.
2. **Done**: what changed this session.
3. **Bugs**: found, fixed, still open.
4. **Next**: the one thing to do next.
