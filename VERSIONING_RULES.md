# Voxel Global Versioning & Deployment Rules

> **Mandatory Rule**: Every new build and deployment must create a dedicated versioned binary and preserve all historical releases. Never overwrite or delete old versions.

---

## 1. Strict Version Rollover Rule
* Version format: `v<Major>.<Minor>.<Patch:02d>` (e.g. `v1.0.06`, `v1.0.07`, `v1.0.08`).
* Every 10th patch cycle increments the minor version:
  - `v1.0.01` ➔ `v1.0.02` ➔ ... ➔ `v1.0.09` ➔ `v1.1.00`
* Every 10th minor cycle increments the major version:
  - `v1.9.09` ➔ `v2.0.00`

---

## 2. Preservation of Previous Versions
* **Never delete or overwrite previous releases**.
* When deploying and building an executable:
  1. The new version must be output with its exact version tag:
     - `dist/Voxel-v1.0.06.exe` (kept intact)
     - `dist/Voxel-v1.0.07.exe` (kept intact)
     - `dist/Voxel-v1.0.08.exe` (kept intact)
     - `dist/Voxel-v1.0.09.exe` (kept intact)
     - `dist/Voxel-v1.1.00.exe` (kept intact)
     - `dist/Voxel-v1.1.01.exe` (kept intact)
     - `dist/Voxel-v1.1.02.exe` (new build)
  2. Maintain a `dist/Voxel.exe` alias pointing to the latest version for convenience.
  3. On macOS, maintain the same version preservation:
     - `dist/Voxel-v1.1.00.pkg`
     - `dist/Voxel-v1.1.00.dmg`

---

## 3. GitHub Deployment & Documentation Standards
* Whenever a new version is created:
  1. **`src/utils/version.py`**: Update `CURRENT_VERSION = "v<Major>.<Minor>.<Patch:02d>"`.
  2. **`CHANGELOG.md`**: Add the new version header with date, fixes, and feature highlights.
  3. **`README.md`**:
     - Update the top version badge.
     - Update direct download links in the Quick Download section.
     - Add a new row to the **Releases & Version Archive** table marked 🟢 **Latest**, and mark the previous release as 📦 **Archived**.
  4. **Git Repository**: Commit all changes with the version tag and push to GitHub (`main` branch).
