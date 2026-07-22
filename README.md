# Xin He · Architecture + Art

An optimized, independent successor to the original `xin1012-HX/my-website` portfolio. The original repository is not modified and this project intentionally has no custom-domain `CNAME` file.

## What changed

- work-first homepage with three featured projects and a complete drawing register
- centralized project and artwork content
- shared responsive CSS and accessible JavaScript
- mobile navigation without horizontal overflow
- keyboard-accessible image viewer and reduced-motion support
- descriptive alt text, explicit image dimensions, canonical metadata, sitemap, and social preview
- public contact details reduced to one professional email and city-level locations
- optimized WebP production assets

The optimized repository is roughly one fifth of the original working-tree size while retaining all eight architecture projects and all fifteen artworks.

## Project structure

```text
assets/css/site.css          Shared visual system
assets/js/site.js            Navigation, reveal, and image-viewer behavior
assets/images/               Optimized production images
assets/media/                CV and project video
content/projects.json        Architecture project content
content/artworks.json        Art catalogue content
tools/build.py               Static page generator
tools/optimize_images.py     Image optimization utility
```

Generated HTML files are committed so GitHub Pages can serve the repository directly without a build service.

## Edit and rebuild

Edit `content/projects.json` or `content/artworks.json`, then run:

```powershell
python tools/build.py
```

To regenerate images from a checkout of the original portfolio:

```powershell
python tools/optimize_images.py C:\path\to\original\my-website
python tools/build.py
```

Preview locally:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000`.

## GitHub Pages

In the new repository, open **Settings → Pages**, choose **Deploy from a branch**, select `main` and `/ (root)`, then save. Do not add the original custom domain until its DNS ownership and certificate configuration have been repaired and verified.

## Rights

Portfolio text, drawings, images, artwork, and video are © Xin He. All rights reserved.
