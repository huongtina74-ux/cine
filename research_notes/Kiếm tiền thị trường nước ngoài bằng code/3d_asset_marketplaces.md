# 3D / Blender digital-asset marketplaces for a small Vietnam-based studio (state as of Nov 2026)

Labels: **OBSERVED** = stated in the linked source (URL given). **INFERRED** = my arithmetic or reasoning from observed figures. **ESTIMATED** = not used for earnings anywhere; no earnings figure here is invented. Sources dated before 2026 are marked with their date. Seller self-reports are labelled "self-reported, unverified".

Researcher's note on method: about 15 search/fetch calls. No accounts were created, no assets were downloaded, no money was spent. The CGTrader 2026 market report PDF was read only through its public landing page and press coverage, not the full PDF.

---

## Q1. Marketplaces and their 2026 terms (commission, payout, eligibility for a Vietnam seller)

### Takeaway
Of the open marketplaces, Fab (88%) and Cults3D/Printables (80%) pay sellers the highest share. Superhive pays 70% on its free tier, and CGTrader cut its rate to 55–80% in September 2026. Most Western marketplaces can pay a Vietnam resident through PayPal, which can receive international payouts in Vietnam. Some also pay through Hyperwallet, Payoneer or a local bank. The bigger friction is tax: no US–Vietnam tax treaty is in force, so 30% US withholding can apply to US-source royalties.

### Cited Findings

**Superhive (formerly Blender Market)**
- OBSERVED: Commission is 70% on the Free plan, 80% on Pro ($49/month) and 90% on Ultimate ($199/month). Every sale also carries a $0.49 per-item fee plus a merchant fee of 5.5% / 5.0% / 4.0% by tier. — [Superhive pricing](https://superhivemarket.com/pricing); [Commission calc](https://support.superhivemarket.com/article/32-how-your-commission-earnings-are-calculated)
- OBSERVED: Superhive's worked example: on the Free plan, a $20 sale leaves the creator $12.87, calculated as (20 − 20×0.055 − 0.49) × 0.70. — [Superhive help](https://support.superhivemarket.com/article/32-how-your-commission-earnings-are-calculated)
- OBSERVED: A third-party analysis puts the effective take on a $30 sale at about 37.1% (Free), 26.6% (Pro) and 16.3% (Ultimate). Payouts run on the 1st and 15th. FX costs about 1% via Stripe and up to 4% via PayPal for non-US sellers, and a first payout can take about 45 days. — [AssetAlley, 2 Oct 2026](https://assetalley.io/learn/blender-market-fees)
- OBSERVED: There is no exclusivity requirement. Superhive is the merchant of record. — [Why sell on Superhive](https://support.superhivemarket.com/article/51-why-do-you-sell-your-products-on-blender-market); [Creator ToU](https://support.superhivemarket.com/article/44-terms-of-use-creator)
- OBSERVED: To sell, you must be 16+, live in a country Superhive can pay, and have a working payout method before your first product can be submitted. New creators get a 30-day hold until their first payout. Each new creator's first product is reviewed, and they can have only one product in progress at a time until it is approved. — [Who can sell](https://support.superhivemarket.com/article/55-who-can-sell-products-on-blender-market)
- OBSERVED: Payout methods are Stripe Connect (Express), PayPal (the account must be able to *receive*, not "send only") and Wise (monthly only). If none of the three works in your region, Superhive cannot accept you. — [Can I be paid](https://support.superhivemarket.com/article/273-can-i-be-payed-as-a-creator-on-blender-market)
- OBSERVED (2026 policy): "Support Periods" are optional. A creator who opts a product in commits to 12 months of support and updates, with replies within 3 business days and good-faith compatibility with the current Blender LTS. Customers can buy discounted renewals. — [Support Period FAQ – creators](https://support.superhivemarket.com/article/331-support-period-faqs-creators); [Overview](https://support.superhivemarket.com/article/340-support-periods-overview). The policy drew community backlash ([BlenderArtists thread, Mar 2026](https://blenderartists.org/t/superhive-changes/1634680?page=22)).
- OBSERVED: AI policy: fully AI-generated products (for example, raw prompt-to-3D models) are not allowed. AI-assisted work with significant human input is allowed, and disclosure is strongly recommended. — [Superhive AI policy](https://support.superhivemarket.com/article/311-superhive-market-ai-policy)

**Fab (Epic; replaced the Unreal Marketplace, Sketchfab Store and ArtStation Marketplace)**
- OBSERVED: Sellers receive 88% of revenue. Fab pays about 30 days after month end once the balance is at least $100; smaller balances roll over, and any remainder is paid on 30 January. Payouts go through a third-party payout provider. — [Fab Publisher Get Started](https://dev.epicgames.com/documentation/en-us/fab/publisher-get-started-in-fab); [UE forum, Dec 2024](https://forums.unrealengine.com/t/not-receiving-payments/2168321)
- OBSERVED: That provider is Hyperwallet (PayPal-owned), according to seller payout threads. December 2024 payouts were wrongly paid at 88% instead of the promised 100% and corrected in February 2025. — [Epic announcement, 30 Jan 2025](https://forums.unrealengine.com/t/issue-with-seller-payouts-for-december-revenue/2311091)
- OBSERVED: Epic collects sales tax and VAT as the seller's agent in listed jurisdictions. It may withhold payouts if tax documentation is missing. — [Fab Distribution Agreement](https://www.fab.com/distribution-agreement?lang=en)
- OBSERVED: Publishers have 60 days from the Publisher Agreement to provide payout information, or the account is closed. — [UE forum, Feb 2025](https://forums.unrealengine.com/t/no-payment-and-also-strange-requests-from-fab/2325682)
- OBSERVED but contradictory: One seller blog says Fab pays on the 15th, holds new sellers' revenue for 60 days, and supports PayPal, direct deposit and Wise. — [StraySpark, Apr 2026](https://www.strayspark.studio/blog/fab-marketplace-12-month-retrospective-seller-2026). This conflicts with Epic's own docs (≈30 days after month end, third-party provider), so treat the blog's payout details as unverified.
- OBSERVED: In May 2025 Fab made the "Created with AI" declaration mandatory. Buyers can hide AI products. The change followed a single seller uploading more than 41,000 AI models. — [AI Trace, Mar 2026](https://www.aitrace.org/company/epic-games/practice/81eb9eed-bae9-4486-9af0-9cf9e12fe341); [StraySpark](https://www.strayspark.studio/blog/fab-marketplace-12-month-retrospective-seller-2026)

**CGTrader**
- OBSERVED: From 15 Sep 2026 the payout rate runs from 55% to 80% across 26 levels, based on rolling 12-month net sales. Level 1 ($0) pays 55%, $1,000 of sales pays 61%, and $300k pays 80%. The previous scale was 60–85%. Referred buyers still pay 85% for one year. — [CGTrader rate update FAQ](https://help.cgtrader.com/hc/en-us/articles/50374021634833-Payout-Rate-Update-September-15-2026-FAQ); [New table](https://help.cgtrader.com/hc/en-us/articles/35293756906257-New-Payout-Rate-System-Explained); [Old table](https://help.cgtrader.com/hc/en-us/articles/35293756906257-Payout-Rate-System-Explained)
- OBSERVED: Payouts go through Hyperwallet, according to the help-centre article list. From 15 May 2026, standard listings can no longer be licensed for AI training; that is now possible only through enterprise deals that CGTrader negotiates. — [CGTrader help, Apr 2026](https://help.cgtrader.com/hc/en-us/articles/46191349842705-Can-my-models-still-be-licensed-for-AI-training)
- OBSERVED: CGTrader accepts AI-generated uploads. — [Fortune, 20 Aug 2026](https://fortune.com/2026/08/20/ai-product-fatigue-online-marketplace-ecommerce/)

**TurboSquid (Shutterstock)**
- OBSERVED: Royalties are paid monthly by PayPal or Payoneer. Exclusivity is optional; exclusive SquidGuild members earn higher royalties. — [TurboSquid Royalties FAQ, Dec 2025](https://www.turbosquid.com/help/en/articles/12638911-artist-royalties-faq); [General seller FAQ](https://resources.turbosquid.com/general-info/general-information-faqs/general-seller-faq)
- OBSERVED: TurboSquid does not accept AI-generated content, including AI-generated geometry or textures. Its content was used to train the 3D AI generator that Shutterstock built with NVIDIA, and contributors get royalties for that through a Contributor Fund. — [TurboSquid AI policy, Oct 2025](https://www.turbosquid.com/help/en/articles/12633683-turbosquid-s-policy-on-publishing-ai-generated-content); [Data deals FAQ](https://www.turbosquid.com/help/en/articles/12530239-data-deals-faq)

**Unity Asset Store**
- OBSERVED: Publishers keep 70% with no publishing fee. The minimum price is $4.99. Payouts are monthly via PayPal, or quarterly by wire for balances over $250, in USD only. Unity may change the share at its discretion (Provider Agreement, updated 13 Apr 2026). — [Unity publishing page](https://assetstore.unity.com/publishing/publish-and-sell-assets); [Payout docs](https://docs.unity.com/en-us/asset-store/publishing/asset-packages/revenue/payouts); [Provider Agreement](https://unity.com/legal/provider)
- OBSERVED: Unity says it has more than 1.7 million monthly Asset Store users. — [Unity publishing page](https://assetstore.unity.com/publishing/publish-and-sell-assets)

**Gumroad**
- OBSERVED: Direct sales cost 10% + $0.50, plus card processing of 2.9% + $0.30. Sales through Gumroad's Discover marketplace cost a flat 30%. After $20k of sales in a month, direct sales drop to 5% + $0.50. Gumroad has been merchant of record since 1 Jan 2025. — [Gumroad fees](https://gumroad.com/help/article/66-gumroads-fees); [Pricing](https://gumroad.com/pricing)
- OBSERVED: Gumroad pays to a local bank account in Vietnam, or by PayPal elsewhere. It does not pay to Payoneer or Wise. The minimum payout is $100, and PayPal payouts carry a 2% fee. — [GetPaidAtlas, 30 Oct 2026](https://getpaidatlas.com/guides/gumroad-payout-countries); [Swell, 2026](http://www.swell.is/content/gumroad-pricing)
- OBSERVED: Gumroad's 2025 company revenue was $17.8M, down about 6% from 2024. This is a secondary source citing Gumroad's SEC report. — [StealWhatWorks, Sep 2026](https://stealwhatworks.com/blogs/news/gumroad-products-making-real-money-now)

**itch.io**
- OBSERVED: Sellers choose the revenue share themselves; the default is 10%, with processing extra. Payouts go to PayPal or Payoneer, and without a tax interview / TIN the default is 30% withholding. — [Getly comparison, Nov 2026](https://www.getly.store/blog/itch-io-vs-gumroad) (secondary)

**3D-print STL marketplaces**
- OBSERVED: Cults3D pays creators 80% of the net (ex-VAT) price, bank fees included, with no subscription. It accepts STL/OBJ/3MF/STEP and also DXF/DWG/SVG CNC files. — [Cults3D upload page](https://cults3d.com/en/upload); [Cults3D home](https://cults3d.com/en)
- OBSERVED: Printables (Prusa) takes 20% on single downloads and 10% on subscriptions, with Stripe fees on top. Its worked example: a $10 subscription leaves the creator $8.41. — [Printables Store T&C](https://www.prusa3d.com/page/printables-club-store-terms-and-conditions-for-creators_236503)
- OBSERVED: MyMiniFactory takes 15% (Upcoming), 12.5% (Pro) or 10% (Studio), plus 3.49% + $0.49 per payment over $3. MyMiniFactory acquired Thingiverse in Feb 2026. — [MMF fees](https://creator.myminifactory.com/store-manager-fees); [Emrld Labs, Aug 2026](https://emrldlabs.com/blog/printables-cults3d-myminifactory-stl-marketplace-compared)
- OBSERVED: Thangs charges 30% on single models under $5, 20% for $5–10 and 15% for $10 and up. It claims more than 20M monthly active users (platform claim). — [Thangs marketplace](https://thangs.com/marketplace)

**Archviz furniture stores**
- OBSERVED: On 3dsky (and its sister site 3ddd.ru), every PRO model costs a fixed $7. Author royalty starts at 40% and rises with a sales-badge scale. Balances are kept in Russian rubles, converting USD sales at the MICEX rate. Withdrawals go via Payoneer ($) and are processed manually. Models must be 3ds Max with V-Ray or Corona, built in millimetres and with quad topology. The operator is 3DWORLD LTD in Cyprus. — [3dsky royalties FAQ](https://3dsky.org/faq/201/show); [3dsky blog, Dec 2025](https://3dsky.org/blog/post/3dsky-the-fixed-price-3d-marketplace-for-archviz-creators-and-beyond); [Royalties category](https://3dsky.org/faq/category/10010/show); [Author ToU](https://3dsky.org/faq/116/show)

**CNC / laser cut-file markets (Etsy alternatives)**
- OBSERVED: Creative Fabrica pays designers 50% of the net price on single sales. Designers set their own prices, the relationship is non-exclusive, and payouts can be requested at any time. — [Creative Fabrica Designer T&C v1.5, Apr 2026](https://www.creativefabrica.com/pl/designers-terms-conditions-v1-5)
- OBSERVED: Design Bundles advertises 50–75% commission and 7-day payouts, but its page currently says it is *not accepting new store applications*. Its subscription partners share a fund equal to 50% of net subscription income. — [Design Bundles store register](https://designbundles.net/store-register); [Partner fund](https://fontbundles.freshdesk.com/en/support/solutions/articles/42000103305-how-much-do-you-make-on-design-bundles-)

**VRChat avatar channels**
- OBSERVED: On VRChat's own Creator Economy, creators get about 50% of what users spend (ex-VAT). Payouts go via Tilia to PayPal. Avatar sellers must apply, and the minimum price is about $10 (1,200 Credits). — [VRChat CE FAQ](https://creators.vrchat.com/economy/faq/); [Avatar Marketplace FAQ, May 2025](https://ask.vrchat.com/t/avatar-marketplace-faq-for-sellers/43555)
- OBSERVED: Jinxxy says it has 13K+ active creators, $10M+ in creator earnings (cumulative) and 150+ supported countries. It acts as merchant of record and pays weekly. These are platform claims. — [Jinxxy selling](https://jinxxy.com/about/selling)

**Vietnam-specific payout and tax facts**
- OBSERVED: Hyperwallet's PayPal transfer method supports payees in Vietnam, and receivers need a bank account linked to PayPal. — [Hyperwallet PayPal docs](https://docs.hyperwallet.com/content/transfer-methods/v1/paypal)
- OBSERVED: In one Hyperwallet program (WorkMarket), payouts to Vietnamese bank accounts in VND carry no transfer fee and a 2–3% FX fee. That is another program's table, not Fab's or CGTrader's. — [WorkMarket Hyperwallet table, Jul 2026](https://workmarket.zendesk.com/hc/en-us/articles/31431909954455-Hyperwallet-Supported-Countries-and-Transfer-Fees)
- OBSERVED: Patreon's PayPal/Hyperwallet payout country list includes Vietnam. — [Patreon help](https://support.patreon.com/hc/en-us/articles/29467737603981-Paypal-supported-countries)
- OBSERVED: PayPal Vietnam can receive international payments, but transfers between two Vietnamese PayPal accounts have been blocked since 2016. — [Payxem, Aug 2026](https://payxem.com/blog/how-freelancers-in-vietnam-get-paid)
- OBSERVED: Sources disagree on Stripe. One says Stripe does not support Vietnam ([TaxSym, Aug 2026](https://www.taxsym.com/blog/itin-application-vietnam)); another says Stripe lists Vietnam but in practice serves registered businesses only ([Payxem](https://payxem.com/blog/how-freelancers-in-vietnam-get-paid)).
- OBSERVED: The US–Vietnam income tax treaty was signed in 2015 but never ratified by the US Senate. US-source royalties to a Vietnamese resident therefore face the default 30% withholding, and a W-8BEN cannot claim a treaty rate. — [TaxSym, Aug 2026](https://www.taxsym.com/blog/itin-application-vietnam); [W&A Consulting, Sep 2026](https://www.wna.global/post/withholding-tax-in-vietnam-a-practical-guide-for-foreign-companies-and-investors)
- OBSERVED: Vietnam's Decree 252/2026/ND-CP (30 June 2026) sets withholding duties for e-commerce and digital platforms. These include personal income tax on Vietnamese tax-resident sellers' domestic *and overseas* transactions. Income that no platform has withheld must be self-declared. — [EY Tax News, 10 Jul 2026](https://taxnews.ey.com/news/2026-1464-vietnam-updates-digital-tax-regulatory-framework-with-new-guidance)

### Inferences
- INFERRED, from the PayPal/Hyperwallet country lists: every marketplace surveyed has at least one payout route open to a Vietnam individual. Superhive (PayPal or Wise), Fab (Hyperwallet), CGTrader (Hyperwallet), TurboSquid (PayPal/Payoneer), Unity (PayPal), Gumroad (local VND bank), itch.io (PayPal/Payoneer), Cults3D/Printables (bank/Stripe; not individually verified for Vietnam) and 3dsky (Payoneer). Stripe-only routes (for example Printables Store, which pays through Stripe) are the risky ones.
- INFERRED: The missing tax treaty matters most where a platform treats payments as US-source royalties and acts as withholding agent (Unity, itch.io, possibly Fab and CGTrader). Gumroad and Superhive are merchants of record that pay "sales proceeds", so the 30% treatment may not apply there. This needs a tax advisor; see Gaps.
- INFERRED: Superhive's Free tier keeps only about 63% of a $30 sale after fees. Pro ($49/month) beats Free once monthly gross sales reach roughly $350–400. (INFERRED: the gap between the tiers is about 10.5–11 points of gross, so $49 ÷ 0.105–0.11 ≈ $445–470 gross; rough threshold, not verified.)
- INFERRED: 3dsky is a poor fit for a Blender-only studio. It requires 3ds Max with V-Ray/Corona, pays as little as $2.80 per sale (40% × $7), and holds balances in rubles, which brings FX and sanctions-related payout risk.
- INFERRED: The Etsy suspension does not directly block any of these platforms. Creative Fabrica, Cults3D and Gumroad are the practical Etsy replacements for cut files. Design Bundles is currently closed to new stores.

### Gaps
- No primary source was found for TurboSquid's current royalty percentages (non-exclusive vs SquidGuild exclusive). No 2026 rate page surfaced.
- Not verified: whether Fab's Hyperwallet program and CGTrader's Hyperwallet program each support VND bank payouts for Vietnam (only another program's table was seen), and Cults3D's payout methods for Vietnam.
- Not verified: whether Fab, CGTrader, Superhive and Gumroad treat a Vietnamese seller's proceeds as US-source royalties subject to 30% withholding. Needs each platform's tax-interview outcome or a tax advisor.
- No current terms found for KitBash3D (it appears to work with studios and creators by contract; no open marketplace terms surfaced), Adobe Substance 3D Assets (no open contributor program found), SketchUp 3D Warehouse (no paid-model program found), Chaos Cosmos (no contributor program found) or Poly Haven (free and CC0, so not a revenue channel).

---

## Q2. Real earnings evidence (platform-level and individual)

### Takeaway
Totals at platform level are large: Fab paid creators more than $24M in 2025, and Superhive has paid more than $53M since 2014. Spread across sellers, though, the averages are small, roughly $1.2k per Fab publisher per year (INFERRED mean). Superhive itself reports that average earnings per creator are falling as the number of creators grows. Earnings are heavily concentrated: the top Fab products earn high six to low seven figures a year, while a free add-on with 13.5k downloads raised $96 in donations.

### Cited Findings
- OBSERVED: In 2025, creators earned more than $24M on Fab. The library tripled to more than 420,000 listings and the number of publishers doubled to more than 20,000. Event sales produced up to 50% of a month's revenue on average, and flash sales about 25%. — [Epic, Fab 2025 Year in Review, 22 Jan 2026](https://unrealengine.com/en-US/news/fab-2025-year-in-review)
- OBSERVED (seller blog, not Epic): The top Fab products earn "high six figures to low seven figures annually". A new seller's first 3–6 months typically earn less than the same period would have on the 2022-era Unreal Marketplace. — [StraySpark, Apr 2026](https://www.strayspark.studio/blog/fab-marketplace-12-month-retrospective-seller-2026)
- OBSERVED: Superhive's cumulative figures since June 2014: 6,557 creators, 73,259 products (59,045 models, 6,619 add-ons, 4,666 surfacing, 400 render setups, 717 training), $53,393,097 paid to creators, 5,784,243 items sold and 1,136,093 customers. — [Superhive market stats, live page, read Nov 2026](https://superhivemarket.com/market-stats)
- OBSERVED: Superhive says it has more than 125,000 monthly unique visitors and about 1M page views a month. — [Superhive help](https://support.superhivemarket.com/article/51-why-do-you-sell-your-products-on-blender-market)
- OBSERVED (Cyber Sale 2024, 5 days): gross merchandise value $713,399.73, creator earnings $540,903, 1,442 creators paid. Average earnings per creator were $375.11, "down from $523.41". The post says "the market as a whole is growing but individual creators are earning a smaller slice of the pie." — [Superhive Cyber 2024 recap](https://superhivemarket.com/posts/blender-market-2024-cyber-sale-recap). (The post says the prior figure was "in 2024", apparently meaning the 2023 sale.)
- OBSERVED (Winter Sale, early 2025, 6 days): 1,483 creators earned $354,858.06, with an average order of $38.42. — [Superhive Winter Sale 2025 recap](https://superhivemarket.com/posts/winter-sale-2025-recap)
- OBSERVED: Superhive's operator Autotroph says that across "virtually all top sellers", the number of users keeps growing while sales are flat or declining. Add-on creators are "working harder than ever for less income". — [Autotroph blog, 18 Feb 2026](https://autotroph.com/the-blender-creator-economy-is-breaking-lets-start-talking-about-it)
- OBSERVED (self-reported, unverified): A Fab seller of MetaHuman clothing says he makes about $160k a year, over $10k a month. — [Andrew Vish YouTube, Mar 2026](https://www.youtube.com/watch?v=M8deOQmee14)
- OBSERVED (self-reported marketing page, unverified): Blender Bros claim more than $2.5M in lifetime sales of Blender digital products, about $2.1M of it on their own platform rather than Blender Market or Gumroad. They argue there "wasn't enough traffic to sell millions of $10 addons". — [Blender Bros](https://www.blenderbros.com/bbd)
- OBSERVED: A free, donation-based add-on (OpenVAT) has had more than 13,500 downloads and earned about $96. — [r/blender, ~mid-2026](https://www.reddit.com/r/blender/comments/1t3zvr5/13500_downloads_96_earned_curious_how_people_feel)
- OBSERVED: In the Blender Foundation's 2024 survey, 44% of respondents make money with Blender. About 1 in 6 of those who earn from art also create assets, and about 1 in 20 respondents profit from add-on development. — [Blender Survey 2024](https://survey.blender.org/feedback/2024)
- OBSERVED: CGTrader's CEO says one of the top-selling print designers has fewer than five models. — [3DPrinting.com, Aug 2026](https://3dprinting.com/news/3d-print-buyers-ai-cgtrader-report-2026/)
- OBSERVED (secondary): CGTrader designer payouts were up 13% year on year as of August 2026. — [Tech-Insider, Oct 2026](https://tech-insider.org/unity-asset-store-vs-fab-vs-cgtrader-2026)
- OBSERVED: Jinxxy (VRChat-focused) reports $10M+ in cumulative creator earnings across 13K+ creators. — [Jinxxy](https://jinxxy.com/about/selling)
- OBSERVED: VRChat avatars on Gumroad typically sell for $25–$40. One store, Jinxed Otter, shows 226 sales at a minimum of just over $29. — [StealWhatWorks, Sep 2026](https://stealwhatworks.com/blogs/news/gumroad-products-making-real-money-now)
- OBSERVED (low-reliability aggregator, unverified): "avatar designers earning $3K/month… top sellers move 200–500 units per month." — [creator-economy.org, Jun 2026](https://creator-economy.org/vrchat-creator-economy-worlds-avatars-real-money)

### Inferences
- INFERRED: Mean Fab creator earnings in 2025 were at most $24M ÷ 20,000 ≈ $1,200 per publisher per year. Because the top products earn six to seven figures, the median is almost certainly far lower. Epic does not publish it.
- INFERRED: Superhive's lifetime mean is about $53.4M ÷ 6,557 ≈ $8,140 per creator since 2014. That is a long-run mean skewed by top add-on sellers.
- INFERRED: The Winter Sale 2025 average was $354,858 ÷ 1,483 ≈ $239 per creator over 6 days. Taken with the Cyber 2024 drop from $523 to $375, the average Superhive creator earns a few hundred dollars even in peak sale weeks.
- INFERRED: Add-ons are about 9% of Superhive products (6,619 of 73,259) but dominate its earnings narrative. AssetAlley says Superhive's audience "skews toward add-on buyers", so models are the crowded, low-yield part of that store.
- INFERRED: The largest verifiable incomes (Blender Bros, Andrew Vish) come from sellers who own an audience or a narrow premium niche (MetaHuman clothing), not from catalogue volume.

### Gaps
- No marketplace publishes a median or a seller earnings distribution (percentiles). Superhive publishes only sale-week averages.
- No independent CGTrader or TurboSquid seller income survey from 2025–2026 was found.
- No Superhive Cyber Sale 2025 recap with a per-creator average was found. Searches returned only the 2024 Cyber and early-2025 Winter recaps.
- Individual income claims above are self-reported and could not be verified.

---

## Q3. Which categories sell best in 2025–2026

### Takeaway
Demand is strongest for real-time-ready, high-quality, specific assets: environments, characters, engine tools and procedural systems (Fab), and real-time formats such as USD, glTF and Unreal (CGTrader). 3D-print files are the fastest-growing market. Commodity categories are being squeezed, and CGTrader names furniture, household and food explicitly. PBR matters for how often a model sells, not for the price.

### Cited Findings
- OBSERVED: Fab's top categories in 2025 were environments, characters, engine tools, procedural systems and gameplay features. Top themes were realistic, fantasy, stylized, medieval and horror. Demand was strong for realistic styles, RPG frameworks, Blueprint products and dynamic VFX. Epic's outlook for 2026 is "high-quality environments, game-mechanics tools and plugins, and procedural game systems." — [Epic Fab 2025 Year in Review](https://unrealengine.com/en-US/news/fab-2025-year-in-review)
- OBSERVED (CGTrader, Jun 2025–May 2026): demand grew 5.1%, supply grew 18.5% (about 3.6× faster) and the average price fell 9.7%. — [CGTrader blog, 23 Jul 2026](https://www.cgtrader.com/blog/3d-model-market-trends-2026-growth-raised-the-bar)
- OBSERVED (CGTrader CG demand by category, year on year, indexed to Character = 100): Character −1%, Exterior +10%, Interior +7%, Military +7%, Architectural +3%, Plant +1%, **Furniture −6%**, Vehicle +15%. About two-thirds of CG categories grew in units. "The squeeze concentrates in commodity, easy-to-flood categories — furniture, household, food." — [CGTrader trends page](https://www.cgtrader.com/discover/3d-market-trends)
- OBSERVED: Demand for real-time formats (USD/USDZ, Unreal, Unity, glTF) grew 40–48%. Blender-format demand grew at about twice the market rate, while traditional DCC formats (for example ZBrush) were flat or declining. Coverage reports the format numbers slightly differently, so treat the exact per-format figures as approximate. — [WebProNews, Aug 2026](https://www.webpronews.com/ai-3d-models-swamp-marketplaces-yet-buyers-stay-away); [CGTrader trends page](https://www.cgtrader.com/discover/3d-market-trends)
- OBSERVED: PBR models are about 40% more likely to ever sell. They list about 35% higher but sell at nearly the same realized price. — [CGTrader blog](https://www.cgtrader.com/blog/3d-model-market-trends-2026-growth-raised-the-bar); [Trends page](https://www.cgtrader.com/discover/3d-market-trends)
- OBSERVED: 3D-print unit demand grew 7.5% vs 3.7% for CG, while print listings grew 23.4%, the widest supply–demand gap. 9 of 10 print categories grew: Miniatures (largest) +4%, Art +1%, Jewelry +8%, Games & Toys +13%, Hobby & DIY +14%. — [CGTrader trends page](https://www.cgtrader.com/discover/3d-market-trends)
- OBSERVED: VRChat avatars are a "surprisingly real" Gumroad niche. In one Gumroad sample, every measured VRChat avatar listing had at least one rating. — [StealWhatWorks, Sep 2026](https://stealwhatworks.com/blogs/news/gumroad-products-making-real-money-now)
- OBSERVED: Typical laser/CNC cut-file prices are $2–5 for a simple single design, $5–12 for a detailed or functional one, $15–40 for a bundle of 10+, and $25+ for custom work. — [TechDrawAI, Jul 2026](https://techdrawai.com/blog/how-to-sell-dxf-files-online). A real store example: CNC furniture DXF/SVG files at about $4–11 each and a welding-tabletop DXF bundle at $80. — [CADtsy furniture collection](https://cadtsy.com/collections/cnc-furniture-plans-dxf); [CADtsy](https://cadtsy.com/)
- OBSERVED (2023, older): CNC and laser files get pirated and resold within days of release, and one maker pulled their files from Etsy for that reason. — [Carbide3D forum, Apr 2023](https://community.carbide3d.com/t/selling-files-on-etsy/61376)
- OBSERVED: Blender add-on buyers increasingly expect ongoing updates, which is why Superhive introduced Support Periods. — [Autotroph, Feb 2026](https://autotroph.com/the-blender-creator-economy-is-breaking-lets-start-talking-about-it)

### Inferences
- INFERRED: The categories with the strongest evidence of demand **and** a defensible moat are tools and procedural systems (Fab engine tools and procedural systems, Blender add-ons) and high-quality environment kits. Generic furniture models and generic low-poly props are the weakest fit, because the data shows furniture demand falling and supply flooding in.
- INFERRED: The studio's furniture CAD/CNC knowledge (WoodFab) is better monetized as **tools** than as models. Examples: a Blender add-on or geometry-nodes generator that builds parametric cabinets or furniture and exports cut lists and DXF nesting, or CNC furniture plan packs. Generic archviz furniture meshes are a shrinking, commodity market.
- INFERRED: 3D print is growing, but its winning sub-categories (miniatures, art) depend on sculpting and community (Tribes/Patreon-style memberships). Functional "Hobby & DIY" prints (+14%) better match a CAD/procedural skill set.

### Gaps
- No per-category revenue (as opposed to unit demand) was published for CGTrader or Fab.
- No public data was found on Blender geometry-nodes asset sales specifically, on CNC-file marketplace size, or on how many Creative Fabrica "CNC" listings actually sell.

---

## Q4. How AI 3D generation (Meshy, Tripo, Hunyuan3D, text-to-3D) affected prices and demand (2025–2026)

### Takeaway
AI has flooded supply but not purchases. On CGTrader, AI models are about 1 in 6 uploads but only about 1 in 90 revenue dollars, and buyers report poor quality. Indirectly, AI-driven oversupply is one reason average prices fell 9.7%, which squeezes sellers who compete on volume. Marketplaces are splitting into those that ban AI (TurboSquid, and Superhive for fully AI products) and those that require AI labels (Fab, Sketchfab, CGTrader).

### Cited Findings
- OBSERVED: On CGTrader (Jun 2025–May 2026), about 1 in 6 uploads is AI-generated but only about 1 in 90 revenue dollars, roughly 2.6% of sales. AI's share of purchases rose from about 1% to about 3.5% over the year. — [CGTrader trends](https://www.cgtrader.com/discover/3d-market-trends); [Fortune, 20 Aug 2026](https://fortune.com/2026/08/20/ai-product-fatigue-online-marketplace-ecommerce/); [404 Media, 12 Aug 2026](https://www.404media.co/ai-generated-3d-models-flood-market-but-almost-no-one-is-buying-them/)
- OBSERVED: In CGTrader's buyer survey, 5% said AI assets work well, 7% said they are usable only with heavy editing, and 20% said they are not good enough. Among print buyers, only about 4% said AI "works well" and about 72% have not used AI models at all. The survey's sample size was not disclosed. — [The Cool Down, Aug 2026](https://www.thecooldown.com/green-tech/ai-generated-3d-models-cgtrader-sales); [All3DP, Jul 2026](https://all3dp.com/6/cgtrader-market-report-shows-demand-for-3d-printable-models-outpacing-general-cg-ai-value-muted); [3DPrinting.com](https://3dprinting.com/news/3d-print-buyers-ai-cgtrader-report-2026/)
- OBSERVED: CGTrader's CEO: "With supply growing considerably faster than demand, adding more average-quality assets makes it increasingly difficult to stand out." CGTrader's advice to sellers is to use AI as a tool, not to flood the market. — [3DPrinting.com](https://3dprinting.com/news/3d-print-buyers-ai-cgtrader-report-2026/); [CGTrader trends](https://www.cgtrader.com/discover/3d-market-trends)
- OBSERVED: CGTrader signed a deal with Tencent in March 2026 around AI tooling. — [Kotaku, Aug 2026](https://kotaku.com/3d-model-markets-are-being-flooded-with-ai-sellers-but-no-ones-buying-2000724790)
- OBSERVED: Fab was hit in May 2025 by a seller uploading more than 41,000 AI models. Epic made AI labelling mandatory and added automated detection, and Sketchfab followed in December 2025. — [AI Trace](https://www.aitrace.org/company/epic-games/practice/81eb9eed-bae9-4486-9af0-9cf9e12fe341)
- OBSERVED: TurboSquid bans AI-generated content, and Superhive bans fully AI-generated products. — [TurboSquid](https://www.turbosquid.com/help/en/articles/12633683-turbosquid-s-policy-on-publishing-ai-generated-content); [Superhive](https://support.superhivemarket.com/article/311-superhive-market-ai-policy)
- OBSERVED: Commenters report that Roblox UGC channels are overflowing with AI 3D models and that most generators produce meshes needing hours of cleanup (anecdotal). — [WebProNews](https://www.webpronews.com/ai-3d-models-swamp-marketplaces-yet-buyers-stay-away)

### Inferences
- INFERRED: AI makes generic, single-object, non-PBR or non-print-tested models close to worthless as products: they are over-supplied and buyers distrust them. Value moves toward things AI does poorly today: clean topology, rigging, real-time optimization, print-tested watertight geometry, parametric or procedural tools, and accurate engineering data such as CNC-ready furniture with correct joinery and tolerances.
- INFERRED: For this studio, AI 3D tools could be used internally (for example as base meshes) only with heavy human rework, and must be disclosed on Fab and CGTrader. Superhive and TurboSquid would reject raw AI output. Running metered AI generation services would also fall under the project's own rule against spending credits without the owner's approval.

### Gaps
- No data was found on AI's effect on Fab, Superhive or 3D-print marketplace prices specifically. CGTrader is the only marketplace that has published numbers.
- The CGTrader survey's sample size is undisclosed. Price declines cannot be attributed to AI alone, since overall supply also grew 18.5%.

---

## Q5. Which segments a small Vietnam-based Blender studio can realistically win

### Takeaway
INFERRED: The best fit is **tools and procedural content where the studio's Python/Claude Code and furniture/CNC knowledge form a moat**: a niche Blender add-on or geometry-nodes product, ideally furniture or woodworking parametric tools that export cut lists and DXF. Sell it on Superhive plus Gumroad (local VND bank payout), with Fab (88%) as a second channel for procedural environment kits. Avoid generic furniture or low-poly model volume, 3dsky, and anything that depends on Etsy.

### Cited Findings (supporting evidence, already sourced above)
- The demand signal for tools and procedural systems on Fab — [Epic](https://unrealengine.com/en-US/news/fab-2025-year-in-review); the commodity squeeze in furniture — [CGTrader](https://www.cgtrader.com/discover/3d-market-trends); the falling average per Superhive creator — [Superhive](https://superhivemarket.com/posts/blender-market-2024-cyber-sale-recap); the support burden on add-on creators — [Autotroph](https://autotroph.com/the-blender-creator-economy-is-breaking-lets-start-talking-about-it); the case for an owned audience — [Blender Bros](https://www.blenderbros.com/bbd) (self-reported); Gumroad's VND bank payouts — [GetPaidAtlas](https://getpaidatlas.com/guides/gumroad-payout-countries); Creative Fabrica's 50% split — [CF T&C](https://www.creativefabrica.com/pl/designers-terms-conditions-v1-5).

### Inferences (segment-by-segment, all INFERRED)
| Segment | Fit with studio | Evidence of demand | Main risks | Verdict |
|---|---|---|---|---|
| Niche Blender add-on / GN tool (e.g., parametric furniture, cabinetry, cut-list/DXF export, procedural generators) | High (Python, Claude Code, WoodFab domain) | Add-ons dominate Superhive; Fab names engine tools and procedural systems as top categories | 12-month support expectations (Support Periods), GPL code is easy to share, sales concentrated at the top, average earnings falling | **Best bet**; sell on Superhive and Gumroad, keep the scope narrow |
| Procedural environment kits (Blender → UE/Unity, glTF/USD, PBR) for Fab | Medium-high (needs UE packaging) | Environments are #1 on Fab; real-time formats +40–48% on CGTrader | 420k+ listings on Fab; first-year sales are low | Good second channel |
| CNC/DXF furniture plans | High (WoodFab) | Real stores sell at $4–11 per file and ~$80 bundles; no market-size data | Piracy, low prices, Etsy unavailable, Design Bundles closed | Viable as a small add-on line via own store, Creative Fabrica and Cults3D (which accepts DXF/SVG) |
| Functional 3D-print files (Hobby & DIY +14%) | Medium | Print demand +7.5%, the fastest-growing segment | Supply +23.4%; printers must be bought for print testing; miniatures need sculpting skill | Optional experiment |
| VRChat avatars / assets | Medium (rigging, Unity) | $25–40 per avatar with repeat buyers | Community- and style-driven; VRChat's own store pays ~50% | Only if the owner wants a long-term community play |
| Generic archviz furniture models (3dsky / CGTrader) | Low (3dsky requires 3ds Max) | Furniture demand −6% | Commodity, flooded by AI, $7 cap, ruble accounting | **Avoid** |
| Generic low-poly packs / AI-assisted volume | Low | AI is 1/6 of uploads but 1/90 of revenue | Price collapse | **Avoid** |

- INFERRED: Rough earnings expectations, using only observed means and no invented forecasts. An average Fab publisher earned ≤ $1.2k in 2025, and an average Superhive creator earned roughly $240–375 per site-wide sale week. Reaching full-time income evidently requires being in the top tail or owning an audience, which is the pattern behind every high-earning example found.
- INFERRED: The project's existing YouTube and CineFactory channels could serve as the "owned audience" that the high earners rely on (tutorials leading to tool sales). This is not measured.

### Gaps
- Earnings for niche furniture/CNC Blender add-ons specifically are not measured; no public sales data was found for comparable products.
- Whether the earlier Etsy suspension affects KYC on Stripe- or PayPal-linked platforms is not researched or known.
- The owner should decide the target channel and whether to accept Superhive's Support Period obligations. Per the project rules, that decision belongs to the owner.
