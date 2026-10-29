# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `93dee3dfd2de` 查的快照，開工前先重查 GitHub。

## 現況

`yt_fetch` 是 CLI＋Tkinter GUI＋Windows 免安裝 EXE 的 YouTube 頻道下載工具（public、非 fork）。2026-10-29 無 open PR、Dependabot 與 Code scanning 告警皆 0，`main` 上程式碼檢查、CodeQL、依賴新鮮度檢查、Dependabot guarded merge 最近一次皆 success（2026-10-29 `gh` 查詢）。唯一的 open issue 是 #19（依賴新鮮度追蹤器）；最近 release 是 v1.9.2（2026-07-26），`CHANGELOG.md` 的 `[未發布]` 已累積 yt-dlp 基線升版、setuptools 建置下限升版與多項修正，EXE 使用者尚未拿到。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 決定是否發 v1.9.3 並重打 EXE | `[未發布]` 已含 yt-dlp 基線升版、批次全失敗結束碼改 1、設定檔 `%` 崩潰等使用者可見修正；EXE 使用者要等新 tag 才拿得到（`docs/RELEASING.md:101`） | 依 `docs/RELEASING.md` 流程：`pyproject.toml` 版號、`CHANGELOG.md` `[未發布]` 轉成 `[1.9.3]`、tag `v1.9.3` 後 release workflow success，Release 頁有 EXE 與 zip；發版前 `gh api repos/SanHsien/channeldepot/dependabot/alerts?state=open` 無筆 | 維護者 | `CHANGELOG.md:8-20`；`pyproject.toml:7`；`docs/RELEASING.md:48,101` |
| 發版時順手讓 #19 追蹤器對齊最新 yt-dlp | #19 內文寫的 PyPI 最新版可能比宣告基線新（以 `gh issue view 19 -R SanHsien/channeldepot` 的內文為準），且追蹤器只有「追蹤依賴皆最新且無 open Dependabot PR」才會關 | 重跑 `gh workflow run dependency-freshness.yml -R SanHsien/channeldepot`；若 PyPI 上有新版，先把 `pyproject.toml`／`requirements.txt` 基線升到該版並 `pytest` 綠；最後 #19 內文表格全為 OK 並自動關閉 | Claude Sonnet | issue #19；`.github/workflows/dependency-freshness.yml`；`pyproject.toml` |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 依實際下載錯誤回報擴充核心錯誤診斷分類與提示表 | 維護者或使用者回報一個目前提示不夠清楚的下載錯誤 | 該錯誤有重現測試（修前紅、修後綠）；CLI 與 GUI 顯示同一提示；`pytest` 與 black／isort／flake8 乾淨 | Claude Sonnet | `docs/HANDOFF.md`（`5e5661d` 版第 75 行） |
| GUI 改版後重產 README 截圖 | GUI 版面有改動 | 重跑 `tools/generate_readme_screenshot.py`，`README.md` 與 `README.en.md` 截圖同步更新 | 維護者（GUI 實機畫面） | `docs/HANDOFF.md`（`5e5661d` 版第 76 行）；`docs/screenshot-workflow.md` |
| 處理 `/live`、`/streams`、`?si=` 網址仍被補 `/videos` | 有人用這類網址下載失敗 | `build_channel_urls` 對這些網址的測試通過且不回歸 `/playlists`、`/c/shortsbreak` 既有案例 | Claude Sonnet | `yt_fetch.py` `build_channel_urls`；深掃報告（2026-10-26）「刻意不修」 |
| 因 YouTube 改版導致下載失敗時的緊急發版 | 下載實測失敗且 `yt-dlp` 新版已修 | 基線升至能下載的 yt-dlp 版本、實機下載成功、tag 後 EXE 重打 | 維護者 | `docs/HANDOFF.md`（`5e5661d` 版第 77 行）；`docs/third-party-youtube-tooling.md` |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 為了讓 #19 變綠而每次 yt-dlp 新版都發 EXE | 升版只改宣告，使用者要新版 EXE 才有差；發版是維護者決定 | 下載實測失敗，或維護者要發新 EXE |
| 由 agent 核准或合併 Dependabot 的人工審查項目 | branch protection 要 1 個核准，且政策分類為人工審查；agent 按核准等於替維護者過關 | 不重新考慮 |
| 修 `--ratelimit inf` 溢位 | 無實際使用情境 | 出現真實使用者回報 |

## 維護方式

依賴更新由 Dependabot 與每月 1 日的 Dependency freshness 處理，低風險項目走 guarded merge，其餘等維護者審；yt-dlp 落後時升宣告基線，是否發版 EXE 由維護者決定。每週一 CodeQL；發版步驟在 `docs/RELEASING.md`。
