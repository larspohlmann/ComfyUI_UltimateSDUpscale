# ComfyUI_UltimateSDUpscale

[ComfyUI](https://github.com/comfyanonymous/ComfyUI) nodes for performing the image-to-image diffusion process on large images in tiles. This approach improves the details that is commonly found on upscaled images while reducing hardware requirements and maintaining an image size that the diffusion model is trained on.

> ## ⑂ About this fork
>
> This is a fork of [`ssitu/ComfyUI_UltimateSDUpscale`](https://github.com/ssitu/ComfyUI_UltimateSDUpscale) that adds two features on top of upstream. Everything else is identical and stays in sync with upstream; the additions are off by default, so existing workflows behave exactly as before.
>
> ### 1. Per-tile color & brightness match (`tile_color_match`)
>
> Because each tile is denoised independently, tiles can drift apart in **brightness, contrast, and color** — most visible at high denoise, where the upscale looks patchy or shows tile seams. Upstream only offers a post-stitch fix (or a separate color-match node), which can correct the image's overall cast but **cannot** equalise one tile against another after they're merged.
>
> This fork corrects the drift **at the source, inside the tiling loop**: right before each redrawn tile is composited back, its color distribution is matched to the *same region of the pre-redraw upscaled canvas* (which is globally consistent). The tile's new spatial detail is left untouched — only its color/tone is re-anchored — so tiles can't drift apart in the first place.
>
> Two new widgets are added to all three USDU nodes:
> - **`tile_color_match`** — `off` (default), `mkl`, `reinhard`, `hm`, `mvgd`, `hm-mkl-hm`, `hm-mvgd-hm`. `mkl` matches mean + covariance (brightness, contrast, color cast) and fully removes linear drift; `hm-mkl-hm` additionally matches the tonal histogram for the closest match.
> - **`tile_color_match_strength`** — `0.0`–`1.0` blend between the original tile and the fully matched result.
>
> It operates on decoded pixels, so it is **model-agnostic** (works with SD, SDXL, Flux, ERNIE, etc.). It is backed by the [`color-matcher`](https://github.com/hahnec/color-matcher) library — declared in `requirements.txt` / `pyproject.toml`, so it installs automatically and depends on **no other custom nodes**.
>
> ### 2. Live stitch-progress preview (`USDU_LIVE_PREVIEW`)
>
> Writes the working canvas to `<ComfyUI temp>/usdu_live.png` after each tile is pasted, with the just-finished tile outlined, so the stitch can be watched in real time. Controlled by the `USDU_LIVE_PREVIEW` environment variable: unset/default draws the progress overlay, `plain` saves the raw canvas, `numbered` also keeps `usdu_live_0001.png …` snapshots, and `off` disables it.
>
> **Installing this fork:** clone `https://github.com/larspohlmann/ComfyUI_UltimateSDUpscale` (instead of the upstream URL below), then `pip install -r requirements.txt`.

## Installation


### Using Git
1. Git must be installed on your system. Verify by running `git -v` in a terminal.
2. Enter the following command from the terminal starting in ComfyUI/custom_nodes/
    ```
    git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale
    ```

### ComfyUI Manager
1. [ComfyUI Manager](https://github.com/Comfy-Org/ComfyUI-Manager) must be installed.
2. After launching ComfyUI, open ComfyUI Manager and select the "Custom Nodes Manager" option.
3. Search for "UltimateSDUpscale" and install the node. Select latest for the most up-to-date version.
4. Follow any prompts to restart ComfyUI.

### comfy-cli

1. [comfy-cli](https://github.com/Comfy-Org/comfy-cli) must be installed.
2. Run this command from the terminal: `comfy node install comfyui_ultimatesdupscale`

### Manual Download
1. Download the zip file from https://registry.comfy.org/nodes/comfyui_ultimatesdupscale to select the version you want, or obtain the current nightly version by clicking the green "Code" button on the GitHub repository page and selecting "Download ZIP".
2. Create a new folder in the `ComfyUI/custom_nodes/` directory to hold the extracted files (e.g. `ComfyUI/custom_nodes/ComfyUI_UltimateSDUpscale`).
3. Extract the contents of the zip file into the `ComfyUI/custom_nodes/ComfyUI_UltimateSDUpscale` folder.


## Usage

Nodes can be found in the node menu under `image/upscaling`.

Documentation for the nodes can be found in the [`js/docs/`](js/docs/) folder, or viewed within the application by right-clicking the relevant node and selecting the info icon.

Details about most of the parameters can be found [here](https://github.com/Coyote-A/ultimate-upscale-for-automatic1111/wiki/FAQ#parameters-descriptions).

Example workflows can be found in the [`example_workflows/`](example_workflows/) folder. You can also find them in the ComfyUI application under the Templates menu, scroll down the left sidebar to find the Extensions section, then selecting this repository.

## References
* Ultimate Stable Diffusion Upscale script for the Automatic1111 Web UI: https://github.com/Coyote-A/ultimate-upscale-for-automatic1111
* ComfyUI: https://github.com/comfyanonymous/ComfyUI