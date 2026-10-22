# Vietnam Field Guides

A static site with the trip itinerary and the Hanoi and Da Nang guides. Pick a tab in the left sidebar; on phones the sidebar becomes a tab bar at the bottom of the screen. The site works offline once you tap **Save for offline**.

## Layout

```
index.html              sidebar + guide switcher (the GUIDES list at the bottom sets the tabs)
sw.js                   service worker for offline use
manifest.webmanifest    lets phones add the site to the home screen as an app
guides/itinerary/       day-by-day plan (all its data is in the DAYS list in that file)
guides/hanoi/           Hanoi guide page + photos/
guides/danang/          Da Nang guide page + photos/
tools/import_guide.py   turns an exported guide page into guides/<slug>/
```

Each guide is the original page with two changes: its photos are stored as separate `.webp` files instead of being embedded, and its link to the other guide switches tabs instead of opening claude.ai. The Da Nang guide also has one fact fix: the Dragon Bridge show now runs Friday to Sunday. Re-apply it if you re-import that guide. That cuts each page from 7–11 MB to about 130 KB. Photos load as you scroll.

## Hosting on GitHub Pages

1. On GitHub, open the repository and go to **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Choose the branch that holds these files and the **/ (root)** folder, then click **Save**.
4. Wait a minute or two. The site appears at `https://jonesruskin.github.io/Vietnam/`, and the Pages settings screen shows the link.

GitHub Pages needs a public repository, unless you're on a paid GitHub plan. No build step is needed. The `.nojekyll` file tells Pages to serve the files exactly as they are.

## The itinerary

- **Now and Next:** during the trip, the card at the top shows what's happening now and what's next, in the right time zone for each person. Add `?now=2026-10-31T15:00:00%2B07:00` to the itinerary page's URL to preview any moment.
- **Bala & Antony / Jones:** the buttons show one person's plan. The days you split up show side by side.
- **Add to my calendar:** downloads an `.ics` file with every item at the correct local time, with a reminder 45 minutes before flights and pickups.
- **Links into the guides:** `#hanoi/food` opens the Hanoi tab at its food section. The sections are `map`, `city`, `food`, `move` and `money`.

## Adding another tab

1. Put the page at `guides/<id>/index.html`. If it's an exported guide with embedded photos, run `python3 tools/import_guide.py <exported.html> <id>`.
2. Add one line to `GUIDES` in `index.html`:
   ```js
   {id:"<id>", en:"Name", vn:"Vietnamese name", region:"short label", c:"#5A3B1E", ci:"#F7EBDD", d:"#E0A52C"}
   ```
3. If any photos were replaced under the same file names, change `CACHE` in `sw.js` (for example `vietnam-v2`) so phones fetch the new copies.

## Updating a guide

Export the updated page, then run `python3 tools/import_guide.py <exported.html> hanoi` (or `danang`), commit, and push. Anyone online gets the new version on their next visit. Anyone who saved the guides for offline should tap **Update saved copy**.
