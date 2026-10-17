# 06. PRD: consistent product terms before the application, then eligibility before identity

**Owner:** author · **Status:** ready for review · **Last updated:** 2026-10-17 · **Evidence:** [01](01_journey_map.md) · [02](02_friction_log.csv) · [03](03_rbi_checklist.md) · [04](04_rice.csv) · [05](05_user_stories.md) · [07](07_ab_test_plan.md)

## 1. Problem
Before a first-time borrower gives a mobile number, the public personal-loan journey states the product's terms in several places that do not
agree, and then asks for identity before giving an eligibility indication. The fee claim differs between the hero and the EMI table
(F-01), the eligibility criteria and loan limits differ between pages (F-08, F-11), the time claims differ between screens (F-05), and the
calculator shows no APR (F-09). The first data screen asks for an Aadhaar-linked mobile number (F-03) although a separate public eligibility
calculator exists, and it loads with a result already showing (F-12). A borrower cannot easily answer the three questions they came with:
*what will it cost, can I get it, how long will it take.*

## 2. Evidence
Generated from the evidence files by `make metrics`; do not edit by hand.

<!-- EVIDENCE:START -->
- **4 journey steps** and **12 friction points** with screenshot evidence (6 clarity, 3 trust, 3 effort; severity 1: 5, severity 2: 6, severity 3: 1).
- **10 fixes ranked** by RICE. Top three: 1. Single source of truth for eligibility criteria and loan limits (one config feeds product page, eligibility page, calculator, splash); 2. One fee statement everywhere: align the hero, EMI table and benefit copy, and state the fee range and when each applies; 3. Show the application pop-up only after the cost and eligibility sections are read, or not on those sections.
- RBI checklist: 4 observed, 0 not observed, 18 could not observe, of 22.
- Evidence boundary: public website, up to the mobile-number entry screen (nothing entered or ticked).
- Ranking robustness: the #1 fix stays #1 in 56% of 2,000 draws with reach and effort moved +/-30%.
<!-- EVIDENCE:END -->

Screenshots behind the points above: fee claims [01](screenshots/01_product_page_calculator.jpg) and [03](screenshots/03_emi_table.jpg); limits and criteria
[04](screenshots/04_eligibility_documents.jpg), [08](screenshots/08_overview_paragraph.png), [18](screenshots/18_eligibility_criteria_cibil.png); gate
[07](screenshots/07_mobile_number_gate.jpg); eligibility calculator [14](screenshots/14_eligibility_calculator.png).

**What this evidence cannot show:** how many users each problem costs. A walkthrough finds where friction *exists*, not where users leave.
Reach in the RICE table is an assumption until the events in [08](08_metrics_tree.md) are live, and the evidence stops at the mobile-number
gate on the public website; the mobile app was not used.

### Prioritisation: why #1 beats #2, and why the bet is ranked ninth
RICE ranks the single source of truth for eligibility criteria and loan limits first and the single fee statement second. They are close: in a
robustness check that moves reach and effort by up to 30%, #1 stays #1 in about 56% of draws and #2 in about 43%, and the pair stays in the top
three in over 99%. #1 edges ahead on **confidence** (80% against 50%): it removes a plain contradiction between pages, so the impact estimate is
less uncertain, whereas the fee statement's effect on completion depends on how much users trust cost claims. So the order is a tie broken by
confidence, not a verdict. Both share one mechanism (one product-terms configuration that every page reads), so they ship together. *These figures describe the 2026-10-17 ranking; if `04_rice.csv` changes, re-read this paragraph.*

The bet, showing an indicative eligibility range and rate band before the mobile-number gate, ranks **ninth** because its assumed effort is four
person-months against half a person-month for the copy fixes. I have not adjusted that to change the answer. The consequence is the plan below:
fix the defects first (cheap, no test needed), and spend the experiment on the one item whose effect is genuinely uncertain.

## 3. Goals and non-goals
**Goals**
1. **Phase 1:** every product term shown before the application (fee, rate band, loan limits, tenure, eligibility criteria, timings) comes from one source and agrees everywhere.
2. **Phase 2:** a user can see an indicative range and rate band before giving a mobile number, and is told when a credit check will be made.
3. Raise completion (started to submitted) by the minimum detectable effect in [07](07_ab_test_plan.md) in Phase 2, **without** raising early delinquency.
4. Keep every regulatory disclosure the current flow already carries.

**Non-goals:** changing credit policy, pricing or the underwriting model; replacing the Key Fact Statement (an indicative screen is a preview, not a KFS);
redesigning the application after the gate; the mobile app (not walked).

## 4. Users
First-time borrowers, salaried and self-employed, comparing two or three lenders on a phone, who have not borrowed digitally before. Secondary:
assisted-sales staff who read the same pages to a customer. Their needs: N1 know the total cost, N2 know eligibility before a bureau check, N3 know how long it takes ([01](01_journey_map.md)).

## 5. Requirements
**Phase 1: consistent terms** (stories S1 to S7)
| ID | Requirement | Story |
|---|---|---|
| FR1 | One product-terms configuration (fee range, rate band, loan minimum and maximum, tenure range, eligibility criteria by occupation, stage timings) read by the product page, calculator, eligibility page and application splash | S1 |
| FR2 | The fee statement gives the range and says when each fee applies; the hero, the EMI table and the benefits copy cannot contradict it | S2 |
| FR3 | The calculator output shows APR and fees as well as EMI, total interest and total payable | S5 |
| FR4 | Time claims are stated per stage (approval, disbursal) and are the same on every screen | S4 |
| FR5 | The promotional pop-up does not cover the cost or eligibility sections | S3 |
| FR6 | The eligibility calculator starts empty and validates inputs (obligations above income are flagged) | S7 |

**Phase 2: the bet** (story S8, plus consent placement S6)
| ID | Requirement | Story |
|---|---|---|
| FR7 | Show an indicative amount range, tenor, EMI and APR band before the mobile-number step, labelled indicative and subject to a credit check | S8 |
| FR8 | State on the same screen when a credit-bureau enquiry will be made; no enquiry before consent | S8 |
| FR9 | The consent checkbox sits next to the field it relates to; terms and KYC-data consent are separate; the purpose is stated | S6 |

**Non-functional:** range and cost updates under 1 s at p95; indicative calls never create a bureau enquiry; screens usable with a screen reader and at 200%
text size; events carry a session id and an anonymous user id, never a PAN or phone number.

## 6. Compliance (RBI)
Preserve, do not weaken ([03](03_rbi_checklist.md) holds the observation record and the paragraph references):
- The Key Fact Statement with the final APR before the contract is executed (Directions para 8(i)); an indicative screen must not be presented as the KFS.
- Purpose of each data request disclosed when asked, with explicit consent (para 12).
- Cooling-off exit and any retained fee disclosed upfront (para 10); grievance officer details displayed (para 11).
- A single terms source reduces the chance of two pages stating different fees or criteria; Compliance should review its wording once, not per page.

**For Compliance to confirm** (could not be observed before the gate): rows 1 to 10, 12 to 15 and 19 to 22 of the checklist. Nothing here claims they are absent.

## 7. Success metrics
Phase 1: share of product-term fields served from the configuration (target 100%); zero contradictions in a pre-release crawl of the four pages.
Phase 2: completion rate (primary), first-EMI default (early guardrail), 30 DPD at 3 months (late), approval quality, complaints per 1,000 starts, KFS-view
rate. Tree and definitions: [08](08_metrics_tree.md). Sample size and decision rule: [07](07_ab_test_plan.md).

## 8. Dependencies
| Dependency | Needed for | Risk |
|---|---|---|
| Content or config store owned by Product | FR1 to FR4 | Today copy lives in several page templates |
| Pricing and credit-policy service | FR3, FR7 | The range and APR band must never promise more than policy can deliver |
| Credit bureau API | Final offer, after consent | Must **not** be called before consent (FR8) |
| e-KYC and Account Aggregator | After the indicative step | OTP failure; extra consent steps |
| e-mandate | Repayment set-up | Bank coverage |
| Marketing pop-up tool | FR5 | Rule support |

## 9. Risks
| Risk | Mitigation |
|---|---|
| The indicative range is read as a commitment | Plain label, a range not a point, the final offer shown with its KFS |
| Completion rises but approval quality falls | Guardrails and staged rollout in [07](07_ab_test_plan.md) |
| Copy fixes lower pop-up-driven clicks | Measure Phase 1 with the metrics tree; the pop-up's impact is rated low for exactly this reason |
| Users enter inflated income to see a larger range | The range is indicative; the final offer uses verified data |
| Rankings rest on assumptions | Replace reach with measured step reach after instrumentation; re-run `make rice` |

## 10. Rollout
**Phase 1:** ship behind a flag to internal users, then 100%, monitored on the metrics tree; these fix defects and are not A/B tested.
**Phase 2:** instrumentation week, then a 5% pilot, then the test in [07](07_ab_test_plan.md); ramp 25%, 50%, 100% only if the decision rule says ship. Kill switch at every stage.

## 11. Open questions
1. What is the correct fee for each customer segment, and where does the "0% to 3.5%" range come from? 2. Is the CIBIL threshold 710 for everyone or 710 and 760 by
occupation? 3. Can an indicative APR band be published without a bureau-based score? 4. Who owns the product-terms configuration and its sign-off? 5. What
does the mobile app show at the same steps?
