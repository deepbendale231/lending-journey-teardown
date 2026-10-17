---
flow_source: website        # app, website or both: which surface you actually walked
evidence_boundary: public website, up to the mobile-number entry screen (nothing entered or ticked)   # one honest phrase (required before you publish)
e2e_time_seconds:           # stopwatch: tap "Personal Loan" to the last step you reached, one clean run
walked_on: 2026-10-17     # date
app_version: n/a           # the flow after the product page is a web view at my.idfcfirst.bank.in; the mobile app was not used
---

# 01. Journey map: personal loan, from "tap Personal Loan" to the last step reached

**What this is.** A step-by-step record of one live digital journey, captured from the public flow. Each row is a screen. The
step count `N` in the README is computed from the table below, never typed.

## Ground rules for capturing evidence
1. Walk the personal-loan flow as far as you can **without submitting a real application or entering real documents**.
2. If the flow gates on a real customer login or OTP, stop there and **say so** in `evidence_boundary` above. Use the public
   website, loan pages and calculators for what lies beyond, and mark those rows "website".
3. Screenshot every screen. Name files `NN_short_name.png` (for example `03_loan_amount.png`), number them in the order you saw
   them, and add each to [screenshots/INDEX.md](screenshots/INDEX.md). **Blur phone numbers, names and any account details.**
4. Time yourself end to end once and put the seconds in `e2e_time_seconds`.
5. Walk **two comparators** (any other bank or NBFC app) to the same gate, and fill the comparator table.

## Journey table
Columns: step, the screen, what the user is trying to do, what the screen asks for, effort (taps and fields), seconds spent,
screenshot number(s), notes. Delete the sample row (`EX`) once you have real rows.

<!-- JOURNEY:START -->
| # | Screen | User goal | What is asked | Effort (taps/fields) | Time (s) | Screenshot | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Product page: hero, EMI calculator, EMI table, eligibility, documents, five-step explainer, footer links (one long page) | Find out whether I can borrow and what it costs | Nothing is required. Optional calculator inputs: amount (₹1L-₹15L), tenure (9-60 months), interest rate (9.99%-38%) | 3 optional controls; 2 calls to action ("Check your eligibility", "Apply Now") | | 01; 03; 04; 05; 08; 09; 10 | Headline says 9.99% and ₹0 processing fee; the same page's EMI table lists processing fees "0% to 3.5%". Time not measured: needs a human stopwatch run |
| 2 | Promotional pop-up (appears unprompted after scrolling) | (none: interrupts the reading) | Nothing; offers "Check Offer" | 1 tap to dismiss or to proceed | | 02; 11 | Says "Approval In 5 Minutes"; the hero says "disbursed in 10 minutes". Appeared on two separate page loads |
| 3 | Application splash: "Loan up to ₹15 Lakh, starting 9.99% p.a., Foreclose anytime, ZERO FEES" | Start the application | Nothing | 1 tap (Apply Now) | | 06 | Carousel; first screen on the application domain |
| 4 | **Verify Details**: "Enter Aadhaar linked mobile number" (progress bar: Verify Details, Get Offer, Get Money) | Prove who I am to get an offer | Aadhaar-linked mobile number; one checkbox: "Agree to T&C and use of my KYC details from Cersai/UIDAI" | 1 field, 1 checkbox, 1 tap | | 07 | **Evidence stops here.** Nothing entered or ticked. Checkbox sits at the bottom of the screen, far from the field |
<!-- JOURNEY:END -->

## Pages read outside the main path (read-only, nothing entered)
These are linked from the product page footer or menu. They are **not** counted as journey steps; they are evidence for the friction log and the RBI checklist.

| Page | Screenshots | What it showed |
|---|---|---|
| Eligibility calculator (`/personal-loan-eligibility-calculator`) | 14, 18 | Public, no identity asked; loads already showing a result; criteria list differs from the product page |
| Schedule Of Charges (`/support/personal-banking-fees-and-charges`) | 12, 13 | Lands on the Accounts tab; loans are one tab-switch away |
| Retail Loans APR (`/retail-loans-apr`) | 15 | Four documents; none opened |
| Grievance Redressal (`/support/grievance-redressal`) | 16 | Collapsed by default; a list of policy and form documents |
| Digital Lending Partners (`/personal-banking/adlp/digital-lending-partners`) | 17 | Partner list by product type; nodal-officer contact details in text |

## Comparators
Same flow, same gate. Not parsed by the tools: this is for your walkthrough.

| Comparator | Surface | Steps to the same gate | Where it differs from the subject (clarity, cost shown, eligibility shown) | Screenshots |
|---|---|---|---|---|
| **HDFC Bank**, XPRESS Personal Loan (bank, website) | Website | Product page with the calculator on it, then "Apply Now", which opens a separate application site in a new tab. **The first data screen was not reached** (the pane blocks new tabs opened by automation) | States a condition next to its headline rate ("9.99%* p.a. on ₹15 lakh+") and disbursal time by customer type (page text); puts Fees & Charges, Documentation and Active Lending Partners as tabs on the product page itself. Not flawless: the product page says "up to ₹1 crore" while the application site's chooser says Personal Loan "upto 40 Lakhs" | 19, 20, 21 |
| **Bajaj Finance**, Personal Loan (NBFC, website) | Website | Product page with the calculator at the top, then "Check Loan Offer". **The first data screen was not reached** | Calculator shows interest payable and total payable with a note that additional fees and charges may apply; loan limits stated under the amount field (₹40,000 to ₹55,00,000); the promotion is a small corner toast, not a modal over the content | 22, 23 |

## Three needs of a first-time borrower
Every friction point in [02_friction_log.csv](02_friction_log.csv) is tied to one of these (`N1`, `N2`, `N3`). The statements are
the hypotheses to test against your walkthrough; change them if the evidence says so.

| ID | Need | Looks like in the journey | What you observed |
|---|---|---|---|
| N1 | **Know the total cost** before committing | Total repayment, APR and every fee visible before the bureau check and before sanction | |
| N2 | **Know my eligibility before a bureau check** | An indicative range, with a clear statement of when a credit enquiry is made | |
| N3 | **Know how long it takes** | Time to decision and time to disbursal stated up front, progress shown | |

## Where users likely drop (hypotheses, replace with what you saw)
Write two or three sentences after the walkthrough: which step asks the most for the least visible reward, where a first-time
borrower would hesitate, and what you would instrument first (see [08_metrics_tree.md](08_metrics_tree.md)).
