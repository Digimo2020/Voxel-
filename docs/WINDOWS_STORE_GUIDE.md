# Making Voxel installable on any Windows PC

## Why Windows blocks Voxel today

`Voxel.exe` is **unsigned**. Windows 11 *Smart App Control* (and SmartScreen) only run programs that are signed by a publisher Microsoft recognizes. A brand-new unsigned exe is blocked, and Smart App Control has no "allow this one app" button.

The fix is **code signing**. There are two real routes. Do both over time.

| | A. Sign the `.exe` (GitHub download) | B. Microsoft Store |
| :--- | :--- | :--- |
| Who can install | Anyone who downloads from GitHub | Anyone, from the Store app |
| Who signs | You (certificate) | Microsoft signs it for you |
| Smart App Control | Allowed once signed (reputation may take weeks) | Allowed, Store apps are trusted |
| Cost (checked Nov 2026) | SignPath Foundation: free for open source. Azure Artifact Signing: paid, US/Canada individuals only. Normal OV certificate: paid | Individual developer registration is free in the new flow; older pages still show about $19, so check Partner Center |
| Effort | Low: one extra CI step | Medium: packaging, listing, certification review |

## Right now (test phase)

Don't turn Smart App Control off: Windows doesn't let you turn it back on without resetting the PC.
Run Voxel from source instead, which is not blocked:

1. Install Python 3.11+ (python.org).
2. In the Voxel folder: `pip install -r requirements.txt`
3. Double-click `run.bat`.

## Route A: signed `.exe` (do this first)

**Recommended: SignPath Foundation** (free for open-source projects). Voxel qualifies: MIT license, public repo, automated GitHub Actions build.

Already prepared in this repo: [`CODE_SIGNING_POLICY.md`](../CODE_SIGNING_POLICY.md), [`.signpath/artifact-configuration.xml`](../.signpath/artifact-configuration.xml), and a signing step in `.github/workflows/build.yml` that stays **off** until you set the variable below.

**Your steps**
1. Turn on multi-factor authentication for your GitHub account.
2. Apply at <https://signpath.org/apply>. Use repo `https://github.com/Digimo2020/Voxel-V01` and link `CODE_SIGNING_POLICY.md`. (SignPath may ask for a previous release, which exists: v1.1.23.)
3. After approval, in SignPath create/confirm: a **project** (slug e.g. `voxel`), an **artifact configuration** (paste `.signpath/artifact-configuration.xml`), and a **signing policy** (e.g. `release-signing`). Create an **API token** (CI user) and connect the GitHub trusted build system.
4. In GitHub: *Settings → Secrets and variables → Actions*:
   - **Secret** `SIGNPATH_API_TOKEN` = the API token
   - **Variables** `SIGNPATH_ORGANIZATION_ID`, `SIGNPATH_PROJECT_SLUG`, `SIGNPATH_SIGNING_POLICY_SLUG`
5. Add to the README: *"Free code signing provided by SignPath.io, certificate by SignPath Foundation."* (Only after approval.)
6. Release a new version tag. The Windows job now uploads the exe, SignPath signs it (you approve the request in SignPath), and the workflow fails the release if the result has no valid signature.

Publisher name will show as "SignPath Foundation". That is normal for this route.

Alternatives: **Azure Artifact Signing** (formerly Trusted Signing), individuals in the US/Canada only, or a paid **OV code-signing certificate** from a certificate authority.

Note: even signed, a *new* app can show a SmartScreen "unrecognized app" warning until it has enough downloads. Smart App Control is stricter on unsigned apps than on signed ones.

## Route B: Microsoft Store

### 1. Account
1. Go to <https://partner.microsoft.com/dashboard> and register as an **individual** developer (government ID + selfie verification). Check the fee shown on screen.
2. Reserve the app name **Voxel** in Partner Center. If it is taken, use "Voxel Text to Speech".

### 2. Prepare the app
- **Privacy policy**: required. Use `docs/PRIVACY.md` and publish it at a public URL (GitHub Pages or digimo.pt).
- **Package**: build with PyInstaller `--onedir` (not `--onefile`), then wrap it as **MSIX** (MSIX Packaging Tool or `makeappx`). Microsoft signs the MSIX for you at ingestion. (A plain `.exe`/`.msi` installer can also be submitted, but it must be signed with a trusted certificate: Route A.)
- **Assets**: Store logo 300×300, tile icons (44, 150, 310), 1-3 screenshots, short and long description. Existing branding in `assets/` covers most of this.
- **Test**: run the *Windows App Certification Kit* on the MSIX and fix anything it reports.
- **Disclosure**: Voxel listens to global mouse/keyboard events to detect text selection. Say this plainly in the listing and privacy policy; reviewers look for it.

### 3. Submit
1. Partner Center → *Apps and games → New product → MSIX or PWA app*.
2. Fill in: pricing (free), age rating questionnaire, category (Productivity / Accessibility), description, screenshots, privacy policy URL.
3. Upload the MSIX, submit for certification. Review usually takes 1-3 business days.
4. When approved, users install from the Microsoft Store with one click. No warnings.

### Updates
Each new version: bump `version.py`, rebuild, upload the new MSIX as a Store submission.

## Suggested order
1. Apply to SignPath (free, a few days) and meanwhile test with `run.bat`.
2. Add signing to the release workflow, so GitHub downloads work on any PC.
3. Package MSIX and submit to the Store.

I can do the code side (workflow signing step, MSIX build script, listing text, privacy page) once you have the account credentials. Steps that need your identity (applying, ID verification, payment, secrets) must be done by you.
