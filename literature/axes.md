# Annotated reading list, by axis

Generated from [register.json](register.json) by `render_axes.py`; edit the register, not this file. Access is
stated for every entry: **read** means the full text was inspected during the prior-art packet and its findings
live in `docs/day3-reading-records.json`; **not read** means an identifier was recorded but the text has not
been inspected, so nothing here claims anything about its contents. "Why it is on the list" is a reason for
reading, never a finding.

Identity is a separate question from access. An identifier that resolves still need not name the work the entry
was selected for, which is how L32 spent two days as a cell-biology thesis standing in for the Simplex paper.
Entries whose identity a person has checked against the reason for selection are marked *identity checked*;
the rest are marked *identity unverified*, which is the honest default. `identity-audit.json` records the
machine-checkable half. Corrected entries keep the record of what was wrong under `quarantined_identifier`.

## Failsafe Testing — Testing and fuzzing of autopilot failsafe and configuration behaviour

14 entries.

**L01. PGFuzz: Policy-Guided Fuzzing for Robotic Vehicles**  
NDSS, 2021 · `doi:10.14722/ndss.2021.24096` · **read** · identity checked · repository record: `U2`  
*Why it is on the list.* The policy-guided fuzzer the prior-art packet read in full; closest neighbour in intent and the source of the known failsafe logic bugs.  
*What reading it would settle.* Nothing further; read. Its policies are per-autopilot, which is where the composition question starts.

**L02. RVFuzzer: Finding Input Validation Bugs in Robotic Vehicles through Control-Guided Testing**  
USENIX Security, 2019 · `https://www.usenix.org/conference/usenixsecurity19/presentation/kim` · not read · identity unverified  
*Why it is on the list.* Named by both 2026 successors as the configuration-bug baseline; the method this project must distinguish itself from on the configuration axis.  
*What reading it would settle.* Whether control-guided input-validation testing already covers the parameter space a composition check would explore.

**L03. Control parameters considered harmful**  
Proceedings of the 44th International Conference on Software Engineering, 2022 · `doi:10.1145/3510003.3510084` · not read · identity unverified · repository record: `cited by S1 and S2`  
*Why it is on the list.* Learning-guided search for range-specification bugs in drone configuration modules; direct ancestor of the screened 2026 successors.  
*What reading it would settle.* Whether range specifications are already a first-class object, which bears on the configuration matrix.

**L04. PGPatch: Policy-Guided Logic Bug Patching for Robotic Vehicles**  
IEEE S&P, 2022 · `doi:10.1109/sp46214.2022.9833567` · **read** · identity checked · repository record: `S3`  
*Why it is on the list.* Patching of the same policy violations; read in full as S3.  
*What reading it would settle.* Nothing further; read. Its fail-safe formulas are per-autopilot restatements of documentation.

**L05. PatchVerif: Discovering Faulty Patches in Robotic Vehicles**  
USENIX Security, 2023 · `https://www.usenix.org/conference/usenixsecurity23/presentation/kim-hyungsub` · not read · identity unverified  
*Why it is on the list.* Validates whether a patch actually fixes robotic-vehicle behaviour; the closest work to this project's witness-replay step.  
*What reading it would settle.* Whether replay-to-confirm is established, and what acceptance criterion it uses.

**L06. Mayday: Identifying the Root Causes of Robotic Vehicle Accidents**  
USENIX Security, to confirm, 2020 · no identifier resolved · **identifier unresolved** · identity unverified  
*Why it is on the list.* Post-accident root-cause analysis for robotic vehicles; the inverse of this project, which predicts before the flight.  
*What reading it would settle.* Whether real accident root causes include failsafe interaction, which would turn plausible motivation into evidenced motivation.

**L07. RVPLAYER: Robotic Vehicle Forensics by Replay with What-if Reasoning**  
Proceedings 2022 Network and Distributed System Security Symposium, 2022 · `doi:10.14722/ndss.2022.24244` · not read · identity unverified  
*Why it is on the list.* Replay with reasoning over recorded robotic-vehicle runs; machinery a witness-replay pipeline could reuse.  
*What reading it would settle.* Whether an existing replay tool can host Study C instead of the harness built here.

**L08. Cyber-Physical Inconsistency Vulnerability Identification for Safety Checks in Robotic Vehicles**  
Proceedings of the 2020 ACM SIGSAC Conference on Computer and Communications Security, 2020 · `doi:10.1145/3372297.3417249` · not read · identity unverified  
*Why it is on the list.* Inconsistency between a safety check and the physical state it guards; adjacent to a monitor that fires without an action.  
*What reading it would settle.* Whether 'check present, effect absent' is already a named defect class with a detection method.

**L09. RoboFuzz: fuzzing robotic systems over robot operating system (ROS) for finding correctness bugs**  
Proceedings of the 30th ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering, 2022 · `doi:10.1145/3540250.3549164` · not read · identity unverified  
*Why it is on the list.* Correctness-bug fuzzing for ROS systems; the companion-computer side of the authority-loss story.  
*What reading it would settle.* Whether the offboard side has established correctness oracles of its own.

**L10. CPFuzz: Combining Fuzzing and Falsification of Cyber-Physical Systems**  
IEEE Access, 2020 · `doi:10.1109/access.2020.3023250` · not read · identity unverified  
*Why it is on the list.* Combines fuzzing with falsification of temporal properties; the hybrid of the two methods this project sits between.  
*What reading it would settle.* Whether falsification already subsumes what a reachability check would add.

**L11. Fuzzing of Embedded Systems: A Survey**  
ACM Computing Surveys, 2022 · `doi:10.1145/3538644` · not read · identity unverified  
*Why it is on the list.* Survey of embedded fuzzing; the map of what testing-based discovery already covers.  
*What reading it would settle.* Where the boundary of testing lies, which is the boundary this project claims to work beyond.

**L12. RouthSearch: Inferring PID Parameter Specification for Flight Control Program by Coordinate Search**  
ISSTA, 2025 · `doi:10.1145/3728904` · **read** · identity checked · repository record: `U4`  
*Why it is on the list.* PID specification inference with a per-mode temporal oracle; read in full as U4.  
*What reading it would settle.* Nothing further; read.

**L13. ADGFuzz: Assignment Dependency-Guided Fuzzing for Robotic Vehicles**  
NDSS, 2026 · `doi:10.14722/ndss.2026.231014` · **read** · identity checked · repository record: `S2`  
*Why it is on the list.* Assignment-dependency fuzzing of ArduPilot; read in full as S2.  
*What reading it would settle.* Nothing further; read.

**L14. UAVConfigFuzzer: Detecting Incorrect Configurations in UAVs via Setpoint Estimation Guided Fuzzing**  
FUZZING Workshop, 2026 · `doi:10.14722/fuzzing.2026.23009` · **read** · identity checked · repository record: `S1`  
*Why it is on the list.* Setpoint-estimation-guided configuration fuzzing of PX4; read in full as S1.  
*What reading it would settle.* Nothing further; read.

## Formal Autopilot — Formal verification and model checking of autopilot and flight-control software

9 entries.

**L15. Software model checking: extracting verification models from source code†**  
Software Testing, Verification and Reliability, 2001 · `doi:10.1002/stvr.228` · not read · identity unverified  
*Why it is on the list.* The method paper for Study A: extracting a verification model from source code, with fidelity stated as the central difficulty. Read this one first.  
*What reading it would settle.* How faithful extraction is argued for, and what evidence a reviewer expects that the extracted model is the program.

**L16. Avis: In-Situ Model Checking for Unmanned Aerial Vehicles**  
arXiv, 2021 · `arxiv:2106.14959` · **read** · identity checked · repository record: `U1`  
*Why it is on the list.* In-situ model checking of PX4 and ArduPilot; read in full as U1 and the closest method neighbour.  
*What reading it would settle.* Nothing further; read. Execution-based invariant checking against profiling runs, not offline composition.

**L17. Finding Security Vulnerabilities in Unmanned Aerial Vehicles Using Software Verification**  
arXiv, 2019 · `arxiv:1906.11488` · not read · identity unverified  
*Why it is on the list.* Software verification applied to a UAV autopilot codebase; squarely on the unsearched formal axis.  
*What reading it would settle.* Which verification technique has been applied to autopilot C at scale, and with what limits.

**L18. QP Based Framework for Development and Formal Verification of Flight Control Software of UAV**  
Lecture Notes in Computer Science, 2011 · `doi:10.1007/978-3-642-23881-9_1` · not read · identity unverified  
*Why it is on the list.* A framework for developing and verifying UAV flight-control software; the constructive counterpart to extracting a model after the fact.  
*What reading it would settle.* Whether building for verification is the accepted route, which would weaken an extract-afterwards claim.

**L19. Verifying the Mathematical Library of an UAV Autopilot with Frama-C**  
Lecture Notes in Computer Science, 2021 · `doi:10.1007/978-3-030-85248-1_10` · not read · identity unverified  
*Why it is on the list.* Deductive verification of a real autopilot's maths library; the current standard of rigour in this subfield.  
*What reading it would settle.* What a verified autopilot component looks like, and how far it sits from the failsafe logic.

**L20. Formal verification of an UAV autopilot: Static analysis and Verified Code Generation**  
thesis, 2023 · `doi:10.70675/00ae7f23z6964z4102zb62ez392357a8ed33` · not read · identity unverified · repository record: `C-record in the prior-art intake`  
*Why it is on the list.* The thesis behind that work: static analysis and verified code generation for Paparazzi.  
*What reading it would settle.* The full method and its limits; already flagged as an unread candidate in the prior-art packet.

**L21. Model Checking Based Unmanned Aerial Vehicle (UAV) Security Analysis**  
2020 International Conference on Communications, Signal Processing, and their Applications (ICCSPA), 2021 · `doi:10.1109/iccspa49915.2021.9385754` · not read · identity unverified  
*Why it is on the list.* Model checking applied to UAV security properties; shows the property vocabulary used in this domain.  
*What reading it would settle.* Whether reachability properties over UAV state machines are already standard, and in what form.

**L22. Model Checking Embedded C Software Using k-Induction and Invariants**  
2015 Brazilian Symposium on Computing Systems Engineering (SBESC), 2015 · `doi:10.1109/sbesc.2015.24` · not read · identity unverified  
*Why it is on the list.* k-induction bounded model checking of embedded C; the route if the model is checked as code rather than as automata.  
*What reading it would settle.* Whether the check could run on the C source directly, removing the extraction-fidelity problem entirely.

**L23. Applying Formal Methods to Build a Safe Continuous-Control Architecture for an Unmanned Aerial Vehicle**  
preprint, 2023 · `doi:10.21203/rs.3.rs-3668418/v1` · not read · identity unverified · repository record: `C266 in the prior-art intake`  
*Why it is on the list.* Formal methods for a safe continuous-control UAV architecture, using UPPAAL for schedulability; surfaced by the intake, still unread.  
*What reading it would settle.* Whether the timed-automata route has already been taken for a UAV architecture, and at what abstraction level.

## Timed & Hybrid — Timed automata, hybrid reachability and the tooling a composition check would use

8 entries.

**L24. A theory of timed automata**  
Theoretical Computer Science, 1994 · `doi:10.1016/0304-3975(94)90010-8` · not read · identity unverified  
*Why it is on the list.* The foundational definition of the formalism Study A proposes to use.  
*What reading it would settle.* The semantics the model must respect, and the decidability the check inherits.

**L25. UPPAAL—a Tool Suite for Automatic Verification of Real–Time Systems**  
BRICS Report Series, 1996 · `doi:10.7146/brics.v3i58.18769` · not read · identity unverified  
*Why it is on the list.* The tool the programme proposes to use, described by its authors.  
*What reading it would settle.* What the checker accepts and what a witness looks like, which the witness schema must match.

**L26. A comprehensive survey of UPPAAL‐assisted formal modeling and verification**  
Software: Practice and Experience, 2024 · `doi:10.1002/spe.3372` · not read · identity unverified  
*Why it is on the list.* A recent survey of what people model in UPPAAL and how.  
*What reading it would settle.* Whether modelling a failsafe state machine in UPPAAL is routine or novel, and the usual pitfalls.

**L27. What's Decidable about Hybrid Automata?**  
Journal of Computer and System Sciences, 1998 · `doi:10.1006/jcss.1998.1581` · not read · identity unverified  
*Why it is on the list.* States exactly where hybrid reachability stops being decidable.  
*What reading it would settle.* Whether the continuous guards can be checked at all, or must stay interval-abstracted.

**L28. An Introduction to Hybrid Automata**  
Handbook of Networked and Embedded Control Systems, 2005 · `doi:10.1007/0-8176-4404-0_21` · not read · identity unverified  
*Why it is on the list.* A readable introduction to the hybrid formalism, for the trigger-gated hybrid step in the scope.  
*What reading it would settle.* The vocabulary for the escalation path if interval abstraction turns out inconclusive.

**L29. UPPAAL-SMC: Statistical Model Checking for Priced Timed Automata**  
Electronic Proceedings in Theoretical Computer Science, 2012 · `doi:10.4204/eptcs.85.1` · not read · identity unverified  
*Why it is on the list.* Statistical model checking for priced timed automata; the fallback when exhaustive checking does not scale.  
*What reading it would settle.* Whether a statistical answer is acceptable evidence for the four properties, and at what confidence.

**L30. Modeling R^3 Needle Steering in Uppaal**  
Electronic Proceedings in Theoretical Computer Science, 2022 · `doi:10.4204/eptcs.355.4` · not read · identity unverified  
*Why it is on the list.* A worked example of taking a real physical system into UPPAAL, including its abstraction decisions.  
*What reading it would settle.* A concrete template for the extraction write-up, and what reviewers expect justified.

**L31. Combining BMC and Fuzzing Techniques for Finding Software Vulnerabilities in Concurrent Programs**  
IEEE Access, 2022 · `doi:10.1109/access.2022.3223359` · not read · identity unverified  
*Why it is on the list.* Combines bounded model checking with fuzzing; the closest published pairing of the two methods this project pairs.  
*What reading it would settle.* Whether predict-then-replay is already an established pipeline, which bears directly on distinctiveness.

## Runtime Assurance — Run-time assurance architectures: monitor, switch, recovery function

8 entries.

**L32. Using simplicity to control complexity**  
IEEE Software, 2001 · `doi:10.1109/MS.2001.936213` · not read · identity checked  
*Corrected 2026-09-24.* This entry previously read `doi:10.70675/fd34825eza23fz4a6az9dc2zeed4a5eb5536` / "Simplicity and complexity in cell cycle control" — a Universite de Rennes thesis on cell-cycle control in fission yeast (Feriel Baidi, 2016). The 2026-09-22 crossref bibliographic query for the simplex paper's title returned this record first and the title was accepted without comparing it to why_selected; found by owner review, 2026-09-24.  
*Why it is on the list.* The simplex architecture: safety controller, complex controller, switch. The pattern PX4's failsafe framework instantiates.  
*What reading it would settle.* The canonical vocabulary and the assumptions the pattern needs, which the unsafe-state definition leans on.

**L33. Dynamic control system upgrade using the Simplex architecture**  
IEEE Control Systems, 1998 · `doi:10.1109/37.710880` · not read · identity unverified  
*Why it is on the list.* The earlier simplex paper, for switching semantics in a control setting.  
*What reading it would settle.* How switching between controllers is argued safe, which is the same question as switching between failsafe actions.

**L34. Toward run-time assurance in general aviation and unmanned aircraft vehicle autopilots**  
2016 IEEE/AIAA 35th Digital Avionics Systems Conference (DASC), 2016 · `doi:10.1109/dasc.2016.7778100` · not read · identity unverified  
*Why it is on the list.* Run-time assurance applied specifically to general-aviation and UAV autopilots.  
*What reading it would settle.* Whether monitor-switch-recovery has already been formalised for an autopilot like PX4.

**L35. Run-Time Assurance: A Rising Technology**  
2020 AIAA/IEEE 39th Digital Avionics Systems Conference (DASC), 2020 · `doi:10.1109/dasc50938.2020.9256425` · not read · identity unverified  
*Why it is on the list.* A survey of run-time assurance as a technology, from the aviation side.  
*What reading it would settle.* The regulatory framing any result here would have to fit.

**L36. Initial considerations of a multi-layered run time assurance approach to enable unpiloted aircraft**  
2018 IEEE Aerospace Conference, 2018 · `doi:10.1109/aero.2018.8396622` · not read · identity unverified  
*Why it is on the list.* Multi-layered run-time assurance: several monitors and the arbitration between them. Directly the priority-consistency property.  
*What reading it would settle.* How conflicting recovery functions are arbitrated in a standards-aligned design.

**L37. Monitoring with verified guarantees**  
International Journal on Software Tools for Technology Transfer, 2023 · `doi:10.1007/s10009-023-00712-3` · not read · identity unverified  
*Why it is on the list.* Runtime monitoring with verified guarantees; the bridge from an offline proof to an online monitor.  
*What reading it would settle.* Whether a checked property can be carried into a monitor, the natural step after Study B.

**L38. Systematic review on contract-based safety assurance and guidance for future research**  
Journal of Systems Architecture, 2024 · `doi:10.1016/j.sysarc.2023.103036` · not read · identity unverified  
*Why it is on the list.* Survey of contract-based safety assurance; the form this project's recovery contracts would take.  
*What reading it would settle.* Whether 'recovery contract' already has an accepted formal meaning to adopt rather than coin.

**L39. A Safety-Driven Architectural Framework for Fail-Operational Drone Swarms**  
arXiv, 2026 · `arxiv:2608.20906` · **read** · identity checked · repository record: `U11`  
*Why it is on the list.* Fail-operational architecture with an explicit communication contract; read in full as U11.  
*What reading it would settle.* Nothing further; read.

## Contingency Ops — Lost link, contingency management and recovery operations for uncrewed aircraft

5 entries.

**L40. System-Level Safety Engineering of Unmanned Aircraft Operations: Incident-Derived Requirements for Control, Feedback, and Recovery**  
venue unrecorded, 2026 · `doi:10.21203/rs.3.rs-9739059/v1` · not read · identity unverified  
*Why it is on the list.* Incident-derived safety requirements for uncrewed operations; the operational evidence behind the question.  
*What reading it would settle.* Whether recorded incidents involve failsafe interaction.

**L41. Model-based System Health Management and Contingency Planning for Autonomous UAS**  
AIAA Scitech 2019 Forum, 2019 · `doi:10.2514/6.2019-1961` · not read · identity unverified  
*Why it is on the list.* Health management and contingency planning for autonomous UAS; the planning layer above the failsafe logic.  
*What reading it would settle.* How contingency selection is specified when several conditions hold at once.

**L42. Reconfigurable Mission Plans for RPAS**  
Aerospace Science and Technology, 2019 · `doi:10.1016/j.ast.2019.105528` · not read · identity unverified · repository record: `prior-art intake row 227`  
*Why it is on the list.* Reconfigurable mission plans for remotely piloted aircraft; surfaced by the earlier intake, still unread.  
*What reading it would settle.* Whether mission reconfiguration already covers the command-return phase this project measures.

**L43. Plan-and-Avoid: Real-Time Aircraft Trajectory Coordination in a Multi-Agent Environment**  
arXiv, 2026 · `arxiv:2608.06648` · **read** · identity checked · repository record: `U10`  
*Corrected 2026-09-24.* This entry previously read `arxiv:2608.06648` / "Plan-and-Avoid: conflict-aware contingency landing planning" — the same arXiv work; only the recorded title was wrong. The title field was filled from the reading record's summary instead of the paper's title page; found by literature/audit_identity.py, 2026-09-24 (word overlap 0.188 against the arXiv title).  
*Why it is on the list.* Contingency landing planning under multi-agent conflict; read in full as U10.  
*What reading it would settle.* Nothing further; read.

**L44. JARUS guidelines on Specific Operations Risk Assessment, edition 2.5**  
JARUS, 2024 · `JARUS SORA v2.5 Main Body (JAR_doc_25)` · **read** · identity checked · repository record: `baseline B7`  
*Why it is on the list.* The operational-risk guidance whose volume vocabulary the unsafe-state definition borrows; already a cited baseline.  
*What reading it would settle.* Nothing further for vocabulary; a full read is needed only if containment becomes a checked property.

## Feature Interaction — Feature interaction and mode confusion: individually correct mechanisms that conflict

7 entries.

**L45. A feature interaction benchmark for the first feature interaction detection contest**  
Computer Networks, 2000 · `doi:10.1016/s1389-1286(00)00007-4` · not read · identity unverified  
*Why it is on the list.* The framing this project lacked a name for: individually correct mechanisms that misbehave in combination, with a benchmark and a detection contest.  
*What reading it would settle.* Whether failsafe composition is an instance of a solved problem in another field, and which detection methods transfer.

**L46. Using model checking to help discover mode confusions and other automation surprises**  
Reliability Engineering &amp; System Safety, 2002 · `doi:10.1016/s0951-8320(01)00092-8` · not read · identity unverified  
*Why it is on the list.* Model checking used to find mode confusion and automation surprises in flight decks.  
*What reading it would settle.* The closest published use of model checking to find interaction defects in aviation automation; it sets the bar on this axis.

**L47. What’s in a Feature: A Requirements Engineering Perspective**  
Lecture Notes in Computer Science, year unrecorded · `doi:10.1007/978-3-540-78743-3_2` · not read · identity unverified  
*Why it is on the list.* A requirements-engineering account of what a feature is and how interactions arise.  
*What reading it would settle.* Whether the failsafe classes here meet the definition of features, which would let the whole literature transfer.

**L48. Formal semantic conflict detection in aspect-oriented requirements**  
Requirements Engineering, 2009 · `doi:10.1007/s00766-009-0083-y` · not read · identity unverified  
*Why it is on the list.* Formal conflict detection between crosscutting requirements.  
*What reading it would settle.* A detection method that may apply directly to the priority-consistency property.

**L49. Retrenching partial requirements into system definitions: a simple feature interaction case study**  
Requirements Engineering, 2003 · `doi:10.1007/s00766-002-0157-6` · not read · identity unverified  
*Why it is on the list.* A worked feature-interaction case study using requirement retrenchment.  
*What reading it would settle.* How partial requirements are composed without losing their individual guarantees.

**L50. Automating integration under emergent constraints for embedded systems**  
SICS Software-Intensive Cyber-Physical Systems, 2021 · `doi:10.1007/s00450-021-00428-2` · not read · identity unverified  
*Why it is on the list.* Integration of embedded components under constraints that only emerge on composition.  
*What reading it would settle.* Whether emergent-constraint analysis is a usable alternative to reachability here.

**L51. Synergistic Allocation of Flight Expertise on the Flight Deck (SAFEdeck): A Design Concept to Combat Mode Confusion, Complacency, and Skill Loss in the Flight Deck**  
Advances in Intelligent Systems and Computing, 2016 · `doi:10.1007/978-3-319-41682-3_74` · not read · identity unverified  
*Why it is on the list.* A flight-deck design intended to combat mode confusion.  
*What reading it would settle.* How the human-facing side handles the same composition problem, which bears on what counts as unsafe.

## Simulation Fidelity — Simulation fidelity, software-in-the-loop validity and the simulation-to-reality gap

2 entries.

**L52. An Empirical Analysis of the Use of Real-Time Reachability for the Safety Assurance of Autonomous Vehicles**  
venue unrecorded, 2023 · `doi:10.2139/ssrn.4346428` · not read · identity unverified  
*Why it is on the list.* Real-time reachability for safety assurance of autonomous vehicles, evaluated empirically.  
*What reading it would settle.* Whether reachability is fast enough to run online, which decides whether a Study B result could become a monitor.

**L53. Developement of SITL & HITL System based on PX4-Matlab for VTOL Test**  
Journal of KIISE, 2024 · `doi:10.5626/jok.2024.51.6.528` · not read · identity unverified  
*Corrected 2026-09-24.* This entry previously read `doi:10.5626/jok.2024.51.6.528` / "Developement of SITL &amp; HITL System based on PX4-Matlab for VTOL Test" — the same work; the title was stored with an HTML-escaped ampersand. The 2026-09-22 registry response was recorded without unescaping its entities; found by intent audit, 2026-09-25.  
*Why it is on the list.* A PX4 software- and hardware-in-the-loop test system; the closest published description of the rig built here.  
*What reading it would settle.* What fidelity claims are normally made for SITL, and the accepted evidence for them.

## Fleet Composition — Multi-vehicle composition of recovery behaviour (deferred scope, tracked)

2 entries.

**L54. Multi-Agent Safety Verification using Symmetry Transformations**  
arXiv, 2019 · `arxiv:1911.00608` · not read · identity unverified  
*Why it is on the list.* Safety verification across many agents using symmetry; the technique that would make a fleet-scale check tractable.  
*What reading it would settle.* Whether the single-vehicle model could be lifted to a fleet without state explosion.

**L55. A Distributed Simplex Architecture for Multi-Agent Systems**  
arXiv, 2020 · `arxiv:2012.10153` · not read · identity unverified  
*Why it is on the list.* A distributed simplex architecture; the fleet-scale form of monitor-switch-recovery.  
*What reading it would settle.* How switching is coordinated across vehicles, the deferred RQ4 question.
