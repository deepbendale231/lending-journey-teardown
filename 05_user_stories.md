# 05. User stories

Eight stories for the top fixes in [04_rice.csv](04_rice.csv), in RICE order, plus the bet to test. Every story names the friction points that justify it,
its place in the ranking, the need it serves, edge cases, an RBI note and the events to instrument ([08](08_metrics_tree.md)).
Ranks 8 (one step model) and 10 (charges link) have no story: they are backlog items with low assumed impact.

Format: "As a [user], I want [x] so that [y]", then Given / When / Then.

---

## S1. One source of truth for eligibility criteria and loan limits
**Friction:** F-08, F-11 · **RICE rank:** 1 · **Need:** N2
Evidence: the product page says loans start at ₹50,000 ([08](screenshots/08_overview_paragraph.png)) while its calculator starts at ₹1L
([01](screenshots/01_product_page_calculator.jpg)); the product page says CIBIL 710 or above ([04](screenshots/04_eligibility_documents.jpg)), the eligibility page says 710+ for
salaried and 760+ for self-employed ([18](screenshots/18_eligibility_criteria_cibil.png)).

**As a** first-time borrower, **I want** every page to give the same loan limits and eligibility criteria, **so that** I can tell whether I qualify without reconciling pages.

1. **Given** a loan limit or eligibility criterion changes in the configuration, **when** the pages reload, **then** the product page, calculator, eligibility page and splash all show the new value.
2. **Given** criteria differ by occupation, **when** I view them on any page, **then** each page shows the same per-occupation values.
3. **Given** the calculator's minimum amount, **when** it differs from the stated minimum, **then** the release is blocked by the crawl check.

**Edge cases:** a limit shown in words in one place and digits in another; a criterion that applies to one product only; cached pages after a change.
**RBI note:** eligibility criteria are part of what the lender records before lending (Directions para 7(i)); consistent public statements make the later KFS easier to reconcile.
**Events:** `terms_config_version_served {page}`, `eligibility_text_viewed {page}`.

## S2. One fee statement everywhere
**Friction:** F-01 · **RICE rank:** 2 · **Need:** N1
Evidence: the hero says "₹0 Processing Fee for Everyone" ([01](screenshots/01_product_page_calculator.jpg)); the EMI table on the same page lists processing fees "0% to 3.5%" ([03](screenshots/03_emi_table.jpg)).

**As a** first-time borrower, **I want** one clear statement of the fee, with the range and when each applies, **so that** I know what I will actually pay.

1. **Given** a fee has a range, **when** the hero or any page mentions it, **then** the range and the condition appear with it or one tap away.
2. **Given** the EMI table, **when** it lists fees, **then** its values come from the same configuration as the hero.
3. **Given** a fee applies only to some customers, **when** I view the page, **then** the page says who.

**Edge cases:** promotional zero fee with an end date; fee waived at disbursal but shown in the table; asterisk footnotes far from the claim.
**RBI note:** any one-time processing fee retained on a cooling-off exit must be disclosed upfront in the KFS (para 10(ii)); the pre-application statement should not conflict with it.
**Events:** `fee_statement_viewed {page}`, `fee_detail_opened`.

## S3. The pop-up does not cover the cost or eligibility sections
**Friction:** F-07 · **RICE rank:** 3 · **Need:** N1
Evidence: the pop-up appeared on two separate page loads while the user was reading ([02](screenshots/02_promo_popup.jpg), [11](screenshots/11_promo_popup_second_load.jpg)).

**As a** first-time borrower, **I want** to read the cost and eligibility sections without interruption, **so that** I can compare before I decide to apply.

1. **Given** I am viewing the EMI table or the eligibility section, **when** the pop-up's trigger fires, **then** it waits until I leave those sections.
2. **Given** I dismiss the pop-up, **when** I keep browsing, **then** it does not return in the same session.

**Edge cases:** keyboard and screen-reader users; the pop-up's own "Check Offer" button; slow connections. **Trade-off:** the pop-up may drive clicks, so its impact is rated low and measured.
**RBI note:** none specific; a pop-up must not obscure required disclosures.
**Events:** `popup_shown {section_in_view}`, `popup_dismissed`, `popup_cta_clicked`.

## S4. Time claims by stage
**Friction:** F-05 (and F-06) · **RICE rank:** 4 · **Need:** N3
Evidence: "disbursed in 10 minutes" ([01](screenshots/01_product_page_calculator.jpg)), "Approval In 5 Minutes" ([02](screenshots/02_promo_popup.jpg)), "Apply in 5 Mins" ([05](screenshots/05_how_to_apply.jpg)).

**As a** first-time borrower, **I want** to know how long each stage takes, **so that** I can plan and trust the claim.

1. **Given** a time claim, **when** it appears anywhere, **then** it names the stage (application, approval, disbursal) and reads from the configuration.
2. **Given** the claim depends on conditions (completed video KYC), **when** it is shown, **then** the condition is shown with it.

**Edge cases:** claims that are medians versus guarantees; peak-hour delays. **RBI note:** none specific. **Events:** `time_claim_viewed {stage, page}`.

## S5. APR and fees in the calculator output
**Friction:** F-09 · **RICE rank:** 5 · **Need:** N1
Evidence: the calculator shows EMI, total interest and total payable but no APR or fees ([01](screenshots/01_product_page_calculator.jpg)); APR is on a separate page of four documents ([15](screenshots/15_retail_loans_apr_page.png)).

**As a** first-time borrower, **I want** the calculator to show APR and fees with the EMI, **so that** I can compare the true cost across lenders.

1. **Given** I move amount, tenure or rate, **when** the calculator updates, **then** EMI, total interest, fees, total payable and APR update together.
2. **Given** I tap "How is this calculated?", **when** the explainer opens, **then** it states which charges the APR includes.

**Edge cases:** rounding; fee range versus a point fee (show the range); rates above the headline rate. **RBI note:** the APR and charges must match what the KFS later states (para 8(i); KFS circular). **Events:** `apr_shown`, `calculator_explainer_opened`.

## S6. Consent next to the field, with the purpose
**Friction:** F-04 · **RICE rank:** 6 · **Need:** (trust)
Evidence: one checkbox, "Agree to T&C and use of my KYC details from Cersai/UIDAI", at the bottom of the first data screen ([07](screenshots/07_mobile_number_gate.jpg)).

**As a** first-time borrower, **I want** consent for my KYC data separate from the terms and beside the field I am filling, **so that** I understand what I am agreeing to.

1. **Given** the mobile-number field, **when** I view it, **then** the consent sits directly under it, unticked.
2. **Given** two different consents, **when** they are shown, **then** they are two controls, each with its purpose in one line.
3. **Given** I do not tick, **when** I tap continue, **then** I am told which consent is needed and why.

**Edge cases:** small screens; screen-reader order. **RBI note:** purpose of consent disclosed at each stage and explicit consent (para 12). **Events:** `consent_viewed`, `consent_toggled {which}`.

## S7. The eligibility calculator's default state
**Friction:** F-12 · **RICE rank:** 7 · **Need:** N2
Evidence: it loads with income ₹75,000 and obligation ₹1,00,000 and already shows "eligible for a total loan amount of ₹50,000" ([14](screenshots/14_eligibility_calculator.png)).

**As a** first-time borrower, **I want** the calculator to start empty and warn me about impossible inputs, **so that** the result reflects my situation.

1. **Given** the page loads, **when** no input has been entered, **then** no result is shown.
2. **Given** obligations exceed income, **when** I enter them, **then** the page says the combination cannot be assessed instead of showing an amount.

**Edge cases:** zero income; obligations entered annually; very large values. **RBI note:** none specific; the result stays labelled indicative. **Events:** `eligibility_input_changed`, `eligibility_result_shown {amount_band}`.

## S8. The bet: indicative eligibility and rate band before the mobile-number gate
**Friction:** F-03, F-02, F-12 · **RICE rank:** 9 (tested, not just shipped) · **Need:** N2, N1
Evidence: "Check your eligibility" opens an application that asks for an Aadhaar-linked mobile number first ([01](screenshots/01_product_page_calculator.jpg), [07](screenshots/07_mobile_number_gate.jpg)); the rate is shown as 9.99% with a slider to 38% ([01](screenshots/01_product_page_calculator.jpg)).

**As a** first-time borrower, **I want** an indicative range and rate band before I give my mobile number, **so that** I can decide whether to continue without committing my identity.

1. **Given** I have entered income, employment type and the amount, **when** I tap "See my options", **then** I see an indicative amount range, tenor, EMI and APR band, labelled *indicative, subject to a credit check*.
2. **Given** the indicative screen, **when** I have not consented, **then** no bureau enquiry has been made, and the screen says when one will be made.
3. **Given** my inputs are outside the supported range, **when** I tap, **then** I am told why and what would change the answer, and nothing else is asked.

**Edge cases:** income entered annually; self-employed with variable income; income changed after seeing a range (invalidate it); declared income later contradicted by verified data.
**RBI note:** the indicative screen is not the KFS, which is still given before the contract is executed (para 8(i)); consent purpose shown (para 12(iii)).
**Events:** `eligibility_submitted`, `indicative_range_shown {min_amount, max_amount, apr_min, apr_max}`, `bureau_consent_viewed`, `bureau_consent_given`.
