# Pharma 3D Studio

Free, forever, headless 3D animation pipeline for pharma technical education videos —
reactor operations/cleaning, QC instruments (HPLC, GC, HRMS, LC-MS), equipment maintenance,
and industrial safety.

## Stack
- **Blender (headless, via `bpy`)** — procedural 3D scene building and rendering. No GUI, no license cost.
- **GitHub Actions** — free CPU compute to run renders (~2,000 min/month free tier).
- **cron-job.org / Telegram bot** — triggers renders remotely (same pattern as other automation repos).
- **Streamlit** — output gallery to browse/download rendered videos.

## Structure
```
components/        Reusable Blender building blocks (vessel, materials, lighting, camera)
configs/            One folder per category; each script = one video part
  reactor_cleaning/
  hplc/
  gc/
  hrms/
  lcms/
  safety/
.github/workflows/  render.yml — workflow_dispatch triggered render job
output/             Rendered .mp4 files land here
```

## How it scales
New equipment/category = new config script that imports from `components/` — no new
infrastructure needed. Shared materials (steel, glass, liquid), lighting rig, and camera
helpers keep every video visually consistent.

## Rendering a scene locally
```bash
blender -b -P configs/reactor_cleaning/part3_boil_agitate.py
```

## Rendering via GitHub Actions
Trigger the `Render Scene` workflow manually (Actions tab -> Run workflow), passing the
scene script path as input. Rendered file is committed to `output/`.

## Status
- [x] Repo scaffolded
- [x] Vessel/agitator/liquid component library
- [x] Part 3 (water rise + agitator rotation) - first proof-of-concept scene
- [ ] Remaining reactor cleaning parts (1, 2, 4-8)
- [ ] HDRI lighting swap-in
- [ ] HPLC/GC/HRMS/LC-MS component library
- [ ] Telegram bot trigger
- [ ] Streamlit output gallery
