# MyDalamudPlugins

Custom Dalamud plugin repository for saewoo's plugins.

## Installation
1. Open Dalamud settings by typing `/xlsettings` in game chat.
2. Go to "Experimental" tab.
3. Find "Custom Plugin Repositories" section and paste:
   `https://raw.githubusercontent.com/saewoo-dalamud/MyDalamudPlugins/main/pluginmaster.json`
4. Click "Save".

## Plugins
- [saewoo's HuntTrainAssistant](https://github.com/saewoo-dalamud/HuntTrainAssistant) — personal fork of [NightmareXIV/HuntTrainAssistant](https://github.com/NightmareXIV/HuntTrainAssistant)

## Adding a plugin
1. Add an entry to `plugins.json` pointing at the plugin repo's manifest and icon path.
2. In the plugin repo, add a workflow that sends a `repository_dispatch` (type `plugin-released`) to this repo on `release: published`, using a PAT with permission to trigger workflows here.
3. `pluginmaster.json` will regenerate automatically from each plugin's manifest and latest GitHub release. You can also trigger it manually from the Actions tab.
