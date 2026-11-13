# Tube Atlas (AppBreed / Dave Guindon) – official vendor usage instructions, v1.0.6.7 (12 Nov 2026)

Research date: 13 Nov 2026. Read-only: no installer, video or login was used, and no email was entered in any form.

**Main source for click paths.** The 44 help videos on appbreed.com open in OptimizePress popups whose links are `#`, so no video ID could be read from the page text ([help page](https://appbreed.com/help-videos-tube-atlas)). The best readable substitute is the YouTube transcript of **"Find Profitable YouTube Videos Fast (Tube Atlas Tutorial)"**, 2:39:38, uploaded by Vidsilo on 24 May 2022 ([YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4)).
- **Who is speaking (INFERRED).** The narrator speaks as the developer ("i've integrated", "my customers requested", "i'll have a separate video"). The chapters follow the order of help videos 3–28 and 22, so this is very likely a compilation of the vendor's own help-video audio. Vidsilo itself is an affiliate: its description carries an affiliate link and coupon.
- **What it reflects.** The transcript describes v1.0.0.x–1.0.1.0 (May 2022). Later changes come from the official changelog.
- **How much I read.** The transcript is 141,138 characters. I read about 75k of them directly: the intro, the Keywords, Trends, Videos, Browse & Extract, Video-to-Text, Tag analyzer, Title analyzer, Creative Commons, Channels, Analyze-all, Comments, Title generator, Estimated revenue, Email and Reports sections. I keyword-searched the rest but did not read every character of it.

---

## Q1. What is on tubeatlas.com/download.php and the other official download, version and help pages?

### Takeaway
download.php is only a gated form: you enter your registration email and click "Get Download Links". It shows no version, notes, bonuses or help links before that. The useful public information is on AppBreed's update page, which shows **current version 1.0.6.7** and a full version history from 1.0.0.0 (22 Aug 2021) to 1.0.6.7 (12 Nov 2026), and on the post-purchase page, which links to the help videos and to the bonuses.

### Cited Findings
**tubeatlas.com/download.php**
- **What the page contains.**
  - Title "Tube Atlas - Download", meta robots NOINDEX/NOFOLLOW.
  - Heading "Congratulations for getting the Tube Atlas Software!"
  - Instructions to enter the email used at purchase in one field ("Registration email:") and click "Get Download Links".
  - A support link: https://appbreed.freshdesk.com/.
  - No version numbers, release notes, help-video links, bonuses or member links before submission.
  - Source: [tubeatlas.com/download.php](https://tubeatlas.com/download.php)

**Post-purchase page (tubeatlas.com/download-tube-atlas)**
- **Step 1:** watch the installation video for Windows or Mac. Mac users must allow the install.
- **Step 2:** click "Download Software & Bonuses Here" to reach the download page and enter the purchase email. "Bonuses are also on the download page."
- **Other buttons:** "Help Video Tutorials" and a support help desk.
- Source: [tubeatlas.com/download-tube-atlas](https://tubeatlas.com/download-tube-atlas)

**Update page (appbreed.com/apps/api/app-download.php?aid=26)**
- **Top of page.** "Software name: Tube Atlas · Current available version: 1.0.6.7". It has the same email form ("Get Download link"), with support at https://appbreed.com/support.php. Source: [app-download.php?aid=26](https://appbreed.com/apps/api/app-download.php?aid=26)
- **1.0.6.7 (Nov 12, 2026) changelog, verbatim points:**
  - fixed the video download tool after YouTube changes; now offers every available size up to 4K; added audio-only (m4a, mp3) and video-only downloads; faster downloading with a working stop button; download tools auto-update at startup
  - "fixed the date error when sorting the Published column in the videos tool"
  - "fixed the Comments column in the videos tool, the number of comments stopped showing due to a change on Youtube"
  - "video data now extracts with half the requests to Youtube, which helps with the 'too many requests' limitation"
  - fixed a 20-second startup delay
  - the "Convert to Text" button in Video to Text is faster and more reliable
  - "Auto punctuate" now works offline with a built-in English punctuator; it keeps punctuation that already exists and only splits text into paragraphs
  - Source: [app-download.php?aid=26](https://appbreed.com/apps/api/app-download.php?aid=26)
- **Version history entries that bear on usage.** All come from the same page: [app-download.php?aid=26](https://appbreed.com/apps/api/app-download.php?aid=26).

| Version | Date | Change relevant to usage |
| --- | --- | --- |
| 1.0.6.6 | 12 Apr 2026 | Handling of YouTube "too many requests"; threading |
| 1.0.6.3 | 18 Oct 2025 | Trending videos button uses a new "top videos trending source" |
| 1.0.6.2 | 21 Jul 2025 | News & updates tab |
| 1.0.6.1 | 12 Jun 2025 | **"Extract Missing" button** in the Videos tool re-extracts rows that were not extracted; punctuator using a free online AI API |
| 1.0.6.0 | 24 Jan 2025 | Trends improved but "still restricted due to Google getting more and more strict" |
| 1.0.5.9 | 16 Dec 2024 | ChatGPT AI-prompt option for auto-punctuating |
| 1.0.5.8 | 20 Oct 2024 | Data now shows after reordering columns |
| 1.0.5.4 | 24 May 2024 | **Right-click grid → videos tool → "ReExtract NOT EXTRACTED rows"** |
| 1.0.5.2 | 16 Mar 2024 | Trends works better with many keywords; more time periods |
| 1.0.5.1 | 9 Feb 2024 | Better channel extraction for users in European countries |
| 1.0.4.7 | 25 Sep 2023 | Custom filters no longer freeze when removing filters; stray double quotes removed from quick and custom filters |
| 1.0.4.5 | 13 Aug 2023 | Settings tab renamed "Speech to Text APIs" |
| 1.0.4.3 | 23 Jun 2023 | Gladia and Deepgram APIs for speech-to-text, with a help video on inserting API keys |
| 1.0.4.2 | 19 Jun 2023 | **"Is Shorts" column** in the Videos tool; "Open data folder" in the File button of Keywords, Video to Text and Comments |
| 1.0.4.1 | 16 Jun 2023 | **"Save emails to CSV or TXT"** in the File button of Videos and Channels; fixed "too many requests" with the Google option |
| 1.0.3.8 | 25 May 2023 | Video to Text converts Shorts; "Make Paragraphs" button; copy as unpunctuated |
| 1.0.3.1 | 22 Feb 2023 | Improved preview and **export of the interactive HTML table** (wider columns, text boxes for description and tags) |
| 1.0.3.0 | 16 Dec 2022 | **"Channel Country" column removed** from the Videos tool because it froze the app |
| 1.0.2.9 | 6 Dec 2022 | Fixes for users in Europe (GDPR) in the Channels tool and tag counts |
| 1.0.2.8 | 3 Dec 2022 | Search-volume import updated for the new Google Keyword Planner file format |
| 1.0.2.7 | 1 Dec 2022 | Channels tool handles the new @handle links |
| 1.0.2.6 | 8 Nov 2022 | AI text-to-headline and summarizer; "Import Keywords" in the Keywords File button and right-click menu; published-date format changed |
| 1.0.2.5 | 9 Oct 2022 | "File to Text" converts an audio or video file on your computer |
| 1.0.2.2 | 15 Sep 2022 | Right-click "Convert to video embed codes" |
| 1.0.2.0 | 7 Sep 2022 | HTML editor, keyword detection, summarization, image search and suggestions, save to HTML in Video to Text; ad-free video player (click the Video ID column or the thumbnail); **column configuration tool** for Videos and Channels |
| 1.0.1.9 | 27 Jul 2022 | Quick-filter "apply" fixed for numbers containing "+" |
| 1.0.1.6 | 1 Jul 2022 | **"Get Video Ads"** button |
| 1.0.1.4 | 28 Jun 2022 | **"get related videos"** button; "unlisted videos" feature; non-English subtitles in Video to Text |
| 1.0.1.2 | 10 Jun 2022 | "Email" column renamed "Email in Desc"; re-extract rows in the right-click menu; copy hashtags; 10 new columns (Characters in Title, Characters in Desc, Word Count in Desc, Link Count in Desc, Hashtag Count in Desc, Hashtags in Desc, Phone in Desc, Readability Score of Desc, Grade Level of Desc, Tags Count) |
| 1.0.1.1 | 26 May 2022 | "Ads Found" column |
| 1.0.1.0 | 24 May 2022 | Trends extraction rebuilt; proxies removed from Trends |
| 1.0.0.6 | 14 Mar 2022 | Multiple YouTube logins in Settings; **estimated revenue columns** in the Video and Channel tools; email column; hashtag generator in the Keywords, Trends, Tags and Title analyzers; **links to the YouTube description generator in the Tools button menu** |
| 1.0.0.4 | 2 Sep 2021 | Content spinner (Google Translate); **Keywords Everywhere tool for paid KE accounts** |
| 1.0.0.3 | 31 Aug 2021 | Download video tool, video title generator, title analyzer, tags analyzer |

- **Bonuses on the sales page.**
  - Bonus 1: online YouTube Description Generator — fill-in-the-blanks form, emoji picker, 9 prefilled sections, character and word counter, works in a browser.
  - Bonus 2: 19 description templates — 13 for videos, 6 for channels, in 7 styles.
  - Bonus 3: online Hashtag Generator — 240 countries, driven by YouTube and Google autosuggest, no install.
  - Also listed: Shorts training, 10 content reports, 8 PDF reports, commercial and outsource licence, 10 installs.
  - Source: [tubeatlas.com](https://tubeatlas.com/)
- **Help page header links.**
  - Support: https://appbreed.freshdesk.com/support/home
  - "Download Software": https://www.tubeatlas.com/download.php
  - "See Software Updates": https://appbreed.com/apps/api/app-download.php?aid=26
  - Source: [help page](https://appbreed.com/help-videos-tube-atlas)
- **Freshdesk knowledge base.** The public page at /support/solutions shows only the heading "Appbreed Software", with no readable articles. Source: [Freshdesk solutions](https://appbreed.freshdesk.com/support/solutions)

### Inferences
- The download, bonus and member content (the bonus tool URLs and the installer links) is only revealed after a registration email is submitted. It cannot be read without entering details, which this task forbids.
- The "Extract Missing" button (1.0.6.1) and the right-click "ReExtract NOT EXTRACTED rows" (1.0.5.4) are the vendor's intended fix for rows with empty or unextracted cells. They should be run before trusting a grid.

### Gaps
- The download-page content after submission (installer links, bonus links, member area) was not seen. Doing so would require entering an email.
- The Freshdesk knowledge base appears empty or private. No FAQ articles could be read.

---

## Q2. The 44 official help videos: titles, URLs and click paths

### Takeaway
All 44 titles are listed below, but no video URL or ID is publicly readable. The click paths below come from the developer-narrated 2h39m compilation, which covers videos 3–28 and 22. Videos 29–44 (2022–2023 features) have no readable transcript. For those, the changelog lines are the only official text.

### Cited Findings
**Titles, all from [appbreed.com/help-videos-tube-atlas](https://appbreed.com/help-videos-tube-atlas); links there are `#` popups and no IDs or descriptions are shown:**

| # | Title |
| --- | --- |
| 1 | Install/activate on PC |
| 2 | Install/activate on Mac |
| 3 | Keyword generator tool |
| 4 | How to import free keyword search volume data |
| 5 | How to use the Keywords Everywhere tool |
| 6 | Trends tool |
| 7 | Analyze videos using the Videos tool |
| 8 | Analyze video tags |
| 9 | Analyze word combinations in YouTube video titles |
| 10 | Import videos using browse & extract |
| 11 | Import videos using content extraction |
| 12 | Extract channel information using the Channels tool |
| 13 | Import channels using browser & extract |
| 14 | Import channels using content extraction |
| 15 | Analyze all videos in a given YouTube channel |
| 16 | Convert videos to text |
| 17 | Spin content using the spinner tool |
| 18 | Analyze video comments using the comments tool |
| 19 | Download videos |
| 20 | Download video thumbnail images |
| 21 | Video title generator tool |
| 22 | Preview and save table/feed reports |
| 23 | Save and load data |
| 24 | Column quick filters and custom filters |
| 25 | Manage your computer installs |
| 26 | Generate hashtags using several tools |
| 27 | Estimated video revenue columns |
| 28 | Email extraction feature |
| 29 | Adding multiple YouTube logins |
| 30 | Legal content from Creative Commons videos |
| 31 | Extract related videos |
| 32 | Extract unlisted videos |
| 33 | Extract video ads |
| 34 | Video-to-Text HTML Editor |
| 35 | Keyword detection (V2T) |
| 36 | Important sentences (V2T) |
| 37 | Suggested images (V2T) |
| 38 | Ad-free integrated video player |
| 39 | Configure columns |
| 40 | Import keywords into the keywords tool |
| 41 | Text-to-Headline (V2T) |
| 42 | Summarizer (V2T) |
| 43 | Two methods to punctuate content in 1.0.3.8 |
| 44 | New File to Text (Speech to Text) APIs in 1.0.4.3 |

- **Update videos on the same page:** "NEW Updates - Version 1.0.1.6", "LOTS of NEW Updates - Version 1.0.1.2", "NEW Trends Tool Updates - Version 1.0.1.0" and "NEW Updates - Version 1.0.2.0". Source: [help page](https://appbreed.com/help-videos-tube-atlas)
- **Chapters of the compilation:**
  - 0:00 Intro · 10:55 Keyword Generator · 23:27 Trends · 34:06 Video Analyzer · 48:17 Video to Text · 59:37 Tag Analyzer
  - 1:06:11 Title Word Combinations · 1:11:42 Browse & Extract Videos · 1:24:02 Content Extraction · 1:29:11 Creative Commons · 1:36:44 Channel Analyzer · 1:42:57 Browse & Extract Channels · 1:47:25 Content Extraction (Channels) · 1:51:14 Analyze Entire Channel · 1:57:50 Content Spinner
  - 2:09:17 Comment Analyzer · 2:19:58 Video Downloader · 2:24:21 Thumbnail Downloader · 2:25:16 Title Generator · **2:28:38 Estimated Revenue Columns** · 2:30:19 Email Extraction · 2:32:39 Reports & Data Export
  - Source: [YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4)

**Click paths from the transcript.** Every bullet in this part comes from [YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4) unless another source is cited.

**Keywords tool (videos 3, 4, 5, 40)**
- **Generate.** Open the **Keywords** tab, type a seed (for example "dog") and click **Generate**. Keywords come from YouTube autosuggest. "Rank" is the position in the autosuggest dropdown (1 = top). Word and character counts are shown.
- **Search range.**
  - Default is seed + a–z and 0–9 after the seed. Options: before, before and after, or double letter (1,296 extractions).
  - Separate several seeds with commas.
  - An asterisk (for example `dog * toy`) overrides the range and puts each letter in its place.
  - A country dropdown is available.
- **Right-click menu.**
  - Send to the **Trends**, **Video** or **Channel** tool.
  - **Get search volume** through the free import of a Storybase or Google Keyword Planner file (video 4).
  - **Send selected to Keywords Everywhere tool**, which uses KE's API and needs a paid KE account (video 5).
  - Search Google Trends (up to 5 keywords), Google, Bing, Amazon or Etsy; autofit or reset columns; delete; remove duplicates.
- **Checkboxes.** Use right-click → Check boxes, or the header checkbox, to select all, unselect all or select highlighted rows. Ctrl-click highlights several rows. Menu items written as "SELECTED" act on checked rows.
- **File button (bottom).**
  - Save to project file (opens only in the same tool), Load, Save to CSV, Save to text, Copy.
  - **Open last working folder** and Open install folder.
- **Import Keywords.** 1.0.2.6 added "Import Keywords" to the Keywords File button and right-click menu (video 40). Source: [changelog](https://appbreed.com/apps/api/app-download.php?aid=26)

**Trends tool (video 6)**
- **Run.** Open the **Trends** tab, enter or send keywords, choose country, time period, category and property (default YouTube search; also web, image, news, Google Shopping) and click **Go**.
- **Results.** Each keyword gets a mini chart. Clicking a chart opens a line or bar chart that can be saved as an image, text or CSV. A button opens the same query on Google Trends.
- **Rate-limit setting.** Under **Settings**: "after 50 web connections pause between 10 and 60 seconds". The developer recommends 20 connections and 60–120 seconds to avoid Google's rate limit.
- **Proxies.** The proxy settings shown in the video were removed in 1.0.1.0 ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)).
- **Search volume.** Free import or Keywords Everywhere graphs are also available here.
- **File.** Save as project file (Trends only), CSV, text or keywords only.

**Videos tool (video 7) — the key one for niche research**
- **Search.**
  - Enter a seed and click **Search**. The YouTube search "can only search the first page results" (about 20–30 videos).
  - Sort options: relevance, upload date, view count or rating.
  - Options: "contains subtitles" and (from the Creative Commons video) "creative commons license".
  - Optional: tick **Google** and **Bing** and choose the number of pages. Results are de-duplicated across sources; one demo gave 108 unique videos.
- **Settings → downloading threads.** Default 5, maximum 15. The developer uses 5–8.
- **Columns, in order:** Image, Video ID, Link, Source (youtube/google/bing), Search phrase, Title, Description, Characters in title, Views, Likes, Dislikes, Rating, Comments, Length (s), Published, published age in days, **Average views per day = views ÷ published days**, Category, Subtitles, Channel, Channel link, Subscribers, Tags. Later columns include Estimated Video Earnings, Estimated Earnings per Day, Email in Desc, Is Shorts and Ads Found.
- **Grid controls.** Image size slider at the bottom. Click a header to sort. **Double-click the thumbnail** to open the Video Details window (title, tags, description, copy buttons). **Clear** button bottom-right. A button extracts the latest **trending videos** (82 in the demo).
- **Right-click → Videos tool** menu:
  - convert selected video to text
  - send selected video to comments tool
  - download video
  - analyze video tags
  - analyze keywords in video titles
  - plus copy, preview and the actions listed under Q1

**Browse & Extract videos (videos 10, 11) — "Browse or import"**
- **Open the browser.** In the Videos tool click **Browse or import → browser**. The integrated browser has bookmarks on the left, the page in the middle and a link collector on the right.
- **Extract.**
  - Search YouTube and apply YouTube's own filters (duration, upload date, HD and so on).
  - Use **Auto scroll** (it shows a scroll count) and click **Stop**.
  - Click **Extract video links** (376 links in the demo), then **Add links → Videos tool**. Answer Yes to close the window.
  - Back in the Videos tool, click **Analyze**.
  - This is the official way around the first-page limit: "20 pages of results … 500 to limitless".
- **Other controls.** **Clear links** empties the collector. **Create bookmark** takes a label and folder. A **User/Pass** button copies the YouTube login saved in Settings; the password is stored encrypted.
- **Content extraction (video 11).** Paste any page source or text that contains YouTube links, then use **paste → extract links → analyze**.

**Channels (videos 12–15)**
- **Search.** Use Search, or Browse/import (browser or content).
- **Columns.** Total videos, views, subscribers, join date, country, channel keywords/tags, external links, Email in Desc. From 1.0.0.6 these also include **estimated total channel earnings** and **estimated earnings per video**.
- **Content extraction for channels.** Example: Google `site:youtube.com/channel "knife making"`, then right-click → View source, Ctrl-A and Ctrl-C, then **paste → extract links → analyze**.
- **Analyze all videos in a channel (video 15).**
  - Double-click a channel row to select it, then **right-click → Channels tool → Analyze videos for selected channel**.
  - The browser opens on the channel's Videos tab. **Clear links**, run **Auto scroll** to the end and click **Extract video links** (115 of 115 in the demo).
  - Click **Add links → Videos tool**, then **Analyze**. Sort by views or average views per day.
  - For very large channels, sort the channel page first (for example by popular) and scroll only part of the way.
  - Alternative: copy the channel link and paste it into Videos → Browse or import → browser.

**Tag analyzer (video 8)**
- **Run.** Check rows (header checkbox → select all), then **Analyze button → Analyze video tags**, or right-click → Videos tool → analyze video tags.
- **Output.** Occurrences, % of videos, number of unique channels, **average views per tag** and average likes per tag. Sort by any column.

**Title word combinations (video 9)**
- **Run.** Select all rows, then **Analyze → analyze keywords in video titles**.
- **Options.** Stop-words list (editable, can be turned off). Word-combination length 1–6. Click **Generate word stats**.
- **Output.** Occurrences, %, **average views per combination** and likes. The developer filters to occurrences > 5 or > 10, then sorts by average views.

**Creative Commons (video 30)**
- **Run.** In the Videos tool tick the "creative commons license" option and search (first page only).
- **Check.** A Creative Commons column flags each video, but "it will still pick up maybe some that don't have any", so check the licence in the description.

**Video to Text (videos 16, 34–37, 41–44)**
- **Run.** Search with "contains subtitles" checked. Then **right-click → Videos tool → convert selected video to text** and click **Convert to text**.
- **After converting.** Click **Auto punctuate**. Line, word and character counts and a readability score are shown.
- **Spinner.** The built-in spinner translates through Google Translate and back.
- **Later features (changelog only):** HTML editor, keyword detection, summarizer, text-to-headline, image suggestions, Shorts, File-to-Text with Gladia or Deepgram API keys under Settings → Speech to Text APIs, an offline punctuator in 1.0.6.7. Source: [changelog](https://appbreed.com/apps/api/app-download.php?aid=26)

**Comments analyzer (video 18)**
- **Load.** In the Videos tool, double-click a row, then **right-click → Videos → send selected video to comments tool**.
- **Extract.** Click **(1) Load video** into the integrated browser, set the **number of page scrolls** and start. It extracts every 5 scrolls. The demo got 180 comments from 10 scrolls and 918 from 50.
- **Columns.** Commenter, channel, when posted, likes, replies, has-question, profanity. The profanity list is editable via right-click → comments tool → profanity list.
- **Analyze.** Select all, then Analyze to get word combinations (stop words, 1–n words). **Generate word stats** shows average likes. Filter, for example, to occurrences > 9, then use **View comments** to see the exact comments containing a combination.
- **Save.** Data file, CSV or text.

**Downloads (videos 19, 20)**
- **Run.** Tick a row, then **right-click → Video tool → download video**. This opens the video download tool, fills in the link and lists the formats.
- **v1.0.6.7 changes.** Up to 4K, audio-only m4a/mp3 and video-only. Source: [changelog](https://appbreed.com/apps/api/app-download.php?aid=26)

**Title generator (video 21)**
- **Run.** Open **Tools → Video title generator tool**, enter 1–2 seed keywords and choose 10, 20 or 100 random titles, or generate all 1,200+.
- **Columns.** Word and character count. The developer advises keeping titles at or under 70 characters.
- **Actions.** Filters, search YouTube or Google, copy.

**Estimated revenue columns (video 27)** — see Q4.

**Email extraction (video 28)**
- **Column.** "Email in Desc", in both Videos and Channels. To show only rows with an email, type "@" in the quick filter. Multiple emails appear comma-separated, and some values may be Instagram links.
- **Developer's warning:** "do not spam these emails".

**Reports (video 22)**
- **Preview.** **Right-click → Preview → HTML table format** gives a sortable, searchable, paginated table with image hover. **HTML feed format** gives a card view.
- **Save.** **File → Export interactive table file** or **interactive feed file** saves a self-contained .html file to give to clients. Find it with File → Open last working folder.
- **Other formats.** CSV ("for spreadsheets like microsoft excel") and text.

**Filters (video 24)** — no dedicated transcript was found. These are the fragments from other chapters:
- **Quick filters.** Click the magnifier icon in a column header. A popup lets you pick a value or type a condition (for example "greater than 50"), then **Apply**.
- **Search box.** Typing in it filters live.
- **Clearing filters.** Use the clear icon, or **Filters → Clear filters** at the bottom.
- **Custom filters.** Open them from **Filters (bottom) → show/load custom filters**. Choose column, compare type and value, then **Apply**. You can save and load filter files.
- **Sales page:** "create any custom filter you want for any column … save your favorite filter combination to a file, and load your saved filters", for example monetized videos sorted by recent daily views ([tubeatlas.com](https://tubeatlas.com/)).
- **No AND/OR detail.** No text describing AND/OR logic in custom filters was found.

### Inferences
- The sister product Pin Inspector and the Keyword Atlas help pages use the same video set ("How to use column quick filters and custom filters", "How to export/save keyword data"). The grid, filter and report UI is a shared AppBreed component, so their videos would show the same UI ([Pin Inspector help](https://appbreed.com/help-videos-pin-inspector); [Keyword Atlas help](https://appbreed.com/help-videos-keyword-atlas)).
- For CineFactory niche research, the official route to a fair sample is: Browse & Extract with YouTube filters + Auto scroll, then Analyze, then "Extract Missing" or "ReExtract NOT EXTRACTED rows", then export CSV. The plain Search button covers only the first page plus optional Google and Bing pages, so it is biased toward top-ranked results.

### Gaps
- No URL or ID could be read for any of the 44 help videos.
- No readable text was found for videos 24 (filters in depth: AND/OR, filter-file format), 25, 29, 31–44. Related videos, unlisted videos, video ads, column configuration and the HTML editor exist only as changelog lines.
- Possible further text sources, not read:
  - "[Full] Tube Atlas: Content Research Software for YouTube" (IM Toolkit, about 3h40m)
  - "Tube Atlas Tutorial and Demo 2022" (LearnWire)
  - Both are listed as related videos on [YouTube mPErvFp97Yk](https://www.youtube.com/watch?v=mPErvFp97Yk). The 3h40m one may cover the later videos.

---

## Q3. The Tools menu: what each item does and where the "Online" items link

### Takeaway
The four desktop tools in the menu are the spinner, the title generator, the Keywords Everywhere connector and the downloader. "Open Data Extraction Browser" is the integrated browser used by Browse & Extract. The three "Online …" entries are links to the web-based **purchase bonuses** (Description Generator, Description Templates, Hashtag Generator). Their exact URLs are not published.

### Cited Findings
- **Content Spinner Tool.** Rewrites text by translating it through Google Translate (109 languages) and back, with no API cost ([tubeatlas.com](https://tubeatlas.com/)). It has auto-punctuation and word replace via right-click or the File button ([changelog 1.0.0.7](https://appbreed.com/apps/api/app-download.php?aid=26)). The developer says it took "a month" to build and suggests trying different languages ([YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4)).
- **Video Title Generator Tool.** Opened from **Tools → video title generator tool**. It fills more than 1,200 title templates with your seed keyword ([YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4); [tubeatlas.com](https://tubeatlas.com/)).
- **Keywords Everywhere Tool.** Added in 1.0.0.4 "for the users that have a paid keywords everywhere account" ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)). It "connects to your paid keywords everywhere account" through KE's API. Keywords can be sent to it from the Keywords tool's right-click menu, and Trends can show KE volume graphs ([YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4)).
- **Download Youtube Video Tool.** Downloads video, audio-only or video-only and thumbnails. Since 1.0.6.7 it goes up to 4K, adds m4a/mp3 and updates itself at startup ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)).
- **Online Description Generator / Online Description Templates / Online Hashtag Generator.**
  - 1.0.0.6 "added links to youtube description generator in the tools button menu" ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)).
  - These match Bonus 1 (online description generator, 9 prefilled sections, emoji picker, works in a browser), Bonus 2 (13 video + 6 channel description templates) and Bonus 3 (online hashtag generator, 240 countries, YouTube and Google autosuggest) ([tubeatlas.com](https://tubeatlas.com/)).
- **Six ways to generate hashtags.** The sales page says "6 ways" ([tubeatlas.com](https://tubeatlas.com/)). The narration names four in-app sources: the Keywords, Trends, Tag analyzer and Title analyzer tools ([YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4)). The hashtag generator was added to those four tools in 1.0.0.6 ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)).

### Inferences
- **"Open Data Extraction Browser" (INFERRED from the name).** It almost certainly opens the same integrated browser as Videos/Channels → Browse or import → browser: bookmarks, Auto scroll, Extract video/channel links, Add links → Videos or Channels tool.
- **The two counts of hashtag methods (INFERRED).** "6 ways" is probably the four in-app tools plus the online hashtag generator plus copying hashtags from the "Hashtags in Desc" column or right-click "copy hashtags".
- **Credits and privacy (INFERRED).** The "Online" items open AppBreed web pages in a browser. They are probably free bonus pages with no metered credits. Even so, under CLAUDE.md they should not be used unattended or with personal data until the owner looks at them.

### Gaps
- The exact URLs of the three online bonus tools were not found publicly. They are most likely revealed on the gated download page or inside the app.
- No official text describes the Keywords Everywhere setup steps (where the API key is entered). Video 5 was not readable.

---

## Q4. Reconciling the owner's run: Estimated Video Earnings = Views × $1.85/1,000; Avg Views/Day = Views ÷ age; Comments "not-given"

### Takeaway
Vendor material **confirms the formulas for Avg Views per Day and Estimated Earnings per Day**. It describes Estimated Video Earnings only as "a special algorithm formula on the internet … rough estimate" and **never names a CPM or RPM or a settings field to change it**. The owner's observed flat $1.85 per 1,000 views (OWNER) is therefore a hidden constant, not a documented, configurable rate. The 1.0.6.7 changelog explicitly says the Videos-tool Comments column had broken and was fixed on 12 Nov 2026.

### Cited Findings
- **Developer's own words on earnings.** "i found a special algorithm formula on the internet that just does a rough estimate so obviously this is not exact it's just an estimate". And: "estimated earnings per day … takes the overall estimated earnings and it divides it by the published age in days". Channels show "total channel earnings" and "estimated earnings per video". Source: [YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4), chapter 2:28:38.
- **Average views per day.** It "takes basically the number of views … and divides it by the published days". Source: [YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4), chapter 34:06.
- **No RPM or CPM anywhere official.** The full changelog never mentions RPM or CPM. The only revenue entry is 1.0.0.6, "added estimated revenue columns" ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)). The sales page lists "Estimated Video Earnings" and "Estimated Earnings per Day" (columns 25 and 26) without a method ([tubeatlas.com](https://tubeatlas.com/)). The settings shown in the transcript are downloading threads, the Trends pause, the YouTube login and (later) Speech-to-Text API keys. No earnings-rate field is shown ([YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4); [changelog](https://appbreed.com/apps/api/app-download.php?aid=26)).
- **Third-party reviewer.** "Earnings and search volume figures are estimates, not real data" ([SaaSPic](https://saaspic.com/tools/tube-atlas)).
- **Comments column fix.** 1.0.6.7: "fixed the Comments column in the videos tool, the number of comments stopped showing due to a change on Youtube". The same release also fixed the Published-column sort error ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)). Earlier Comments-tool fixes: 1.0.5.0, 1.0.5.3, 1.0.5.5 ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)).
- **Re-extraction tools.** "Extract Missing" (1.0.6.1) and "ReExtract NOT EXTRACTED rows" (1.0.5.4) exist for incomplete rows ([changelog](https://appbreed.com/apps/api/app-download.php?aid=26)).

### Inferences
- **The $1.85 rate.** A single $1.85/1,000 for every category matches "a rough estimate" from one internet formula. It ignores monetization status, made-for-kids status, Shorts vs long-form and country. It is a ranking proxy proportional to views and **adds no information beyond Views**. Sorting by Estimated Video Earnings equals sorting by Views; sorting by Estimated Earnings per Day equals sorting by Avg Views per Day. Treat both as OBSERVED-derived from views, never as revenue.
- **Checking the constant locally.** Compute `est_earnings / views × 1000` across the exported CSV (this matches the gap noted in data_standards.md). Since no settings field exists, the owner cannot "fix" the rate inside the app. Any RPM model belongs in CineFactory's own `cf_research_stats.py`, labelled INFERRED.
- **Why Comments shows "not-given".** There are two separable causes:
  - (a) A YouTube page change broke the Videos-tool Comments column, fixed in 1.0.6.7 on 12 Nov 2026. If the owner's run used 1.0.6.6 or earlier, or the update had not been applied, blanks are expected for all videos.
  - (b) Made-for-kids videos have comments disabled by YouTube, so even a working extractor finds no count. This is general YouTube policy, not taken from vendor material, and is unverified here.
  - To separate them, re-run on 1.0.6.7 with "Extract Missing" or "ReExtract NOT EXTRACTED rows". If only kids videos stay blank, cause (b) applies, and the value should be recorded as "disabled/not available", not 0.
- **Avg Views per Day is a lifetime average** (views ÷ age). It is biased in favour of very new videos and against old evergreen ones. The developer himself compares a 1-day-old video at 228/day with an 800-day-old one at 69/day ([YouTube Vt8ktMezDJ4](https://www.youtube.com/watch?v=Vt8ktMezDJ4)).

### Gaps
- The actual "internet formula" and the exact constant behind Estimated Video Earnings are not disclosed in any readable vendor text. Video 27's own description is not readable. The $1.85 figure remains OWNER-observed only.
- No vendor statement explains how the app handles videos whose comments are disabled (kids content). Whether it shows blank, "not-given" or 0 in v1.0.6.7 is not measured.
- The owner's app version at the time of the run is unknown. It should be checked against 1.0.6.7, which is what the update page currently offers.
