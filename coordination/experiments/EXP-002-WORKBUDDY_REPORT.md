# WORKBUDDY REPORT — EXP-002

> 状态：PENDING
> 执行者：WorkBuddy / 宿主执行侧
> 审计者：ChatGPT（后续）

## A. Environment

- WorkBuddy version:
- Host/model:
- Subagent model(s):
- OS:
- Experiment time:
- Working directory:
- Baseline `~/.workbuddy/agents/` state:

## B. H1 — Member → Member Spawn

### Run 1
- parent task_id:
- parent actual Agent function_call:
- grandchild task_id:
- grandchild transcript:
- canary:
- terminal status:
- raw error:
- result:

### Run 2
同上。

### Run 3
同上。

**Conclusion:** UNKNOWN  
**Evidence level:** UNKNOWN

## C. H2 — SendMessage Delivery + ACK

对每个 run 分别记录：

| Run | sender task_id | listener task_id | route accepted | consumed in listener transcript | ACK received by lead | notes |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

**Conclusion:** UNKNOWN  
**Evidence level:** UNKNOWN

## D. H3 — TaskStop

| Run | worker task_id | stop tool result | files before | files after stop | files +5s | host terminal status | final envelope | actual stop? |
|---|---|---|---:|---:|---:|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |

**Conclusion:** UNKNOWN  
**Evidence level:** UNKNOWN

## E. H4 — Timeout

- Is timeout/deadline exposed by tested WorkBuddy interface?
- Exact tool/schema evidence:
- If tested, run evidence:
- If not exposed, state UNKNOWN explicitly.

**Conclusion:** UNKNOWN  
**Evidence level:** UNKNOWN

## F. H5 — Definition Body Hot-load Repeatability

### Fingerprint A
- agent id:
- signature source:
- dispatch prompt contains signature?:
- child output:
- transcript side-channel reads?:
- result:

### Fingerprint B
同上。

**Conclusion:** UNKNOWN  
**Evidence level:** UNKNOWN

## G. H6 — Artifact Namespace Discipline

- A namespace:
- B namespace:
- A transcript references B path?:
- B transcript references A path?:
- artifact hashes:
- lead synthesis path:
- limitations:

**Conclusion:** UNKNOWN  
**Evidence level:** UNKNOWN

## H. Contradictions / Corrections

若执行过程中出现：
- 自述与 transcript 冲突；
- running snapshot 与 terminal 结果冲突；
- 两次重复结果冲突；

必须逐条记录，不得静默覆盖。

## I. Architecture Impact

只写证据直接支持的变更：

- nested topology:
- message delivery contract:
- stop contract:
- timeout contract:
- hot-loaded Expert contract:
- artifact isolation contract:

## J. A/B Evidence Split

### A layer committed
- report:
- redacted raw logs:
- disposable agent definitions:
- runtime excerpts:

### B layer local only
- full transcripts:
- runtime snapshot:
- other fine-grained logs:

## K. Cleanup

- agents removed:
- tmp artifacts removed:
- baseline restored:
- manual recovery needed?:

## L. WorkBuddy Conclusion Table

| Hypothesis | Conclusion | Evidence Level | Key Evidence |
|---|---|---|---|
| H1 nested spawn | UNKNOWN | UNKNOWN | |
| H2 message consumed/ACK | UNKNOWN | UNKNOWN | |
| H3 TaskStop actual stop | UNKNOWN | UNKNOWN | |
| H4 timeout | UNKNOWN | UNKNOWN | |
| H5 definition hot-load repeatability | UNKNOWN | UNKNOWN | |
| H6 namespace discipline | UNKNOWN | UNKNOWN | |
